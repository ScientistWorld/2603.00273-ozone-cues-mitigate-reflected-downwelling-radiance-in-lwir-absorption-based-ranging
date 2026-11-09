#!/usr/bin/env python3
"""Rank every audited attempt against the reference, as the gym's ranker does.

rank = sum_m |coef_m| * improvement_m / spread_m, improvement taken in each
metric's better direction (all scored metrics here are lower-is-better),
spread_m = population standard deviation of metric m across the attempts.
Population A: every audited attempt. Population B: the non-failed attempts
plus the candidate itself.
"""

from __future__ import annotations

import argparse
import csv
import json
import math
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
EXP = "lwir_reflective_patch_ranges"


def pstdev(values: list[float]) -> float:
    mu = sum(values) / len(values)
    return math.sqrt(sum((v - mu) ** 2 for v in values) / len(values))


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--scores", default=str(ROOT / "redteam" / "hardening" / "scores_test_all.json"))
    parser.add_argument("--reference-name", default="reference_quadspectral")
    parser.add_argument("--out-prefix", default=str(ROOT / "redteam" / "hardening" / "summary"))
    args = parser.parse_args()

    ref_def = json.loads((ROOT / "scoring" / "reference.json").read_text())["experiments"][EXP]["metrics"]
    scores = json.loads(Path(args.scores).read_text())["experiments"][EXP]
    results, diags = scores["results"], scores["_diagnostics"]
    metrics = [m for m, d in ref_def.items() if abs(float(d.get("coefficient", 0.0))) > 0]
    ref = results[args.reference_name]

    def rank(name: str, population: list[str]) -> float:
        total = 0.0
        for m in metrics:
            spread = pstdev([results[p][m] for p in population])
            if spread == 0.0:
                continue
            sign = 1.0 if ref_def[m]["higher_is_better"] else -1.0
            total += abs(float(ref_def[m]["coefficient"])) * sign * (results[name][m] - ref[m]) / spread
        return total

    names = sorted(results)
    pop_a = names
    ok = [n for n in names if not diags[n]["run_failed"]]
    rows = []
    for n in names:
        pop_b = sorted(set(ok) | {n})
        rows.append(
            {
                "attempt": n,
                **{m: round(results[n][m], 4) for m in metrics},
                "run_failed": diags[n]["run_failed"],
                "failure_reasons": "; ".join(diags[n]["failure_reasons"]),
                "ungated_reflective_mae_m": round(diags[n].get("ungated", {}).get("reflective_mae_m", float("nan")), 4)
                if diags[n].get("ungated")
                else None,
                "real_reflective_mae_m": round(diags[n]["real_reflective_mae_m"], 4) if "real_reflective_mae_m" in diags[n] else None,
                "rank_delta_A": round(rank(n, pop_a), 6),
                "rank_delta_B": round(rank(n, pop_b), 6),
            }
        )
    Path(args.out_prefix + ".json").write_text(
        json.dumps({"metrics": metrics, "population_A": pop_a, "population_B_core": ok, "rows": rows}, indent=2) + "\n"
    )
    with open(args.out_prefix + ".csv", "w", newline="") as fh:
        writer = csv.DictWriter(fh, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)
    for r in sorted(rows, key=lambda r: -r["rank_delta_A"]):
        print(
            "%-40s refl %7.2f patch %7.2f ord %7.2f failed=%-5s A %+8.3f B %+8.3f %s"
            % (
                r["attempt"],
                r["reflective_mae_m"],
                r["reflective_patch_abs_error_m"],
                r["ordinary_mae_m"],
                r["run_failed"],
                r["rank_delta_A"],
                r["rank_delta_B"],
                r["failure_reasons"][:70],
            )
        )


if __name__ == "__main__":
    main()
