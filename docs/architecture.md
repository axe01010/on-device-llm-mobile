# Architecture — on-device-llm-mobile

This document explains how the four tools fit together and why they're split
the way they are.

## The data model: `models/catalog.json`

Everything hangs off one file: the model catalog. It is a JSON array of
entries like:

```json
{
  "key": "llama-3.2-1b",
  "name": "Llama 3.2 1B Instruct",
  "family": "llama",
  "params_billions": 1.24,
  "quant": "Q4_K_M",
  "size_gb": 0.8,
  "context": 8192,
  "url": "https://huggingface.co/.../…gguf",
  "hf_repo": "bartowski/Llama-3.2-1B-Instruct-GGUF",
  "tier": "low"
}
```

Four tools read/write this single source of truth, so there's never a
"models differ between pages" drift problem:

```
        ┌────────────── models/catalog.json ──────────────┐
        │                (single source of truth)          │
        └──┬──────────────┬────────────────┬───────────────┘
           │imports           │imports          │imports
           ▼                  ▼                 ▼
      chat.py           download_model.py  memory_estimator.py
   (REPL/one-shot)       (fetch GGUF)         (size models)
           │                   │                    │
           └────────────── swap ◀─ llama.cpp runner ─┘
                          (real inference)
```

## find individual tools

### `download_model.py` — getting the weights

- `resolve(name)` maps a catalog key → entry. If the key isn't in the catalog,
  it falls back to the legacy inline `MODELS` table and synthesises an entry.
- `download(url, dest, sha256)` uses `requests` streaming with a byte-range
  `Range` header for **resume**, renders a progress bar, and verifies a SHA-256
  digest when provided (on fresh downloads; resumed files skip verification
  because only the appended bytes are hashed).
- `--dry-run` prints the exact plan (URL, dest, size) without touching the
  network — the safety default.

### `memory_estimator.py` — sizing the model

The estimator models **resident RAM**:

```
weights_bytes = params × bytes_per_weight(quant)      # on-disk size
ram           ≈ (weights + KV_cache) × 1.08           # runtime overhead
```

- `BYTES_PER_WEIGHT` holds bytes/parameter for `F16 … Q2_K`.
- `KV_BYTES_PER_TOKEN` (512 B/tok) covers the KV cache for `--context` tokens.
- `estimate_ram_gb()` is the pure function; `pick_for_budget()`/`score_device()`
  re-use it to recommend models for a RAM budget or this device.

### `chat.py` — the interface

- Loads the catalog (`catalog.json`) merged over the inline `MODELS` table.
- `--model`/`-m` selects; `/memory` delegates to `memory_estimator`; REPL
  commands `/model`, `/history`, `/clear`, `/help`.
- `-q "…"` one-shot path is intentionally *pure* (importable) so scripts can
  call `infer_stub()` / `param_count()` directly.
- The inference engine is a deterministic **stub** by default; a real llama.cpp
  runner is "wire in later" without changing the CLI.

### `benchmark.py` — measuring the real thing

- Dedicated `@dataclass BenchResult` output (model, runner, prompt_tokens,
  output_tokens, wall_ms, tokens_per_sec, mean_token_ms, peak_ram_mb).
- `run_real_runner()` execs a llama.cpp CLI; `_simulate_generation()` provides a
  deterministic 2-second fake for CI/tests (`--simulate`).
- Accepts a single `.gguf` OR a whole directory; `--budget-mb` fails the run
  (exit 1) if peak RAM exceeds the budget.

## Design principles

1. **One catalog, many readers.** No hard-coded model lists scattered across
   tools — add a model in `catalog.json` once and all four tools see it.
2. **Pure functions at the core.** `estimate_ram_gb`, `weights_gb`,
   `param_count`, `resolve` have no I/O, so they're trivially unit-testable.
3. **Dry-run safe.** Downloads and benchmarks both support a no-op mode so CI
   and docs never need the network or a 4GB file.
4. **Backward compatible.** The original `MODELS` dict in `chat.py` and
   `download_model.py` is preserved as a fallback so old callers keep working.

## For maintainers

- A new model = one new `catalog.json` entry. Keep `params_billions`/`size_tt
  accurate — they drive RAM advice.
- Keep `benchmark.py` deterministic in `--simulate` (no wall-clock assertions
  in tests).
- Never commit `.gguf`/`.bin` files (gitignored).