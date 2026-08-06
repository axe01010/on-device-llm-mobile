#!/usr/bin/env python3
"""Curated catalog of GGUF models for on-device mobile inference.

The catalog is the single source of truth about which models the toolchain
knows how to download, estimate and run. Each entry carries the metadata the
rest of the project needs (RAM/RAM estimate, quantization, source, family) so
the CLI and examples stay data-driven rather than hard-coding model names.

Fields:
    id          stable machine key (used by chat.py --model, download_model.py)
    name        publishable display name
    family      architecture family (llama / phi / gemma / qwen / ...)
    params_b    parameter count in billions
    quant       recommended GGUF quantization (Q4_K_M is a good mobile default)
    size_gb     approximate file size at that quant
    ram_gb      approximate peak RAM needed to run comfortably
    source      model card URL on huggingface.co
    note        human note about suitability / caveats
"""

from __future__ import annotations

MODEL_CATALOG: dict[str, dict[str, str | float | int]] = {
    "llama-3.2-1b": {
        "name": "Llama 3.2 1B",
        "family": "llama",
        "params_b": 1.24,
        "quant": "Q4_K_M",
        "size_mb": 780,
        "ram_mb": 1040,
        "context": 4096, "download_url": "https://huggingface.co/bartowski/Llama-3.2-1B-Instruct-GGUF",
        "source": "hf",
        "note": "Fastest useful chat model for phones; great default for CPU.",
    },
    "tinyllama-1.1b": {
        "name": "TinyLlama 1.1B",
        "family": "llama",
        "params_b": 1.1,
        "quant": "Q4_K_M",
        "size_mb": 660,
        "ram_mb": 900,
        "context": 2048, "download_url": "https://huggingface.co/TheBloke/TinyLlama-1.1B-Chat-v1.0-GGUF",
        "source": "hf",
        "note": "Very light; good for low-RAM devices or background tasks.",
    },
    "phi-3-mini": {
        "name": "Phi-3 Mini 3.8B",
        "family": "phi",
        "params_b": 3.8,
        "quant": "Q4_K_M",
        "size_mb": 2300,
        "ram_mb": 3900,
        "context": 4096, "download_url": "https://huggingface.co/microsoft/Phi-3-mini-4k-instruct-gguf",
        "source": "hf",
        "note": "Strong instruction-following-to-power ratio; a solid default for mid phones.",
    },
    "gemma-2-2b": {
        "name": "Gemma 2 2B",
        "family": "gemma",
        "params_b": 2.6,
        "quant": "Q4_K_M",
        "size_mb": 1500,
        "ram_mb": 2200,
        "context": 4096, "download_url": "https://huggingface.co/bartowski/gemma-2-2b-it-GGUF",
        "source": "hf",
        "note": "Good multilingual support and reasoning for its size.",
    },
    "qwen2.5-1.5b": {
        "name": "Qwen 2.5 1.5B",
        "family": "qwen",
        "params_b": 1.5,
        "quant": "Q4_K_M",
        "size_mb": 980,
        "ram_mb": 1350,
        "context": 4096, "download_url": "https://huggingface.co/Qwen/Qwen2.5-1.5B-Instruct-GGUF",
        "source": "hf",
        "note": "Excellent for code + multilingual tasks on mobile.",
    },
    "llama-3.1-8b": {
        "name": "Llama 3.1 8B",
        "family": "llama",
        "params_b": 8.03,
        "quant": "Q4_K_M",
        "size_mb": 4900,
        "ram_mb": 8100,
        "context": 8192, "download_url": "https://huggingface.co/bartowski/Meta-Llama-3.1-8B-Instruct-GGUF",
        "source": "hf",
        "note": "Largest realistic option; needs a recent flagship with lots of RAM.",
    },
}

#: Backwards-compatible alias map used by the original chat.py / download_model.py.
MODELS: dict[str, str] = {
    "phi-3-mini": "phi-3-mini",
    "llama-3.2-1b": "llama-3.2-1b",
    "gemma-2b": "gemma-2-2b",
    "tinylama": "tinyllama-1.1b",
}

# Safe-friendly display name -> (metadata key).
ALIASES: dict[str, str] = {
    "llama-3.2-1b": "llama-3.2-1b",
    "llama-3.2-1b.q4": "llama-3.2-1b",
    "tinyllama": "tinyllama-1.1b",
    "tiny": "tinyllama-1.1b",
    "phi-3-mini": "phi-3-mini",
    "phi": "phi-3-mini",
    "gemma-2b": "gemma-2-2b",
    "gemma": "gemma-2-2b",
    "qwen2.5": "qwen2.5-1.5b",
    "qwen": "qwen2.5-1.5b",
    "llama-3.1-8b": "llama-3.1-8b",
    "llama-8b": "llama-3.1-8b",
}


def resolve(model: str) -> dict[str, object]:
    """Return the catalog entry for ``model`` (accepting an alias or catalog key)."""
    key = ALIASES.get(model, model)
    if key not in MODEL_CATALOG:
        raise KeyError(f"unknown model: '{model}'. Known: {', '.join(sorted(MODEL_CATALOG))}")
    return dict(MODEL_CATALOG[key])


def list_models() -> list[str]:
    """Return catalog keys sorted by size (smallest first)."""
    return sorted(MODEL_CATALOG, key=lambda k: MODEL_CATALOG[k]["params_b"])


def catalog_json(sort="size") -> str:
    """Return a pretty JSON dump of the catalog, optionally sorted."""
    models = dict(MODEL_CATALOG)
    if sort == "size":
        models = dict(sorted(models.items(), key=lambda kv: kv[1]["params_b"]))
    elif sort == "name":
        models = dict(sorted(models.items(), key=lambda kv: kv[1]["name"]))
    import json
    return json.dumps(models, indent=2)


if __name__ == "__main__":
    print(catalog_json())