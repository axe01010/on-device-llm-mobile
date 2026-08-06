#!/usr/bin/env python3
"""Example: script a one-shot chat + RAM check against the catalog.

Demonstrates importing chat.py as a module (instead of the CLI) to run a
non-interactive prompt and to ask for a RAM footprint.

Run:
    python examples/scripted_chat.py
"""
from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from chat import infer_stub, load_catalog, param_count, estimate_ram  # noqa: E402


def main() -> int:
    catalog = load_catalog()
    print(f"catalog has {len(catalog)} models\n")

    model = "qwen2.5-1.5b"
    if model not in catalog:
        model = "phi-3-mini"

    print(f"=== Scripted chat with {model} ({param_count(model):.2f}B) ===")
    print("Q:", "summarize the runtime Cost of self-hosting an LLM?")
    print("A:", infer_stub(model, "summarize the Cost of self-hosting an LLM?"))

    print("\n=== RAM estimate ===")
    estimate_ram(model)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())