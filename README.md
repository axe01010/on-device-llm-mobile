# 📱 On-Device LLM Mobile

<p align="center">
  <img src="https://img.shields.io/badge/On--Device-LLM-green?style=for-the-badge&logo=ai&logoColor=white" />
  <img src="https://img.shields.io/badge/Android-3DDC84?style=for-the-badge&logo=android&logoColor=white" />
</p>

> **Run LLMs directly on your Android phone.** No cloud, no internet — private AI in your pocket.

## ✨ Features

- 🧠 Run quantized LLMs (Llama, Phi, Gemma) on Android
- ⚡ GPU acceleration via Vulkan/OpenCL
- 📱 Optimized for ARM64 Snapdragon
- 💾 Smart memory management
- 🔒 Fully private (no data leaves device)
- 🔌 Integration with AI agents

## 🚀 Quick Start

```bash
git clone https://github.com/axe01010/on-device-llm-mobile.git
cd on-device-llm-mobile

# Download a model
python download_model.py phi-3-mini

# Run inference
python chat.py --model phi-3-mini
```

## 📊 Supported Models

| Model | Size | RAM Needed |
|-------|------|------------|
| Phi-3 Mini | 3.8B | 4GB |
| Llama 3.2 1B | 1B | 2GB |
| Gemma 2B | 2B | 3GB |
| TinyLlama | 1.1B | 2GB |

## 📁 Structure

```
on-device-llm-mobile/
├── chat.py               # Interactive chat
├── download_model.py     # Model downloader
├── models/               # Model configs
├── inference/            # Inference engine
├── benchmarks/
├── CONTRIBUTING.md
├── LICENSE
└── README.md
```

## 🤝 Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md).

## 📜 License

MIT
