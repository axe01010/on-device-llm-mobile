# Model Catalog & Choosing a Model

A practical guide to the catalog schema, how to read RAM estimates, and how to
pick the right model for a given Android device.

## The catalog

Two artifacts describe every supported model:

* **`models/catalog.json`** — the canonical machine-readable catalog used by
  the CLI tools (downloader, estimator, benchmark).
* **`models/catalog.py`** — a Python mirror with extra convenience (aliases,
  `resolve()`).

Both expose the same fields per model:

| field          | example                    | meaning                                  |
|----------------|----------------------------|------------------------------------------|
| `key`          | `llama-3.2-1b`             | stable id used in `--model`              |
| `name`         | `Llama 3.2 1B`             | display name                              |
| `family`       | `llama`                    | architecture family                       |
| `params_billions` | `1.24`                  | parameter count in billions               |
| `quant`        | `Q4_K_M`                   | recommended GGUF quantization             |
| `context`      | `4096`                     | recommended context window (tokens)       |
| `download_url` | `https://…`                | public model card on HuggingFace          |
| `note`         | `…`                        | human guidance / caveats                  |

## Adding a model

1. Pick a trustworthy GGUF on HuggingFace.
2. Record its params (`model_card` or paper), recommended quant, and a sensible
   context window.
3. Add the entry to **both** `models/catalog.json` and `models/catalog.py`.
4. Size-check it: `python memory_estimator.py --params N --quant Q4_K_M`.
5. Add a one-line table row to `README.md`.

## How RAM estimates work

The estimator (`memory_estimator.py`) models the dominant cost — loading the
weights — plus a conservative runtime overhead:

```
weights_gb = params_billions × bytes_per_weight(quant) / (1024³)

kv_cache    = (bytes/token) × context_tokens / (1024³)   # ~512 B/token typical

resident_gb = (weights_gb + kv) × 1.08
```

The `1.08` factor covers KV cache, activation buffers, GPU/CPU compute scopes
and a small app sandbox margin. It is deliberately conservative so you won't be
surprised by an OOM-kill after context.

### Choosing a `context`

Context is the knob you pay for twice — in KV-cache memory and in slower
prefill. Practically:

| Context | Use for  | RAM impact |
|---------|----------|-----------|
| 2048    | Q&A, summarise | low |
| 4096    | chat, docs (default) | medium |
| 8192    | long conversations, RAG | high (KV doubles) |

Double the context roughly doubles the KV cache — often the difference between
"fits" and "killed".

## Rules of thumb by phone

| Free RAM (after apps) | Models that fit comfortably |
|-----------------------|------------------------------|
| ~1 GB  | TinyLlama 1.1B, Llama 3.2 1B        |
| ~2 GB  | + Qwen 2.5 1.5B, Gemma 2 2B          |
| ~3–4 GB| + Phi-3 Mini                         |
| ~6 GB+ | Llama 3.1 8B (flagship)              |

Run `python memory_estimator.py --device` on your own phone for exact numbers
(it reads `/proc/meminfo`).

---

## Why GGUF + llama.cpp?

**GGUF** is the standard, self-contained file format for 8-bit/4-bit quantized
transformers. **llama.cpp** is the reference multi-backend engine (CPU/NEON,
Vulkan, Metal, CUDA) that runs GGUF on phones, laptops and desktops with no
cloud dependency. The whole project is built around keeping that pairing simple:
catalog → download → estimate → run.