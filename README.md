<p align="center">
  <img src="https://github.com/axe01010/on-device-llm-mobile/raw/main/assets/banner.png" alt="on-device-llm-mobile" width="100%" />
</p>

<p align="center">
  <img src="https://img.shields.io/github/stars/axe01010/on-device-llm-mobile?style=for-the-badge&color=10B981&logo=github" />
  <img src="https://img.shields.io/github/forks/axe01010/on-device-llm-mobile?style=for-the-badge&color=3DDC84&logo=github" />
  <img src="https://img.shields.io/github/license/axe01010/on-device-llm-mobile?style=for-the-badge&color=10B981" />
  <img src="https://img.shields.io/github/last-commit/axe01010/on-device-llm-mobile?style=for-the-badge&color=3DDC84" />
</p>

# 📱 On-Device LLM Mobile

<p align="center">
  <img src="https://img.shields.io/badge/On--Device-LLM-10B981?style=for-the-badge&logo=ai&logoColor=white" />
  <img src="https://img.shields.io/badge/Android-3DDC84?style=for-the-badge&logo=android&logoColor=white" />
  <img src="https://img.shields.io/badge/Python-3.8%2B-blue?style=for-the-badge&logo=python&logoColor=white" />
  <img src="https://img.shields.io/badge/License-MIT-green?style=for-the-badge" />
</p>

> **Run LLMs directly on your Android phone.** No cloud, no internet, no data
> leaving the device — private AI in your pocket, built on quantized GGUF
> models and local llama.cpp inference.

A practical toolchain for choosing, sizing, downloading, benchmarking and
chatting with on-device models — everything needed to ship a real, offline
assistant.

---

## ✨ Features

- 🧠 **Curated model catalog** — six verified GGUF models (Llama, Phi, Gemma,
  Qwen, TinyLlama) in one source of truth (`models/catalog.json`).
- 💾 **RAM estimator** — predict the resident footprint of any model/quant/context
  combination before you risk an out-of-memory kill.
- 📊 **Benchmark helper** — measure prompt & generation **tokens/second**
  (bridges to llama.cpp when present; deterministic synthetic baseline otherwise).
- 🧬 **Offline chat** — a REPL that runs fully local, in mock mode or against
  a real `.gguf` + `llama-cli`.
- 📦 **Model downloader** — stream a model straight from HuggingFace with progress.
- 🔒 **100% offline** — once a model is downloaded, nothing leaves the phone.

---

## 🚀 Quick Start

```bash
git clone https://github.com/axe01010/on-device-llm-mobile.git
cd on-device-llm-mobile

# 1. Pick a model that fits your device's RAM
python memory_estimator.py --device

# 2. Download it (takes a while on the first run)
python download_model.py llama-3.2-1b

# 3. Chat, fully offline
python chat.py --model llama-3.2-1b
```

For real inference also install llama.cpp on your phone:

```bash
# Termux example
pkg install llama-cpp   # or build llama.cpp yourself
```

---

## 📊 Supported models

| Model | Family | Params | Quant  | Size | RAM (est.) | Notes |
|-------|--------|-------:|--------|-----:|-----------:|-------|
| TinyLlama 1.1B | llama | 1.1B | Q4_K_M | ~660 MB | ~0.9 GB | Best for low-end |
| Llama 3.2 1B | llama | 1.2B | Q4_K_M | ~780 MB | ~1.0 GB | Great default |
| Qwen 2.5 1.5B | qwen | 1.5B | Q4_K_M | ~980 MB | ~1.4 GB | Multilingual focus |
| Gemma 2 2B | gemma | 2.6B | Q4_K_M | ~1.5 GB | ~2.2 GB | Strong reasoning |
| Phi-3 Mini | phi | 3.8B | Q4_K_M | ~2.3 GB | ~3.9 GB | Mid-range phones |
| Llama 3.1 8B | llama | 8.0B | Q4_K_M | ~4.9 GB | ~8.1 GB | Flagship only |

Numbers are approximate and depend on your quant/context. Get precise figures for
*your* phone with `python memory_estimator.py --device`.

---

## 🧰 Tooling

### Estimate RAM

```bash
python memory_estimator.py --params 3.8 --quant Q4_K_M      # a single model
python memory_estimator.py --budget-mb 3500                 # what fits 3.5 GB?
python memory_estimator.py --device                          # score this phone
```

### Benchmark

```bash
python benchmark.py -m models/llama-3.2-1b.gguf --ctx 4096  # real numbers
python benchmark.py --synthetic --json                        # no model, JSON
```

### Chat offline

```bash
python chat.py --model qwen2.5                  # interactive REPL
python chat.py --one-shot "hello" "summarize"   # scripted turns
python chat.py --list-models                     # catalog
```

---

## 🧠 How it works

```
                 ┌──────────────────────────────┐
  pick model ──▶ │  models/catalog.json         │  params, quant, context, URL
                 └──────────────┬───────────────┘
                                │
              ┌─────────────────┼─────────────────┐
              ▼                 ▼                 ▼
   memory_estimator.py  download_model.py   chat.py / benchmark.py
   RAM to run it        fetch the .gguf      run & measure locally
```

All three tools share the same catalog, so the model you size is the model you
download is the model you chat with.

---

## ❓ FAQ

**Does this need a cloud API?** No. Inference is local via llama.cpp (GGUF).

**Which phone can run what?** Roughly: ≤1B models on any device with ~1 GB free
RAM; 2–4B needs a mid-range phone; 8B+ needs a recent flagship.

**What is "mock / review mode"?** When no model file is present, `chat.py`
still runs the full conversation flow with deterministic replies, so you can
build and test your UI before downloading a model.

---

## 🤝 Contributing

See [`CONTRIBUTING.md`](CONTRIBUTING.md). Keep the catalog schema, match the
style, and size-check new models with `memory_estimator.py` before adding them.

## 📜 License

MIT — use it, fork it, learn from it.

---
<p align="center">
  <b>Part of the <a href="https://github.com/axe01010/axe01010">Free On-Device AI DevKit</a> stack</b><br>
</p>
<p align="center">
  <a href="https://github.com/axe01010/android-ai-agent">android-ai-agent</a> ·
  <a href="https://github.com/axe01010/on-device-llm-mobile">on-device-llm-mobile</a> ·
  <a href="https://github.com/axe01010/mcp-server-hub">mcp-server-hub</a> ·
  <a href="https://github.com/axe01010/termux-toolkit">termux-toolkit</a> ·
  <a href="https://github.com/axe01010/android-security-lab">android-security-lab</a>
</p>
<p align="center"><sub>README built for the <b>Free On-Device AI DevKit</b> — private AI that runs entirely on a phone.</sub></p>
