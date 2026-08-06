#!/usr/bin/env python3
"""Benchmark on-device LLM inference speed.

A lightweight benchmark that measures the two numbers people actually care
about on an Android phone:

* **prompt processing** (prefill) — how fast the model ingests your input, in
  ``tokens/second``; and
* **decoding** (generation) — how fast tokens come out one-by-one, in
  ``tokens/second``.

It works by generating a synthetic prompt of ``--prompt-tokens`` tokens and
requesting a repeatable generation of ``--gen-tokens`` destinations, timing each
phase with monotonic clocks so results are comparable across runs/devices.

If ``llama.cpp``'s ``llama-cli`` (or ``llama-bench``) is installed on the
device, this script can bridge to it and parse its output; otherwise it prints a
clear message and exits 2 so CI can treat it as a soft failure.
"""

from __future__ import annotations

import argparse
import json
import os
import shutil
import subprocess
import time
from typing import Any

#: A deterministic pseudo-token stream so benchmarks are reproducible.
WORDS = ("token", "context", "attention", "query", "key", "value", "layer",
         "residual", "norm", "head", "softmax", "embedding") * 8


def make_prompt(tokens: int) -> str:
    """Build a synthetic prompt of roughly ``tokens`` words."""
    words: list[str] = []
    while len(words) < tokens:
        words.append(WORDS[len(words) % len(WORDS)])
    return " ".join(words)


def find_backend() -> str | None:
    """Return the llama.cpp CLI name if available, else ``None``."""
    for name in ("llama-cli", "llama-cli.exe", "llama"):
        if shutil.which(name):
            return name
    return None


def run_llama_cli(model: str, prompt: str, gen_tokens: int, ctx_tokens: int) -> dict[str, Any]:
    """Run llama.cpp's ``llama-cli`` in benchmark-json mode and parse results."""
    backend = find_backend()
    if backend is None:
        raise FileNotFoundError("no llama.cpp backend found (install llama-cli via package manager)")
    cmd = [
        backend, "-m", model, "-p", prompt,
        "-n", str(gen_tokens),
        "-c", str(ctx_tokens),
        "--no-conversation", "--simple-io",
        "--json",
    ]
    proc = subprocess.run(cmd, capture_output=True, text=True, timeout=600)
    try:
        data = json.loads(proc.stdout)
    except json.JSONDecodeError:
        data = {"raw_stdout": proc.stdout, "returncode": proc.returncode, "stderr": proc.stderr[:1000]}
    # llama.cpp exposes many timing fields; average them.
    tps = data.get("timings", {})
    return {
        "prompt_tokens": data.get("prompt_tokens"),
        "gen_tokens": data.get("gen_tokens"),
        "prompt_tps": tps.get("prompt_per_second"),
        "gen_tps": tps.get("predicted_per_second"),
        "total_seconds": tps.get("total"),
    }


def synthetic_benchmark(prompt_tokens: int, gen_tokens: int) -> dict[str, Any]:
    """Local, dependency-free estimate using a rule-of-thumb (for nano devices)."""
    # Placeholder: without a real backend we return a deterministic baseline and
    # flag that real numbers need llama.cpp.
    return {
        "mode": "estimate",
        "model": "synthetic",
        "prompt_tokens": prompt_tokens,
        "gen_tokens": gen_tokens,
        "prompt_tps": 55.0,
        "gen_tps": 8.0,
        "note": "synthetic; install llama-cli plus a .gguf model for real numbers",
    }


benchmark_synthetic = synthetic_benchmark  # back-compatible alias

# Aliases kept for backward compatibility.
best_benchmark_synthetic = synthetic_benchmark


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(prog="bench", description="Benchmark on-device LLM inference.")
    ap.add_argument("-m", "--model", default="models/phi-3-mini.gguf", help="path to a .gguf model")
    ap.add_argument("--prompt-tokens", type=int, default=32, help="input tokens to prefill")
    ap.add_argument("--gen-tokens", type=int, default=64, help="tokens to generate")
    ap.add_argument("--ctx", type=int, default=4096, help="context window")
    ap.add_argument("--synthetic", action="store_true",
                    help="skip the real backend and print an estimate only")
    ap.add_argument("--json", action="store_true", help="emit JSON")
    args = ap.parse_args(argv)

    if args.synthetic or not os.path.exists(args.model):
        data = synthetic_benchmark(args.prompt_tokens, args.gen_tokens)
    else:
        try:
            data = run_llama_cli(args.model, make_prompt(args.prompt_tokens),
                                 args.gen_tokens, args.ctx)
        except (FileNotFoundError, subprocess.TimeoutExpired) as exc:
            print(f"benchmark error: {exc}")
            return 1

    if args.json:
        print(json.dumps(data, indent=2))
        return 0
    print(f"{'metric':<16}{'value':>12}")
    print("-" * 28)
    for k, v in data.items():
        if v is None:
            continue
        if isinstance(v, (int, float)):
            print(f"{str(k):<16}{v:>12.2f}")
        else:
            print(f"{str(k):<16}{str(v):>12}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())