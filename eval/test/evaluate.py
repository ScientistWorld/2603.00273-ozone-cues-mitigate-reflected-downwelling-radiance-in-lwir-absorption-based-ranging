#!/usr/bin/env python3
"""Held-out test evaluator for the LWIR patch-ranging gym.

Scores every ``outputs/*_predictions.json`` against held-out simulated
targets (labels in this directory only) and runs the real-scene check.
All numbers are recomputed from the raw per-pixel range estimates; nothing
written by a method other than those estimates is read.
"""

from __future__ import annotations

import argparse
import json
import math
from pathlib import Path

HERE = Path(__file__).resolve().parent
EXPERIMENT = "lwir_reflective_patch_ranges"
SLICE = "test"
PIXELS_PER_PATCH = 64
# Per-pixel absolute errors are clipped here, and a missing (null) estimate
# costs exactly this much: abstaining is never cheaper than any estimate.
ERROR_CAP_M = 100.0
# Real-scene check: on the two real checkerboards, ranging that ignores
# reflected sky radiance errs by more than 100 m; a method must bring the
# mean per-pixel error (null = 100 m) to at most this value.
REAL_REFLECTIVE_GATE_M = 35.0
SCORED_METRICS = ("reflective_mae_m", "reflective_patch_abs_error_m", "ordinary_mae_m")


def mean(values: list[float]) -> float:
    # math.fsum is correctly rounded, so scores are bit-identical across Python versions.
    return math.fsum(values) / len(values)


def median(values: list[float]) -> float:
    ordered = sorted(values)
    mid = len(ordered) // 2
    if len(ordered) % 2:
        return ordered[mid]
    return 0.5 * (ordered[mid - 1] + ordered[mid])


def stdev(values: list[float]) -> float:
    if len(values) < 2:
        return 0.0
    mu = mean(values)
    return math.sqrt(math.fsum((v - mu) ** 2 for v in values) / (len(values) - 1))


def load_labels(path: Path) -> dict[str, dict]:
    raw = json.loads(path.read_text(encoding="utf-8"))["patches"]
    labels = {}
    for pid, item in raw.items():
        dist = item["distance_m"]
        if not isinstance(dist, list):
            dist = [float(dist)] * PIXELS_PER_PATCH
        labels[pid] = {"class": item["class"], "distance_m": [float(d) for d in dist]}
    return labels


def _is_number(v: object) -> bool:
    return isinstance(v, (int, float)) and not isinstance(v, bool)


def validate_predictions(path: Path, required: list[str]) -> tuple[dict[str, list] | None, str | None]:
    """Return (patch -> estimates, None) or (None, reason) for a malformed submission."""
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, ValueError) as exc:
        return None, f"unreadable prediction file: {exc.__class__.__name__}"
    patches = data.get("patches") if isinstance(data, dict) else None
    if not isinstance(patches, dict):
        return None, "prediction file must hold a 'patches' object mapping patch id -> estimates"
    out: dict[str, list] = {}
    for pid in required:
        values = patches.get(pid)
        if not isinstance(values, list):
            return None, f"missing estimates for patch {pid}"
        if len(values) != PIXELS_PER_PATCH:
            return None, f"patch {pid} has {len(values)} estimates, expected {PIXELS_PER_PATCH}"
        for v in values:
            if v is None:
                continue
            if not _is_number(v):
                return None, f"patch {pid} holds a non-numeric estimate"
            if not math.isfinite(float(v)):
                return None, f"patch {pid} holds a non-finite estimate"
            if float(v) < 0.0:
                return None, f"patch {pid} holds a negative range"
        out[pid] = values
    return out, None


def pixel_error(value: object, truth: float) -> float:
    if value is None:
        return ERROR_CAP_M
    return min(ERROR_CAP_M, abs(float(value) - truth))


def patch_estimate(values: list) -> float:
    """Median of the patch's estimates, a missing estimate counting as +infinity."""
    return median([float(v) if v is not None else math.inf for v in values])


def class_metrics(preds: dict[str, list], labels: dict[str, dict], cls: str) -> dict[str, float]:
    errors: list[float] = []
    patch_errors: list[float] = []
    patch_stds: list[float] = []
    truths: list[float] = []
    invalid = 0
    for pid, lab in labels.items():
        if lab["class"] != cls:
            continue
        values = preds[pid]
        dist = lab["distance_m"]
        errors.extend(pixel_error(v, d) for v, d in zip(values, dist))
        truths.extend(dist)
        invalid += sum(v is None for v in values)
        est = patch_estimate(values)
        patch_errors.append(min(ERROR_CAP_M, abs(est - mean(dist))) if math.isfinite(est) else ERROR_CAP_M)
        patch_stds.append(stdev([float(v) for v in values if v is not None]))
    centre = median(truths)
    return {
        "mae": mean(errors),
        "patch_abs_error": mean(patch_errors),
        "patch_std": mean(patch_stds),
        "invalid_fraction": invalid / len(errors),
        "constant_guess_mae": mean([abs(d - centre) for d in truths]),
        "n_patches": len(patch_errors),
    }


def score(path: Path, sim_labels: dict[str, dict], real_labels: dict[str, dict]) -> tuple[dict, dict]:
    required = sorted(sim_labels) + sorted(real_labels)
    preds, reason = validate_predictions(path, required)
    failures: list[str] = [] if reason is None else [reason]
    diag: dict[str, object] = {}
    raw: dict[str, float] = {}
    if preds is not None:
        refl = class_metrics(preds, sim_labels, "reflective")
        ordi = class_metrics(preds, sim_labels, "ordinary")
        real_refl = class_metrics(preds, real_labels, "reflective")
        real_ordi = class_metrics(preds, real_labels, "ordinary")
        raw = {
            "reflective_mae_m": refl["mae"],
            "reflective_patch_abs_error_m": refl["patch_abs_error"],
            "ordinary_mae_m": ordi["mae"],
        }
        diag = {
            "ordinary_patch_abs_error_m": ordi["patch_abs_error"],
            "reflective_patch_std_m": refl["patch_std"],
            "ordinary_patch_std_m": ordi["patch_std"],
            "reflective_invalid_fraction": refl["invalid_fraction"],
            "ordinary_invalid_fraction": ordi["invalid_fraction"],
            "reflective_constant_guess_mae_m": refl["constant_guess_mae"],
            "ordinary_constant_guess_mae_m": ordi["constant_guess_mae"],
            "real_reflective_mae_m": real_refl["mae"],
            "real_low_reflectance_mae_m": real_ordi["mae"],
            "real_reflective_gate_m": REAL_REFLECTIVE_GATE_M,
        }
        if refl["mae"] >= refl["constant_guess_mae"]:
            failures.append("reflective targets: no better than the best constant range guess")
        if ordi["mae"] >= ordi["constant_guess_mae"]:
            failures.append("ordinary targets: no better than the best constant range guess")
        if real_refl["mae"] > REAL_REFLECTIVE_GATE_M:
            failures.append("real scene: reflective-target error above the reflected-sky gate")
    failed = bool(failures)
    results = {m: (ERROR_CAP_M if failed else raw[m]) for m in SCORED_METRICS}
    diag["run_failed"] = failed
    diag["failure_reasons"] = failures
    diag["ungated"] = raw
    return results, diag


def discover_predictions(outputs_dir: Path) -> dict[str, Path]:
    found: dict[str, Path] = {}
    for path in sorted(outputs_dir.glob("*_predictions.json")):
        found[path.name[: -len("_predictions.json")]] = path
    return found


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--outputs-dir", default="outputs")
    parser.add_argument("--labels", default=str(HERE / "test_labels.json"))
    parser.add_argument("--real-labels", default=str(HERE / "real_labels.json"))
    parser.add_argument("--output", default="scoring/scores_test.json")
    args = parser.parse_args()

    sim_labels = load_labels(Path(args.labels))
    real_labels = load_labels(Path(args.real_labels))
    predictions = discover_predictions(Path(args.outputs_dir))
    if not predictions:
        raise SystemExit(f"No *_predictions.json files found in {args.outputs_dir}")
    results, diagnostics = {}, {}
    for name, path in predictions.items():
        results[name], diagnostics[name] = score(path, sim_labels, real_labels)
    payload = {
        "_slice": SLICE,
        "experiments": {
            EXPERIMENT: {
                "_slice": SLICE,
                "results": results,
                "_diagnostics": diagnostics,
            }
        },
    }
    out = Path(args.output)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
