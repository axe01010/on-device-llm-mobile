#!/usr/bin/env python3
"""On-device LLM chat runner (local inference stub)."""
import argparse

MODELS = {
    "phi-3-mini": 3.8,
    "llama-3.2-1b": 1.0,
    "gemma-2b": 2.0,
    "tinylama": 1.1,
}

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--model", default="phi-3-mini", choices=list(MODELS))
    a = ap.parse_args()
    print(f"🐧 model={a.model} ({MODELS[a.model]}B params, local-only)")
    print("type 'exit' to quit")
    while True:
        try:
            q = input("> ")
        except EOFError:
            break
        if q.strip().lower() == "exit":
            break
        print(f"[{a.model}] (local inference stub) got: {q}")

if __name__ == "__main__":
    main()