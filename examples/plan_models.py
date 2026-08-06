#!/usr/bin/env python3
"""Example: catalog + memory-estimate + benchmark, end to end.

Shows the toolchain's three most useful functions working together:
  1. look a model up in the catalog,
  2. estimate how much RAM it needs on a phone,
  3. run a (synthetic) benchmark and print comparable numbers.

Run::

    python examples/plan_models.py
"""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from models.catalog import list_models, resolve  # noqa: E402
from memory_estimator import estimate_ram_gb, device_free_ram_mb  # noqa: E402
from benchmark import synthetic_benchmark  # noqa: E402


def main() -> None:
    models = list_models()
    free_mb = device_free_ram_mb()
    print(f"Device free RAM: {free_mb:.0f} MB" if free_mb else "Device free RAM: n/a")
    print(f"{'MODEL':<16}{'B':>6}{'RAM(MB)':>10}{'fits?':>8}")
    print("-" * 46)
    for key in models:
        meta = _meta(key)
        params = float(meta.get("params_b", 1.0))
        quant = str(meta.get("quant", "Q4_K_M"))
        ram_mb = estimate_ram_gb(params, quant, meta.get("context", 4096)) * 1024
        fits = "yes" if (free_mb and ram_mb <= free_mb) else "no"
        print(f"{key:<16}{params:<9.2f}{ram_mb:>8.0f}  {fits:>6}")

    print("\nSynthetic benchmark (no model, no llama.cpp):")
    bench = synthetic_benchmark(32, 64)
    print(f"  prompt {bench['prompt_tps']:.1f} t/s · gen {bench['gen_tps']:.1f} t/s "
          f"({bench['note']})")


def _meta(key: str) -> dict:
    from models.catalog import MODEL_CATALOG
    return dict(MODEL_CATALOG.get(key, {"params_b": 1.0, "quant": "Q4_K_M", "context": 4096}))


if __name__ == "__main__":
    main()