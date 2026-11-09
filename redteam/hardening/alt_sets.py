#!/usr/bin/env python3
"""Robustness audit: rebuild the held-out set with three other keys and rescore.

Checks that the reference/baseline gap and the ordering of better/weaker
variants are stable across independent test-set realisations (the method is
deterministic, so test sampling is the only noise source).
"""

from __future__ import annotations

import json
import random
import shutil
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
for sub in ("data", "method/ozone_cues", "baseline", "eval/test", "redteam/hardening"):
    sys.path.insert(0, str(ROOT / sub))

import bispectral  # noqa: E402
import evaluate as test_eval  # noqa: E402  (eval/test/evaluate.py)
import make_attempts as ma  # noqa: E402
import quadspectral  # noqa: E402
from lwir_physics import load_atmosphere, write_split  # noqa: E402
from scene_simulator import simulate_patch  # noqa: E402


def build(key: str, data_dir: Path) -> dict:
    atm = load_atmosphere(data_dir)
    rng = random.Random(key)
    order = ["reflective"] * 192 + ["ordinary"] * 96
    rng.shuffle(order)
    patches, labels = [], {}
    for i, cls in enumerate(order):
        pixels, dist, _ = simulate_patch(rng, cls, atm)
        pid = f"alt_{i:04d}"
        patches.append((pid, pixels))
        labels[pid] = {"class": cls, "distance_m": dist}
    write_split(data_dir, "test", patches, n_bands=len(atm["band_index_1based"]))
    # train split is not needed by these estimators; reuse the test cube under the train name
    write_split(data_dir, "train", patches[:1], n_bands=len(atm["band_index_1based"]))
    return labels


def main() -> None:
    report = {}
    for key in ("alt-key-1", "alt-key-2", "alt-key-3"):
        tmp = Path(tempfile.mkdtemp())
        for f in ("atmosphere.json", "real_index.json", "real_radiance.f32"):
            shutil.copy(ROOT / "data" / "lwir_scenes" / f, tmp / f)
        labels = build(key, tmp)
        lab_path = tmp / "labels.json"
        lab_path.write_text(json.dumps({"patches": labels}))
        quad = quadspectral.predict(tmp)
        air = ma.aircentred_quad(load_atmosphere(tmp), tmp)
        attempts = {
            "reference_quadspectral": quad,
            "weaker_no_sky_correction": bispectral.predict(tmp),
            "weaker_sky_slope_0p8": quadspectral.predict(tmp, slope_scale=0.8),
            "better_aircentred_cue": air,
            "better_local_median3x3": {p: ma.local_median(v) for p, v in quad.items()},
            "better_patch_median": {p: ma.patch_median_fill(v) for p, v in quad.items()},
            "better_aircentred_cue_patch_median": {p: ma.patch_median_fill(v) for p, v in air.items()},
        }
        sim = test_eval.load_labels(lab_path)
        real = test_eval.load_labels(ROOT / "eval" / "test" / "real_labels.json")
        rows = {}
        for name, pred in attempts.items():
            f = tmp / f"{name}_predictions.json"
            f.write_text(json.dumps({"patches": pred}))
            res, diag = test_eval.score(f, sim, real)
            rows[name] = {"results": {k: round(v, 3) for k, v in res.items()}, "run_failed": diag["run_failed"],
                          "ungated": {k: round(v, 3) for k, v in diag["ungated"].items()}}
        report[key] = rows
        shutil.rmtree(tmp)
        print(key)
        for name, r in rows.items():
            print("   %-38s %s failed=%s ungated=%s" % (name, r["results"], r["run_failed"], r["ungated"]))
    (ROOT / "redteam" / "hardening" / "alt_sets.json").write_text(json.dumps(report, indent=2) + "\n")


if __name__ == "__main__":
    main()
