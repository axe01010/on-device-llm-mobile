# models/

Drop quantized `.gguf` model files here (e.g. via `download_model.py`).

## Catalog

`catalog.json` is the machine-readable index of recommended GGUF models —
params, quantization, context window, download URL and tier. A few ways to use
it:

```bash
# list the whole catalog
python3 download_model.py --list

# download a model's GGUF with progress/resume
python3 download_model.py llama-3.2-1b

# see only what fits a RAM budget
python3 memory_estimator.py --budget-mb 3500
```

## Layout

```
models/
├── catalog.json      # model index (source of truth for name/url/quant/RAM)
└── *.gguf            # downloaded weights (gitignored; don't commit ~0.5-4GB files)
```

## Adding a model

Add an entry to `catalog.json` with: `key`, `name`, `family`,
`params_billions`, `quant`, `size_gb`, `context`, `url`, `hf_repo`, `tier`.
Keep `params_billions` and `size_gb` accurate — they feed `memory_estimator.py`.