# Getting started — on-device-llm-mobile

Set up and run a model locally on your phone (Termux) or any Linux/desktop.

## 1. Install

```bash
git clone https://github.com/axe01010/on-device-llm-mobile.git
cd on-device-llm-mobile
pip install -r requirements.txt      # requests (for downloads)

# optional: real inference engine (Termux)
pkg install llama-cpp                # provides llama-cli / llama-server
```

## 2. Choose a model

Two questions matter:

1. **How much RAM can you spare?** — see `memory_estimator.py`.
2. **How smart/deep is the task?** — see the tier table.

```bash
# list models that fit a budget
python3 memory_estimator.py --budget-mb 3500

# or score against THIS device's free RAM (reads /proc/meminfo)
python3 memory_estimator.py --device
```

Quick default: **1–3 GB free RAM** → `llama-3.2-1b` or `qwen2.5-1.5b`;
**3–5 GB** → `llama-3.2-3b` / `gemma-2b`; **5+ GB** → `mistral-7b`
(multi-turn).

## 3. Download the weights

```bash
# preview first, then the real thing
python3 download_model.py llama-3.2-1b --dry-run
python3 download_model.py llama-3.2-1b

# verify integrity with a known digest
python3 download_model.py llama-3.2-1b --sha256 <64-hex>
```

Downloads stream to `models/` with a progress bar, resume a partial file, and
(skip) verify SHA-256 on fresh downloads.

## 4. Chat

```bash
# stub backend (no model needed) — explore the CLI
python3 chat.py

# one-shot for scripting
python3 chat.py -m llama-3.2-1b -q "caputal of Benin?"

# check the footprint first
python3 chat.py -m phi-3-mini --estimate-ram
```

REPL commands:

```
> /model llama-3.2-3b        # swap models
> /memory                    # RAM estimate for the current model
> /history                   # last 10 turns
> /clear                     # clear history
> exit                        # leave
```

### Wiring a real engine

The REPL is identical either way. Install llama.cpp and run chat through it:

```bash
# option A: interactive
python3 chat.py -m llama-3.2-1b        # (real inference via llama_cli when installed)

# option B: benchmark first
python3 benchmark.py --model models/ --runner llama-cli
```

> What the stub does vs a real runner: the stub echoes a framed answer using
> the catalog in `models/catalog.json` metadata. A real runner tokenizes the
> prompt, generates and streams; the tooling around it (catalog, sizing,
> benchmark) is the same.

## 5. Benchmark

```bash
python3 benchmark.py --simulate                 # deterministic smoke test
python3 benchmark.py --model models/ --runner llama-cli   # real throughput
```

The `--json` flag emits a machine-readable report (`tokens_per_sec`,
`lower_tok_ms`, `wall_ms`, `peak_ram_mb`).

## Troubleshooting

| Symptom | Fix |
| ------- | --- |
| `no .gguf found` | point `--model` at a dir containing `.gguf`, or a file path |
| `runner not found` | `pkg install llama-cpp`; else use `--simulate` |
| model "unknown" | `python3 download_model.py --list`; keys must match `catalog.json` |
| oom during infer | pick a smaller model / smaller `--context`, or free RAM (kill background apps) |
| size "0.00 GB" | that's the per-token KV figure; trust the `estimated` line |

## Next steps

- Which model? → `docs/model-guide.md`
- How everything fits → `docs/architecture.md`