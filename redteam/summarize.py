#!/usr/bin/env python3
"""Audit-only aggregation; never used by a candidate or the gym evaluator."""
from __future__ import annotations

import csv
import json
import math
import statistics
import subprocess
from pathlib import Path

ROOT = Path("/home/user")
AUDIT = ROOT / "redteam"
EXP = "lwir_reflective_patch_ranges"


def main():
    reference_spec = json.loads((ROOT / "scoring/reference.json").read_text())["experiments"][EXP]
    specs = reference_spec["metrics"]
    rows = {}
    for folder in sorted(AUDIT.iterdir()):
        if not folder.is_dir() or not (folder / "scores_test.json").is_file():
            continue
        scores = json.loads((folder / "scores_test.json").read_text())
        values = scores["experiments"][EXP]["results"]["quadspectral"]
        rows[folder.name] = {"metrics": values,
                             "finite": all(k in values and math.isfinite(values[k]) for k in specs)}
    anchor = rows["reference_seed0"]["metrics"]
    cohorts = {
        "all_finite_audit_attempts": [n for n, r in rows.items() if r["finite"]
                                      and n not in ("reference_seed1", "reference_seed2")],
        "finite_without_empty": [n for n, r in rows.items() if r["finite"]
                                  and n not in ("reference_seed1", "reference_seed2", "empty_shortcut")],
        "quality_checks": [n for n in rows if n.startswith("better_")]
                          + ["reference_seed0", "weaker_no_sky", "brute_force_physics"],
    }
    normalizations = {}
    for cohort, members in cohorts.items():
        scales = {k: statistics.pstdev(rows[n]["metrics"][k] for n in members) for k in specs}
        normalizations[cohort] = {"members": members, "population_stddev": scales}
        for name, row in rows.items():
            if not row["finite"]:
                row[cohort] = None
                continue
            components = {
                k: reference_spec.get("weight", 1) * abs(spec["coefficient"])
                   * (1 if spec["higher_is_better"] else -1)
                   * (row["metrics"][k] - anchor[k]) / scales[k]
                if scales[k] > 0 else 0.0
                for k, spec in specs.items()
            }
            row[cohort] = {"rank_delta": sum(components.values()), "components": components,
                           "population_member": name in members,
                           "scale_projection": name not in members}
    for name, row in rows.items():
        if not row["finite"]:
            row["quality_checks_with_candidate"] = None
            continue
        # This is an actual normalization population containing this attempt,
        # unlike projecting an unseen shortcut onto control-only scales.
        members = list(cohorts["quality_checks"])
        if name not in members:
            members.append(name)
        scales = {k: statistics.pstdev(rows[n]["metrics"][k] for n in members) for k in specs}
        rank = sum(reference_spec.get("weight", 1) * abs(spec["coefficient"])
                   * (1 if spec["higher_is_better"] else -1)
                   * (row["metrics"][k]-anchor[k])/scales[k]
                   for k, spec in specs.items() if scales[k] > 0)
        row["quality_checks_with_candidate"] = {"members": members, "population_stddev": scales, "rank_delta": rank}
    seeds = [rows[f"reference_seed{s}"] for s in (0, 1, 2)]
    spread = {k: max(row["metrics"][k] for row in seeds)-min(row["metrics"][k] for row in seeds)
              for k in specs}
    initial_commit = (AUDIT / "start_commit.txt").read_text().strip()
    initial = json.loads(subprocess.check_output(
        ["git", "show", f"{initial_commit}:scoring/scores_test.json"], text=True))
    original_anchor = initial["experiments"][EXP]["results"]["quadspectral"]
    for name, row in rows.items():
        row["dominates_reference"] = row["finite"] and all(
            (row["metrics"][k] >= anchor[k] if spec["higher_is_better"] else row["metrics"][k] <= anchor[k])
            for k, spec in specs.items()) and any(row["metrics"][k] != anchor[k] for k in specs)
        row["ties_reference"] = row["finite"] and row["metrics"] == anchor
    summary = {
        "rank_caveat": "Future normalization population is not known. Scores below instantiate the specified rank for explicitly listed audit populations; dominance conclusions hold for any positive metric scales.",
        "rank_formula": "sum(experiment_weight * abs(coefficient) * direction * (attempt-reference) / population_stddev)",
        "zero_scale_rule": "Constant metrics contribute zero within that cohort.",
        "reference_matches_initial_saved_test_exactly": anchor == original_anchor,
        "reference_matches_initial_saved_test_at_1e_10": all(abs(anchor[k]-original_anchor[k]) < 1e-10 for k in specs),
        "reference_max_absolute_roundoff_from_saved_test": max(abs(anchor[k]-original_anchor[k]) for k in specs),
        "reference_metrics_at_lower_bound_zero": [k for k in specs if anchor[k] == 0],
        "seed_metric_max_minus_min": spread,
        "normalizations": normalizations,
        "attempts": rows,
    }
    def strict(value):
        if isinstance(value, float) and not math.isfinite(value):
            return str(value)
        if isinstance(value, dict):
            return {k: strict(v) for k, v in value.items()}
        if isinstance(value, list):
            return [strict(v) for v in value]
        return value
    (AUDIT / "summary.json").write_text(json.dumps(strict(summary), indent=2, allow_nan=False)+"\n")
    with (AUDIT / "summary.csv").open("w", newline="") as fp:
        writer = csv.writer(fp, lineterminator="\n")
        writer.writerow(["attempt", "rank_delta_all_finite", "rank_delta_without_empty", "rank_delta_quality_scales_projection", "rank_delta_quality_plus_candidate", *specs])
        for name, row in rows.items():
            ranks = [row[c]["rank_delta"] if row[c] is not None else "nonfinite" for c in cohorts]
            if name == "empty_shortcut":
                ranks[1] = "excluded"
            ranks.append(row["quality_checks_with_candidate"]["rank_delta"] if row["finite"] else "nonfinite")
            writer.writerow([name, *ranks, *(row["metrics"].get(k) for k in specs)])
    print("attempt, primary MAE, tree MAE, invalid fraction, all-finite rank delta, without-empty rank delta, quality-scales projection")
    for name, row in rows.items():
        a = row["metrics"]
        ranks = [f"{row[c]['rank_delta']:.5f}" if row[c] is not None else "nonfinite" for c in cohorts]
        print(name, a["reflective_mean_abs_error_m"], a["tree_abs_error_m"], a["invalid_fraction"], *ranks, sep=", ")


if __name__ == "__main__":
    main()
