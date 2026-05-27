#!/usr/bin/env python3
from __future__ import annotations

import argparse
import hashlib
import json
import math
from pathlib import Path


PATCH_TO_METRIC = {
    "front_checkerboard": "front_abs_error_m",
    "rear_checkerboard": "rear_abs_error_m",
    "tree": "tree_abs_error_m",
}

EXPERIMENT = "lwir_reflective_patch_ranges"
SLICE = "test"
SPLIT_SALT = "researchgym-lwir-patch-heldout-v2"
TRAIN_SPLIT_SALT = "researchgym-lwir-patch-visible-v2"


def mean(values: list[float]) -> float:
    return sum(values) / len(values)


def median(values: list[float]) -> float:
    if not values:
        return 1.0e9
    ordered = sorted(values)
    mid = len(ordered) // 2
    if len(ordered) % 2:
        return ordered[mid]
    return (ordered[mid - 1] + ordered[mid]) / 2.0


def percentile(values: list[float], q: float) -> float:
    if not values:
        return 1.0e9
    ordered = sorted(values)
    if len(ordered) == 1:
        return ordered[0]
    pos = (len(ordered) - 1) * q
    lo = math.floor(pos)
    hi = math.ceil(pos)
    if lo == hi:
        return ordered[lo]
    return ordered[lo] * (hi - pos) + ordered[hi] * (pos - lo)


def stdev(values: list[float]) -> float:
    if len(values) < 2:
        return 0.0
    mu = mean(values)
    return math.sqrt(sum((v - mu) ** 2 for v in values) / (len(values) - 1))


def load_labels(path: Path) -> dict[str, dict[str, float | str]]:
    labels = json.loads(path.read_text(encoding="utf-8"))
    return {patch["name"]: patch for patch in labels["patches"]}


def split_rank(index: int, count: int) -> tuple[int, int]:
    digest = hashlib.blake2b(
        f"{SPLIT_SALT}:{count}:{index}".encode("ascii"),
        digest_size=8,
    ).digest()
    return (int.from_bytes(digest, "big"), index)


def train_split_rank(index: int, count: int) -> tuple[int, int]:
    digest = hashlib.blake2b(
        f"{TRAIN_SPLIT_SALT}:{count}:{index}".encode("ascii"),
        digest_size=8,
    ).digest()
    return (int.from_bytes(digest, "big"), index)


def train_selected_indices(count: int) -> set[int]:
    target = count // 2
    ranked = sorted(range(count), key=lambda index: train_split_rank(index, count))
    return set(ranked[:target])


def selected_indices(count: int) -> set[int]:
    target = count // 2
    train_members = train_selected_indices(count)
    candidates = [index for index in range(count) if index not in train_members]
    ranked = sorted(candidates, key=lambda index: split_rank(index, count))
    return set(ranked[:target])


def selected_estimates(estimates: list[object]) -> list[object]:
    members = selected_indices(len(estimates))
    return [value for i, value in enumerate(estimates) if i in members]


def summarize(path: Path, labels: dict[str, dict[str, float | str]]) -> dict[str, float]:
    data = json.loads(path.read_text(encoding="utf-8"))
    metrics: dict[str, float] = {}
    reflective_errors: list[float] = []
    reflective_signed_errors: list[float] = []
    invalid_count = 0
    total_count = 0
    for patch in data["patches"]:
        label = labels[patch["name"]]
        estimates = selected_estimates(patch["estimates_m"])
        total_count += len(estimates)
        valid = [float(v) for v in estimates if isinstance(v, (int, float))]
        invalid_count += len(estimates) - len(valid)
        signed_errors = [v - float(label["distance_m"]) for v in valid]
        abs_errors = [abs(v) for v in signed_errors]
        metric_name = PATCH_TO_METRIC[patch["name"]]
        metrics[metric_name] = mean(abs_errors) if abs_errors else 1.0e9
        metrics[metric_name.replace("_abs_error_m", "_std_m")] = stdev(valid)
        if label["type"] == "reflective":
            reflective_errors.extend(abs_errors)
            reflective_signed_errors.extend(signed_errors)
    metrics["reflective_mean_abs_error_m"] = (
        mean(reflective_errors) if reflective_errors else 1.0e9
    )
    metrics["reflective_median_abs_error_m"] = median(reflective_errors)
    metrics["reflective_p90_abs_error_m"] = percentile(reflective_errors, 0.90)
    metrics["reflective_abs_bias_m"] = (
        abs(mean(reflective_signed_errors)) if reflective_signed_errors else 1.0e9
    )
    metrics["invalid_fraction"] = invalid_count / total_count if total_count else 1.0
    return metrics


def method_name(path: Path) -> str:
    data = json.loads(path.read_text(encoding="utf-8"))
    name = data.get("method")
    if isinstance(name, str) and name:
        return name
    suffix = "_predictions"
    return path.stem[: -len(suffix)] if path.stem.endswith(suffix) else path.stem


def all_predictions(outputs_dir: Path) -> dict[str, Path]:
    predictions: dict[str, Path] = {}
    for path in sorted(outputs_dir.glob("*_predictions.json")):
        predictions[method_name(path)] = path
    if not predictions:
        raise FileNotFoundError(f"No *_predictions.json files found in {outputs_dir}")
    return predictions


def train_methods(path: Path) -> list[str]:
    scores = json.loads(path.read_text(encoding="utf-8"))
    experiment = scores["experiments"][EXPERIMENT]
    return [
        name
        for name in experiment["results"]
        if not name.startswith("_")
    ]


def discover_predictions(outputs_dir: Path, method_source: Path) -> dict[str, Path]:
    predictions = all_predictions(outputs_dir)
    if not method_source.is_file():
        return predictions
    selected: dict[str, Path] = {}
    missing: list[str] = []
    for name in train_methods(method_source):
        if name in predictions:
            selected[name] = predictions[name]
        else:
            missing.append(name)
    if missing:
        joined = ", ".join(missing)
        raise FileNotFoundError(
            f"Missing prediction files for train-scored method(s): {joined}"
        )
    return selected


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--outputs-dir", default="outputs")
    parser.add_argument("--labels", default="eval/test/lwir_patch_test_labels.json")
    parser.add_argument("--method-source", default="scoring/scores_train.json")
    parser.add_argument("--output", default="scoring/scores_test.json")
    args = parser.parse_args()

    labels = load_labels(Path(args.labels))
    predictions = discover_predictions(Path(args.outputs_dir), Path(args.method_source))
    scores = {
        "_slice": SLICE,
        "experiments": {
            EXPERIMENT: {
                "_slice": SLICE,
                "results": {
                    name: summarize(path, labels)
                    for name, path in sorted(predictions.items())
                },
            }
        },
    }
    output = Path(args.output)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(scores, indent=2) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
