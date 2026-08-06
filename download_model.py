#!/usr/bin/env python3
"""Download a quantized GGUF model from the public HuggingFace hub.

Looks a model up in ``models/catalog.py`` / ``models/catalog.json`` to get its
download URL and recommended quantization, then streams it to ``models/`` with
progress. Also lets you point at your own source file or skip a full download
with ``--dry-run`` to verify URLs.

Usage
    python download_model.py                       # default: llama-3.2-1b
    python download_model.py phi-3-mini
    python download_model.py --model qwen2.5 --dry-run    # resolve only, no download
"""

from __future__ import annotations

import argparse
import json
import shutil
import sys
import urllib.request
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parent
OUT_DIR = ROOT / "models"
CATALOG_JSON = ROOT / "models" / "catalog.json"

# Fall back to catalog.py for model metadata if the JSON is missing.
DEFAULT_URLS = {
    "phi-3-mini": "https://huggingface.co/microsoft/Phi-3-mini-4k-instruct-gguf/resolve/main/Phi-3-mini-4k-instruct-q4.gguf",
    "llama-3.2-1b": "https://huggingface.co/bartowski/Llama-3.2-1B-Instruct-GGUF/resolve/main/Llama-3.2-1B-Instruct-Q4_K_M.gguf",
}
DEFAULT_MODEL = {"key": "llama-3.2-1b"}


def load_catalog() -> list[dict[str, Any]]:
    """Load the merged catalog as a flat list dict keyed by ``key``."""
    entries: list[dict[str, Any]] = []
    if CATALOG_JSON.exists():
        try:
            data = json.loads(CATALOG_JSON.read_text(encoding="utf-8"))
            entries = data.get("models", [])
        except (json.JSONDecodeError, OSError):
            entries = []
    # Also fold in python catalog if present, for models not in JSON.
    try:
        from models.catalog import MODEL_CATALOG
        for key, meta in MODEL_CATALOG.items():
            if key not in {e.get("key") for e in entries}:
                entries.append({"key": key, "name": meta.get("name", key),
                                "download_url": meta.get("download_url", ""),
                                "quant": meta.get("quant", "Q4_K_M")})
    except Exception:
        pass
    return entries


def entry(name: str) -> dict[str, Any]:
    """Return catalog metadata for ``name`` (or a best-effort fallback)."""
    for e in load_catalog():
        if e.get("key") == name or e.get("name", "").lower() == name.lower():
            return {"key": name, **e}
    url = DEFAULT_URLS.get(name)
    if not url:
        return {}
    return {"key": name, "name": name, "download_url": url, "quant": ""}


def url_for(model: str) -> str:
    meta = entry(model)
    return meta.get("download_url") or DEFAULT_URLS.get(model, "")


def download(model: str, out_dir: str | Path | None = None, force: bool = False,
             dry_run: bool = False) -> int:
    """Download ``model``; returns a process exit code (0 ok, 1 err, 2 missing)."""
    out_dir = Path(out_dir) if out_dir else OUT_DIR
    out_dir.mkdir(parents=True, exist_ok=True)
    meta = entry(model)
    url = meta.get("download_url")
    quant = meta.get("quant", "Q4_K_M")

    if not url:
        print(f"no known download URL for '{model}'")
        print("known models: " + ", ".join(sorted(e["key"] for e in load_json())))
        return 2

    dest = out_dir / f"{model}.gguf"
    if dest.exists() and not force:
        print(f"already there: {dest} (use --force to re-download)")
        return 0

    print(f"downloading {meta.get('name', model)} ({quant}) -> {dest}")
    if dry_run:
        print(f"[dry-run] would download: {url}")
        return 0

    try:
        req = urllib.request.Request(url, headers={"User-Agent": "on-device-llm-mobile"})
        with urllib.request.urlopen(req) as resp, open(dest, "wb") as fh:
            total = int(resp.headers.get("Content-Length") or 0)
            copied = 0
            while True:
                chunk = resp.read(1 << 20)
                if not chunk:
                    break
                fh.write(chunk)
                copied += len(chunk)
                if total:
                    print(f"\r{copied / total * 100:5.1f}%", end="", flush=True)
        print(f"\ndone: {dest} ({copied / (1024 ** 3):.2f} GB)")
        return 0
    except (urllib.error.URLError, OSError) as exc:
        print(f"download failed: {exc}")
        return 1


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(prog="download_model", description="Fetch a GGUF model.")
    ap.add_argument("model", nargs="?", default="phi-3-mini", help="catalog key (default phi-3-mini)")
    ap.add_argument("-m", "--model", dest="model_alias", help="catalog key (alias)")
    ap.add_argument("--out", default=str(OUT_DIR), help="output directory")
    ap.add_argument("--force", action="store_true", help="re-download if present")
    ap.add_argument("--dry-run", action="store_true", help="validate URL, don't download")
    ap.add_argument("--list", action="store_true", help="list available models")
    args = ap.parse_args(argv)
    model = args.model_alias or args.model
    if args.list:
        for e in load_catalog():
            print(f"  {e['key']:<18} {e.get('name','')}")
        return 0
    return download(model, out_dir=args.out, force=args.force, dry_run=args.dry_run)


if __name__ == "__main__":
    raise SystemExit(main())