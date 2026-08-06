#!/usr/bin/env python3
"""Estimate the RAM footprint of a quantized on-device LLM.

The dominant cost of running a transformer on-device is loading the weights:

    weights_bytes  ≈  params × bytes_per_weight(quant)

Runtime overhead (KV cache, activations, graphs, app sandbox) is modelled as a
small multiplier. The estimator is deliberately conservative — it predicts the
*resident* footprint, i.e. what the OS actually keeps in RAM while the model is
loaded (shared pages count once, mmap'd weights count once).

Example:
    python memory_estimator.py --params 3.8 --quant Q4_K_M
    python memory_estimator.py --budget-mb 3500      # which catalog fits?
    python memory_estimator.py --device              # score against this device
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parent
CATALOG_PATH = ROOT / "models" / "catalog.json"

#: Bytes per weight for common llama.cpp quant formats (approx., incl. headers).
BYTES_PER_WEIGHT: dict[str, float] = {
    "F16": 2.0, "F32": 4.0, "Q8_0": 1.0625, "Q6_K": 0.8125,
    "Q5_K_M": 0.679, "Q5_0": 0.6875, "Q4_K_M": 0.585, "Q4_0": 0.5625,
    "Q3_K_M": 0.473, "Q2_K": 0.344,
}
#: Overhead for KV cache, activations, GPU/NEON buffers, app sandbox.
RUNTIME_OVERHEAD = 1.08
#: KV-cache cost per token of context (bytes/token, typical small GQA model).
KV_BYTES_PER_TOKEN = 512.0


def weights_gb(params_billions: float, quant: str) -> float:
    """Pure weight-file size in GB for ``params_billions`` and ``quant``."""
    if quant not in BYTES_PER_WEIGHT:
        raise ValueError(
            f"unknown quant '{quant}'; known: {', '.join(sorted(BYTES_PER_WEIGHT))}"
        )
    return params_billions * 1e9 * BYTES_PER_WEIGHT[quant] / (1024 ** 3)


def estimate_ram_gb(params_billions: float, quant: str, context_tokens: int = 4096) -> float:
    """Predict steady-state resident RAM in GB while the model is loaded."""
    weights = weights_gb(params_billions, quant)
    kv = KV_BYTES_PER_TOKEN * context_tokens / (1024 ** 3)
    return (weights + kv) * RUNTIME_OVERHEAD


def _catalog() -> list[dict[str, Any]]:
    if not CATALOG_PATH.exists():
        return []
    try:
        return json.loads(CATALOG_PATH.read_text(encoding="utf-8"))["models"]
    except (json.JSONDecodeError, KeyError, OSError):
        return []


def pick_for_budget(catalog: list[dict[str, Any]], budget_mb: float) -> list[dict[str, Any]]:
    """Return catalog entries whose estimated RAM fits ``budget_mb``."""
    fits: list[dict[str, Any]] = []
    for entry in catalog:
        try:
            ram_mb = estimate_ram_gb(entry["params_billions"], entry["quant"],
                                     entry.get("context", 4096)) * 1024
        except (ValueError, KeyError):
            continue
        if ram_mb <= budget_mb:
            fits.append({**entry, "estimated_ram_mb": round(ram_mb)})
    return sorted(fits, key=lambda e: e["estimated_ram_mb"])


def score_device(ram_mb: float) -> list[dict[str, Any]]:
    """Rank catalog models that fit in ``ram_mb`` by size ascending."""
    return pick_for_budget(_catalog(), ram_mb)


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(
        prog="memory_estimator", description="Estimate how much RAM an on-device LLM needs.")
    ap.add_argument("--params", type=float, default=None, help="model size in billions of params")
    ap.add_argument("--quant", default="Q4_K_M", help="quantization format (default Q4_K_M)")
    ap.add_argument("--context", type=int, default=4096, help="context window in tokens")
    ap.add_argument("--budget-mb", type=float, default=None,
                    help="filter the catalog to models fitting this RAM budget (MB)")
    ap.add_argument("--device", action="store_true",
                    help="score the catalog against this device's free RAM (/proc/meminfo)")
    ap.add_argument("--json", action="store_true", help="emit JSON")
    args = ap.parse_args(argv)

    if args.device:
        free = device_free_ram_mb()
        if free is None:
            print("cannot read /proc/meminfo — pass --budget-mb instead")
            return 1
        print(f"device free RAM: {free:.0f} MB")
        fits = score_device(free)
        for e in fits:
            print(f"  {e['key']:<18} ~{e['estimated_ram_mb']:>5} MB  "
                  f"({e['params_billions']}B @ {e['quant']})")
        print(f"\n{len(fits)} of {len(_catalog())} catalog entries fit.")
        return 0

    if args.budget_mb is not None:
        fits = pick_for_budget(_catalog(), args.budget_mb)
        if args.json:
            print(json.dumps(fits, indent=2))
            return 0
        print(f"Models estimated to fit within {args.budget_mb:.0f} MB of RAM:\n")
        for e in fits:
            print(f"  {e['key']:<18} ~{e['estimated_ram_mb']:>5} MB  "
                  f"({e['params_billions']}B @ {e['quant']})")
        print(f"\n{len(fits)} of {len(_catalog())} catalog entries fit.")
        return 0

    if args.params is None:
        ap.error("provide --params (or use --budget-mb / --device with the catalog)")
    ram = estimate_ram_gb(args.params, args.quant, args.context)
    if args.json:
        print(json.dumps({"params_billions": args.params, "quant": args.quant,
                          "context_tokens": args.context,
                          "weights_gb": round(weights_gb(args.params, args.quant), 2),
                          "estimated_ram_gb": round(ram, 2)}))
        return 0
    print(f"weights:    {weights_gb(args.params, args.quant):.2f} GB ({args.quant})")
    print(f"kv/ctx:     {512.0 / 1e6 * args.context:.0f} MB for {args.context} tokens")
    print(f"estimated:  {ram:.2f} GB resident RAM (incl. {int((RUNTIME_OVERHEAD - 1) * 100)}% overhead)")
    return 0


def device_free_ram_mb() -> float | None:
    """Free/available RAM in MB from /proc/meminfo (Linux/Android)."""
    try:
        for line in Path("/proc/meminfo").read_text().splitlines():
            if line.startswith("MemAvailable:"):
                return float(line.split()[1]) / 1024.0
    except (OSError, ValueError, IndexError):
        return None
    return None


if __name__ == "__main__":
    raise SystemExit(main())