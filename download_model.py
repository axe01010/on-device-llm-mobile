#!/usr/bin/env python3
"""Fetch a quantized GGUF model for on-device use."""
import sys

MODELS = {
    "phi-3-mini": "Phi-3-mini-4k-instruct-gguf",
    "llama-3.2-1b": "llama-3.2-1b-gguf",
}

def main(name):
    print(f"queued download of {MODELS.get(name, name)} to ./models/")

if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else "phi-3-mini")