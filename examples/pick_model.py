#!/usr/bin/env python3
"""Example: pick the right model for a RAM budget from the catalog.

Combines the memory estimator with the catalog to recommend the largest model
that fits your device's free RAM, or a given budget.

Run:
    python examples/pick_model.py --budget-mb 3500
    python examples/pick_model.py --device
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from memory_estimator import _catalog, score_device, pick_for_budget  # noqa: E402


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description="Pick a model for your RAM budget.")
    ap.add_argument("--budget-mb", type=float, default=None)
    ap.add_argument("--device", action="store_true")
    args = ap.parse_args(argv)

    if args.device:
        from memory_estimator import device_free_ram_mb
        free = device_free_ram_mb()
        if free is None:
            print("no /proc/meminfo; pass --budget-mb")
            return 1
        fits = score_device(free)
        print(f"device free RAM ≈ {free:.0f} MB — recommended models:")
    elif args.budget_mb:
        fits = pick_for_budget(_catalog(), args.budget_mb)
        print(f"budget {args.budget_mb:.0f} MB — fitting models:")
    else:
        ap.error("--device or --budget-mb required")

    if not fits:
        print("  (none fit — reduce context, smaller quant, or free RAM)")
        return 0
    for e in fits:
        print(f"  {e['key']:<20} ~{e['estimated_ram_mb']:>5} MB  "
              f"({e['params_billions']}B @ {e['quant']})")
    best = fits[-1]
    print(f"\nRecommended: {best['key']} ({best['name']}) — largest that fits.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())