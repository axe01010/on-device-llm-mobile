# Model guide — on-device-llm-mobile

How to choose, quantise, and get good results from an on-device LLM.

## The trade-off triangle

Every choice is a blend of three constraints:

1. **RAM** — set by your device. `memory_estimator.py` tells you exactly.
2. **Quality** — parameter count and quant mainly drive this.
3. **Speed / context** — KV cache and token-gen cost rise with size and window.

You can't maximise all three. Decide which one you care about most and pick
along the two axes that remain.

## Reading a catalog entry

```json
{ "key": "qwen2.5-1.5b", "params_billions": 1.54, "quant": "Q4_K_M",
  "size_gb": 1.0, "context": 32768, "tier": "low" }
```

- `params_billions` — raw model size. See chart below.
- `quant` — how the weights are packed (`Q4_K_M` is the sweet spot).
- `size_gb` — GGUF file size on disk, ~weights in RAM.
- `tier` — recommended class: `low` (any phone), `mid`, `high` (higher-end).

### Quantisation quick reference

| Quant | bytes/weight | Use |
| ----- | ------------ | --- |
| `F16` | 2.00 | exact, huge — desktop only |
| `Q8_0` | ~1.06 | near-lossless, small models |
| `Q6_K` | ~0.81 | high quality, still biggish |
| `Q5_K_M` | ~0.68 | good quality, safe floor |
| **`Q4_K_M`** | **~0.59** | **recommended default — best quality/MB** |
| `Q3_K_M` | ~0.47 | aggressive, runnable on low RAM |
| `Q2_K` | ~0.34 | small but noticeably degraded |

Rule of thumb: start at `Q4_K_M`; only drop to Q3/Q2 if you're RAM-starved,
and only go up (Q5/Q6/Q8) if you have headroom to spare.

## Which model should I pick?

### ≤ 1 GB free RAM → `smollm-360m`, `qwen2.5-0.5b`, `tinyllama`

- Fast, tiny, fine for single-turn Q&A, naming, simple formatting.
- Good when you need *something* private and offline on the cheapest device.

### 1–3 GB → `llama-3.2-1b`, `qwen2.5-1.5b`

- The daily drivers. Good instruction-following, ~8-32 K context.
- Best balance for most phones.

### 3–5 GB → `llama-3.2-3b`, `gemma-2b`, `phi-3-mini`

- Meaningfully smarter; multi-step conversation, summarisation, some code.
- Needs a phone with ~6+ GB total RAM to feel safe (app + model + OS).

### 5+ GB → `deepseek-r1-1.5b`, `mistral-7b`

- Reasoning traces (R1 Distill) or desktop-class width (Mistral-7B).
- High-end only; expect slower per token on CPU.

## Estimating memory yourself

`memory_estimator.py` prints a `estimated` line that already taxes overhead:

```bash
python3 memory_estimator.py --params 3.8 --quant Q4_K_M --context 4096
# weights: 2.07 GB (Q4_K_M)
# kv/ctx:  2 MB for 4096 tokens
# estimated: 2.24 GB resident RAM (incl. 8% overhead)
```

The formula (roughly): **RAM ≈ params×bpw × 1.08**, plus ~512 B/token of
context. Keep ~512 MB headroom for the OS and other apps.

## Tips for better on-device results

- Keep the prompt length sane — context is *expensive* (KV cache) and small
  models forget fast.
- Instructions beat open-ended questions. "List three bullet points" is sharper
  than "tell me about X".
- Restart generation: many tiny models 'ramp' their answer — nudge with
  follow-up turns.
- For structured output (JSON), few-shot the format in the user turn.
- Prefer `Q4_K_M` for most; only chase `Q8_0` on a 0.5B toy.

## Adding your own model

1. Add a `catalog.json` entry (see the guide in `models/README.md`).
2. Put the `.gguf` under `models/` (gitignored).
3. It now appears in `--list` and `--budget-mb` automatically — no code changes.