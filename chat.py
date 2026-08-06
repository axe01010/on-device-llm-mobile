#!/usr/bin/env python3
"""On-device LLM chat runner (offline, local llama).

A small chat powered entirely by a local model. Two paths:

* **Real inference** — if you have ``llama-cli`` (llama.cpp) and a downloaded
  ``.gguf`` model file, this bridges to it (see ``--model``).
* **Mock / review mode** — with no backend it behaves deterministically,
  maintains conversation history, and reports how much RAM the chosen model
  needs, so you can exercise the whole UX before a real model is installed.

Usage
    python chat.py                                  # interactive, default model
    python chat.py --model qwen2.5                   # pick a model by catalog key
    python chat.py --list-models                     # what the catalog knows
    python chat.py --one-shot "hello"                # scripted, no loop
"""

from __future__ import annotations

import argparse
import shutil
import subprocess
import sys
from pathlib import Path
from types import SimpleNamespace
from typing import Any

from models.catalog import resolve
from memory_estimator import estimate_ram_gb  # noqa: F401

DEFAULT_MODEL = "llama-3.2-1b"

#: Shared cache so we don't recompute RAM estimates repeatedly in a session.
_MODEL_RAM: dict[str, dict[str, Any]] = {}


def _model_ram_hint(model: str) -> dict[str, Any]:
    """Return a compact RAM-hint dict for a catalog model key.

    Uses the estimator's ``estimate_ram_gb(params, quant, context)`` and
    degrades gracefully (1 GiB) when the model isn't in the catalog.
    """
    if model in _MODEL_RAM:
        return _MODEL_RAM[model]
    try:
        meta = resolve(model)
        params = float(meta.get("params_b", meta.get("params_billions", 1.0)))
        quant = str(meta.get("quant", "Q4_K_M"))
        context = int(meta.get("context", 4096))
        gb = estimate_ram_gb(params, quant, context)
    except Exception:
        gb = 1.0
    hint = {"ram_mb": round(gb * 1024), "gb": round(gb, 1)}
    _MODEL_RAM[model] = hint
    return hint


def _p(text: str) -> str:
    return (text or "").strip()


def _resolve_model_file(model: str) -> str | None:
    """Find a .gguf file for ``model`` in ./models or ./models/<model>/."""
    root = Path(__file__).resolve().parent
    candidates = [
        root / "models" / f"{model}.gguf",
        root / "models" / "gguf" / f"{model}.gguf",
        root / "models" / f"{model}" / f"{model}.gguf",
    ]
    for c in candidates:
        if c.exists():
            return str(c)
    return None


def _backend() -> str | None:
    for name in ("llama-cli", "llama"):
        path = shutil.which(name)
        if path:
            return path
    return None


def _mock_reply(model: str, user_text: str, history: list[dict[str, Any]]) -> dict[str, Any]:
    """Deterministic mock reply when no real model backend is present."""
    n = len([m for m in history if m.get("role") == "user"])
    text = _p(user_text)
    snippet = text[:80] if text else "(empty)"
    return {
        "role": "assistant",
        "content": f"[local] (turn {n}) received: {snippet}",
        "model": model,
        "mock": True,
    }


def subtle_infer(model: str, model_file: str, user_text: str,
                 history: list[dict[str, Any]]) -> dict[str, Any]:
    """Run llama.cpp locally (subprocess). Returns the assistant reply dict."""
    backend = _backend()
    if not backend:
        return {"role": "assistant", "content": "[llama] binary not found — install llama-cli.",
                "model": model, "mock": True}
    ctx = "\n".join(f"{m.get('role', 'user')}: {m.get('content', '')}" for m in history[-6:])
    context = f"{ctx}\nuser: {_p(user_text)}\nassistant:"
    cmd = [backend, "-m", model_file, "-p", context, "-n", "120",
           "--no-display-prompt", "--simple-io"]
    try:
        out = subprocess.run(cmd, capture_output=True, text=True, timeout=180)
        reply = out.stdout.strip() or out.stderr.strip() or "(empty reply)"
    except (subprocess.TimeoutExpired, OSError) as exc:
        reply = f"[llama error] {exc}"
    return {"role": "assistant", "content": reply, "model": model}


def local_chat(model: str, user_text: str, history: list[dict[str, Any]]) -> dict[str, Any]:
    """Handle one user turn; returns the assistant dict."""
    history = history or []
    model_file = _resolve_model_file(model)
    if model_file:
        return local_chat_realfile(model, model_file, user_text, history)
    hint = _model_ram_hint(model)
    return {
        "role": "assistant",
        "content": f"[local review] you said: {_p(user_text)[:90] or '(empty)'} — "
                   f"needs ~{hint['ram_mb']} MiB RAM. Install a .gguf + llama-cli "
                   "(python download_model.py) for real inference.",
        "model": model,
    }


def local_chat_realfile(model: str, model_file: str, user_text: str,
                        history: list[dict[str, Any]]) -> dict[str, Any]:
    """Run a real llama.cpp inference against an existing model file."""
    return subtle_infer(model, model_file, user_text, history)


def prompt_block(model: str, history: list[dict[str, Any]]) -> str:
    """Render a simple system+message block (used for mock & subprocess)."""
    lines = ["<<SYS>>You are a helpful local assistant.<</SYS>>"]
    for m in history:
        lines.append(f"<{m.get('role')}>\n{m.get('content')}")
    return "\n".join(lines)


def run_repl(model: str) -> int:
    meta = _lookup(model)
    history: list[dict[str, Any]] = []
    print(f"🐧 {meta.get('name', model)} — local & offline ('exit' to quit, 'reset' to clear)")
    while True:
        try:
            q = input("you> ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\nbye.")
            return 0
        if not q:
            continue
        if q.lower() in ("exit", "quit"):
            return 0
        if q.lower() == "reset":
            history.clear()
            print("history cleared.")
            continue
        history.append({"role": "user", "content": q})
        reply = local_chat(model, q, history)
        history.append(reply)
        print(f"\n  bot: {reply['content']}\n")


def run_one_shot(model: str, msgs: list[str]) -> int:
    history: list[dict[str, Any]] = []
    for m in msgs:
        history.append({"role": "user", "content": m})
        print(f"user> {m}")
        try:
            reply = local_chat(model, m, history)
        except Exception as exc:
            print(f"  error: {exc}")
            continue
        history.append(reply)
        print(f"bot> {reply['content']}\n")
    return 0


def _lookup(model: str) -> dict[str, Any]:
    try:
        meta = resolve(model)
        return {"name": meta["name"], "quant": meta.get("quant", "Q4_K_M"),
                "params": meta.get("params_b")}
    except KeyError:
        return {"name": model, "quant": "Q4_K_M"}


# Keep-name portable callers.
local_chat = local_chat  # defined above
local_reply = local_chat


def main_cli(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(prog="chat", description="On-device LLM chat (offline).")
    ap.add_argument("--model", default=DEFAULT_MODEL, help="catalog key or custom name")
    ap.add_argument("--list-models", action="store_true", help="list catalog models")
    ap.add_argument("--one-shot", nargs="*", default=None, help="scripted messages, then exit")
    ap.add_argument("-q", "--prompt", default=None,
                    help="one-shot single prompt (shorthand for --one-shot)")
    args = ap.parse_args(argv)

    if args.prompt:
        return run_one_shot(args.model, [args.prompt])
    if args.list_models:
        from models.catalog import list_models as _lm
        for key in _lm():
            m = _lookup(key)
            print(f"  {key:<16} {m.get('name','')}")
        return 0
    if args.one_shot is not None:
        return run_one_shot(args.model, args.one_shot)
    return run_repl(args.model)


if __name__ == "__main__":
    raise SystemExit(main_cli())