#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import math
from pathlib import Path


PATCH_TO_METRIC = {
    "front_checkerboard": "front_abs_error_m",
    "rear_checkerboard": "rear_abs_error_m",
    "tree": "tree_abs_error_m",
}


def mean(values: list[float]) -> float:
    return sum(values) / len(values)


def stdev(values: list[float]) -> float:
    if len(values) < 2:
        return 0.0
    mu = mean(values)
    return math.sqrt(sum((v - mu) ** 2 for v in values) / (len(values) - 1))


def load_labels(path: Path) -> dict[str, dict[str, float | str]]:
    labels = json.loads(path.read_text(encoding="utf-8"))
    return {patch["name"]: patch for patch in labels["patches"]}


def summarize(path: Path, labels: dict[str, dict[str, float | str]]) -> dict[str, float]:
    data = json.loads(path.read_text(encoding="utf-8"))
    metrics: dict[str, float] = {}
    reflective_errors = []
    invalid_count = 0
    total_count = 0
    for patch in data["patches"]:
        label = labels[patch["name"]]
        estimates = patch["estimates_m"]
        total_count += len(estimates)
        valid = [float(v) for v in estimates if isinstance(v, (int, float))]
        invalid_count += len(estimates) - len(valid)
        abs_errors = [abs(v - float(label["distance_m"])) for v in valid]
        metric_name = PATCH_TO_METRIC[patch["name"]]
        metrics[metric_name] = mean(abs_errors) if abs_errors else 1.0e9
        metrics[metric_name.replace("_abs_error_m", "_std_m")] = stdev(valid)
        if label["type"] == "reflective":
            reflective_errors.extend(abs_errors)
    metrics["reflective_mean_abs_error_m"] = mean(reflective_errors) if reflective_errors else 1.0e9
    metrics["invalid_fraction"] = invalid_count / total_count if total_count else 1.0
    return metrics


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--bispectral", default="outputs/bispectral_predictions.json")
    parser.add_argument("--quadspectral", default="outputs/quadspectral_predictions.json")
    parser.add_argument("--labels", default="eval/quadspectral_core_labels.json")
    parser.add_argument("--output", default="scoring/scores.json")
    args = parser.parse_args()
    labels = load_labels(Path(args.labels))

    scores = {
        "experiments": {
            "quadspectral_patch_ranges": {
                "results": {
                    "bispectral": summarize(Path(args.bispectral), labels),
                    "quadspectral": summarize(Path(args.quadspectral), labels),
                }
            }
        }
    }
    output = Path(args.output)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(scores, indent=2) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
