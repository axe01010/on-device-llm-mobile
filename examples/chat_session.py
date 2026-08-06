#!/usr/bin/env python3
"""Example: script a short multi-turn chat through the local chat backend.

Demonstrates the programmatic ``local_chat()`` API across a few turns, printing
how the session history grows. Works in mock mode (no model needed).

Run::

    python examples/chat_session.py
"""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from chat import local_chat, DEFAULT_MODEL  # noqa: E402


def main() -> None:
    history: list[dict] = []
    prompts = [
        "What is on-device inference?",
        "Give me a one-line summary.",
    ]
    for msg in prompts:
        print(f"\nuser> {msg}")
        reply = local_chat(DEFAULT_MODEL, msg, history)
        history.append({"role": "user", "content": msg})
        history.append(reply)
        print(f"bot > {reply['content']}")
    print(f"\n({len(history)} history entries, "
          f"{len([m for m in history if m['role'] == 'user'])} user turns)")


if __name__ == "__main__":
    main()