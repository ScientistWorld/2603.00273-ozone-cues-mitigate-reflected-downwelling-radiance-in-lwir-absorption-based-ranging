#!/usr/bin/env python3
"""Paired per-target comparisons against the reference (audit only).

For each attempt, per-target reflective / ordinary MAE (same clipping and
missing-estimate rule as the evaluator) minus the reference's, averaged over
the test targets with its standard error. Uses hidden labels; audit tool.
"""

from __future__ import annotations

import argparse
import json
import math
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
CAP = 100.0


def per_target(pred: dict, labels: dict) -> dict[str, float]:
    out = {}
    for pid, lab in labels.items():
        vals = pred[pid]
        errs = [CAP if v is None else min(CAP, abs(v - d)) for v, d in zip(vals, lab["distance_m"])]
        out[pid] = sum(errs) / len(errs)
    return out


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--outputs", default=str(ROOT / "redteam" / "hardening" / "outputs"))
    parser.add_argument("--labels", default=str(ROOT / "eval" / "test" / "test_labels.json"))
    parser.add_argument("--reference", default="reference_quadspectral")
    parser.add_argument("--attempts", nargs="+", required=True)
    parser.add_argument("--output", default=str(ROOT / "redteam" / "hardening" / "paired_test.json"))
    args = parser.parse_args()
    labels = json.loads(Path(args.labels).read_text())["patches"]
    load = lambda n: json.loads((Path(args.outputs) / f"{n}_predictions.json").read_text())["patches"]
    ref = per_target(load(args.reference), labels)
    report = {}
    for name in args.attempts:
        cur = per_target(load(name), labels)
        row = {}
        for cls in ("reflective", "ordinary"):
            diffs = [cur[p] - ref[p] for p, lab in labels.items() if lab["class"] == cls]
            mu = sum(diffs) / len(diffs)
            se = math.sqrt(sum((d - mu) ** 2 for d in diffs) / (len(diffs) - 1) / len(diffs))
            row[cls] = {"mean_diff_m": round(mu, 3), "se_m": round(se, 3), "z": round(mu / se, 2) if se else None, "n": len(diffs)}
        report[name] = row
        print("%-38s refl %+7.2f ± %.2f (z %+6.1f)   ord %+7.2f ± %.2f (z %+6.1f)" % (
            name, row["reflective"]["mean_diff_m"], row["reflective"]["se_m"], row["reflective"]["z"] or 0,
            row["ordinary"]["mean_diff_m"], row["ordinary"]["se_m"], row["ordinary"]["z"] or 0))
    Path(args.output).write_text(json.dumps(report, indent=2) + "\n")


if __name__ == "__main__":
    main()
