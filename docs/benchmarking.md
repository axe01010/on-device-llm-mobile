# Benchmarking On-Device Inference

A guide to benchmarking LLM inference on a phone and interpreting the two
numbers that matter: **prompt processing** and **generation** throughput.

## Why measure both?

When you ask a phone model a question, inference has two phases with very
different speed:

| phase | what happens | typical bottleneck |
|-------|--------------|-------------------|
| **prefill / prompt** | context & question are ingested, tokens parallel | memory bandwidth |
| **decode / generation** | answer tokens emitted one-by-one | serial latency |

For a chat assistant, **generation tokens/s** is what feels like "how fast it
types". **Prompt tokens/s** matters for RAG where you dump a lot of text into
context before asking.

## What `benchmark.py` reports

For each phase it gives a **tokens/second** figure. Higher is better.

```text
metric                    value
----------------------------------
mode                            estimate
model                         synthetic
prompt_tokens                          32
gen_tokens                            64
prompt_tps                       55.00
gen_tps                          8.00
note           synthetic; install llama-cli plus a .gguf model for real numbers
```

When a real `llama-cli` backend and a model file exist, it runs an actual
zero-shot generation and parses llama.cpp's `--json` timings.

## How to get a real number

```bash
# install llama.cpp (Termux)
pkg install llama-cpp

# download a model you sized for the phone
python download_model.py llama-3.2-1b

# run the benchmark
python benchmark.py -m models/llama-3.2-1b.gguf --gen-tokens 32

# emit JSON for scripting / CI
python benchmark.py -m models/llama-3.2-1b.gguf --json
```

Tip: keep `--gen-tokens` low (16–64) on a phone so it finishes in seconds; use
`--ctx` to simulate answering long prompts.

## Interpreting numbers

| gen t/s | feel |
|---------|------|
| 30+ | snappy — feels real-time |
| 10–30 | fine for Q&A |
| 2–10 | usable but laggy for long answers |
| <2 | too slow for chat (reconsider quant/context) |

Compare across: model, quant, context, and the device's RAM. Log the numbers in
`benchmark --json` output so you can track a given model across OS updates.

## Benchmark pitfalls

- **Thermal throttling** — run on a charged phone, not mid-charge, and do a
  warm-up before the timed run.
- **Background apps** — close other apps; the OS may evict the model to RAM.
- **Different context** isn't comparable — report the context used.
- **llama.cpp default threads** — on multi-core phones you may get better
  numbers with `--threads N`.

## Programmatic use

```python
from benchmark import synthetic_benchmark, run_llama_cli

rep = synthetic_benchmark(32, 64)        # deterministic estimate
path = run_llama_cli("models/llama-3.2-1b.gguf", "hello", 64, 4096)
print(path["gen_tps"])
```

See `examples/plan_models.py` for catalog + RAM + estimate + benchmark in one
script.