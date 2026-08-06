# Installation & Usage

Set up on-device LLM inference on Android (Termux) or a desktop, and a reference
for every CLI.

## Requirements

- **Python 3.8+** (3.10+ recommended).
- A working `pip` (Termux: `pkg install python`).
- Optional: **llama.cpp** for real inference
  (`pkg install llama-cpp` in Termux) and ~1–4 GB of free storage for models.

## Installation

```bash
git clone https://github.com/axe01010/on-device-llm-mobile.git
cd on-device-llm-mobile
python3 -m venv .venv && source .venv/bin/activate   # optional
pip install -r requirements.txt
```

No runtime dependencies are required for the estimator or the mock chat; the
`requirements.txt` is intentionally light (it enables the JSON catalog loader
conveniences and hand-harvested deps).

## End-to-end: your first offline chat

```bash
# 0. See which models fit the phone
python memory_estimator.py --device

# 1. Download a model you like
python download_model.py llama-3.2-1b

# 2. (Optional) benchmark real speed once installed
python benchmark.py -m models/llama-3.2-1b.gguf

# 3. Chat offline
python chat.py --model llama-3.2-1b

# 4. Scripted, non-interactive
python chat.py --model phi-3-mini --one-shot "write a haiku about phones"
```

## Command reference

### Memory estimator (`memory_estimator.py`)

```bash
python memory_estimator.py --params 3.8 --quant Q4_K_M
python memory_estimator.py --params 8.03 --context 8192 --json
python memory_estimator.py --budget-mb 3500
python memory_estimator.py --device
```

| flag | meaning |
|------|---------|
| `--params` | model size in billions |
| `--quant` | quantization tag (default `Q4_K_M`) |
| `--context` | context tokens (default 4096) |
| `--budget-mb` | list catalog models that fit this RAM budget |
| `--device` | score the catalog against this phone |
| `--json` | machine-readable output |

### Model download (`download_model.py`)

```bash
python download_model.py                 # default model
python download_model.py phi-3-mini
python download_model.py llama-3.2-1b --dry-run
python download_model.py --list
python download_model.py llama-3.2-1b --force
```

| flag | meaning |
|------|---------|
| `<key>` / `-m` | which model (catalog key) |
| `--out` | output dir (default `models/`) |
| `--force` | re-download even if present |
| `--dry-run` | resolve the URL, don't download |
| `--list` | list available models |

### Benchmark (`benchmark.py`)

```bash
python benchmark.py -m models/model.gguf --gen-tokens 32 --json
python benchmark.py --synthetic
```

Reports **prompt t/s** (prefill) and **gen t/s** (decoding), the two numbers
that matter for a phone assistant.

### Chat (`chat.py`)

```bash
python chat.py                       # interactive
python chat.py --model qwen2.5
python chat.py --one-shot "hi" "what is termux?"
python chat.py --list-models
```

| flag | meaning |
|------|---------|
| `--model` | catalog key (default `llama-3.2-1b`) |
| `--one-shot` | feed messages, print replies, exit |
| `--list-models` | list the catalog |
| `--off` (app-provided) | |mock clipboard; by default mock mode is automatic |

### Examples

```bash
python examples/plan_models.py    # catalog + RAM + benchmark combined
python examples/chat_session.py   # scripted multi-turn chat
```

## How to get llama.cpp on Android

```bash
pkg update && pkg install -y llama-cpp
# or build from source to enable GPU backends (Vulkan etc.)
```

Once `llama-cli` is on `PATH`, `chat.py --model <key>` and `benchmark.py` will
use it automatically when it finds a `.gguf` in `models/`.

## Troubleshooting

- **`ImportError: cannot import name 'X' from 'memory_estimator'`** — run
  `python memory_estimator.py` (it is self-executing); if it works, your Python
  is picking up an older cached `.pyc`. Delete `__pycache__/`.
- **Download is slow** — expected on first run; a 4-billion model is ~2 GB.
- **llama-cli missing** but model present — install `llama-cpp` or put a
  `llama` binary on `PATH`.
- **OOM mid-generation** — lower the model, lower `--context`, or pick a more
  aggressive quant.
- **`/proc/meminfo` unreadable** — pass `--budget-mb N` instead of `--device`.