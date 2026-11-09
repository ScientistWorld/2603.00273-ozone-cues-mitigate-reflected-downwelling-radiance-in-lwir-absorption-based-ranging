#!/usr/bin/env python3
"""Hardening audit: build every variant / shortcut prediction file.

Each attempt is written as <out>/<name>_predictions.json and later scored by
the unchanged hidden-test evaluator (eval/test/evaluate.py). Shortcuts use
only scientist-visible inputs (data/lwir_scenes, eval/train labels).
"""

from __future__ import annotations

import argparse
import json
import math
import statistics as st
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "data"))
sys.path.insert(0, str(ROOT / "method" / "ozone_cues"))
sys.path.insert(0, str(ROOT / "baseline"))

import bispectral  # noqa: E402
import quadspectral  # noqa: E402
from lwir_physics import SPLITS, band_columns, blackbody_microflick, load_atmosphere, load_split  # noqa: E402

DATA = ROOT / "data" / "lwir_scenes"
N = 8


def write(out_dir: Path, name: str, patches: dict, extra: dict | None = None, raw_text: str | None = None) -> None:
    path = out_dir / f"{name}_predictions.json"
    if raw_text is not None:
        path.write_text(raw_text, encoding="utf-8")
        return
    payload = {"method": name, "patches": patches}
    if extra:
        payload.update(extra)
    path.write_text(json.dumps(payload) + "\n", encoding="utf-8")


def patch_median_fill(values: list) -> list:
    valid = [v for v in values if v is not None]
    m = st.median(valid) if valid else None
    return [m] * len(values)


def local_median(values: list, radius: int = 1) -> list:
    out = []
    for i in range(N):
        for j in range(N):
            neigh = [
                values[a * N + b]
                for a in range(max(0, i - radius), min(N, i + radius + 1))
                for b in range(max(0, j - radius), min(N, j + radius + 1))
                if values[a * N + b] is not None
            ]
            out.append(st.median(neigh) if neigh else None)
    # fill any remaining hole with the patch median
    valid = [v for v in out if v is not None]
    m = st.median(valid) if valid else None
    return [v if v is not None else m for v in out]


def aircentred_quad(atm: dict, data_dir: Path = DATA) -> dict[str, list]:
    """Variant: air-centre the ozone cue, s*((L4-B4(Tair)) - (L3-B3(Tair)))."""
    cols = band_columns(atm, list(quadspectral.BANDS_1BASED))
    lam = [atm["wavelengths_um"][c] for c in cols]
    alpha = [atm["attenuation_db_per_m"][c] for c in cols]
    t_air = float(atm["t_air_k"])
    bb = [blackbody_microflick(l, t_air) for l in lam]
    s = quadspectral.sky_cue_slope(atm, *quadspectral.BANDS_1BASED)
    out = {}
    for split in SPLITS:
        for pid, pixels in load_split(data_dir, split):
            out[pid] = [
                quadspectral.estimate_distance(
                    p[cols[0]], p[cols[1]], p[cols[2]] - bb[2], p[cols[3]] - bb[3], bb[0], bb[1], s, alpha[0], alpha[1]
                )
                for p in pixels
            ]
    return out


def patch_features(atm: dict, pixels: list) -> list[float]:
    t_air = float(atm["t_air_k"])
    bb = [blackbody_microflick(l, t_air) for l in atm["wavelengths_um"]]
    k = len(bb)
    return [sum(p[c] for p in pixels) / len(pixels) - bb[c] for c in range(k)]


def solve(a: list[list[float]], b: list[float]) -> list[float]:
    n = len(b)
    m = [row[:] + [b[i]] for i, row in enumerate(a)]
    for col in range(n):
        piv = max(range(col, n), key=lambda r: abs(m[r][col]))
        m[col], m[piv] = m[piv], m[col]
        for r in range(n):
            if r != col and m[r][col] != 0.0:
                f = m[r][col] / m[col][col]
                for c in range(col, n + 1):
                    m[r][c] -= f * m[col][c]
    return [m[i][n] / m[i][i] for i in range(n)]


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--out", default=str(ROOT / "redteam" / "hardening" / "outputs"))
    args = parser.parse_args()
    out = Path(args.out)
    out.mkdir(parents=True, exist_ok=True)
    atm = load_atmosphere(DATA)
    splits = {s: load_split(DATA, s) for s in SPLITS}
    all_ids = [pid for s in SPLITS for pid, _ in splits[s]]
    train_labels = json.loads((ROOT / "eval" / "train" / "train_labels.json").read_text())["patches"]

    quad = quadspectral.predict(DATA)
    bis = bispectral.predict(DATA)

    # --- reference, weaker and better variants -------------------------------------------
    write(out, "reference_quadspectral", quad)
    write(out, "weaker_no_sky_correction", bis)
    write(out, "weaker_half_sky_slope", quadspectral.predict(DATA, slope_scale=0.5))
    write(out, "weaker_sky_slope_0p8", quadspectral.predict(DATA, slope_scale=0.8))
    write(out, "better_local_median3x3", {pid: local_median(v) for pid, v in quad.items()})
    write(out, "better_patch_median", {pid: patch_median_fill(v) for pid, v in quad.items()})
    air = aircentred_quad(atm)
    write(out, "better_aircentred_cue", air)
    write(out, "better_aircentred_cue_patch_median", {pid: patch_median_fill(v) for pid, v in air.items()})

    # --- shortcuts ----------------------------------------------------------------------------
    train_dist = [d for lab in train_labels.values() for d in lab["distance_m"]]
    c_med = st.median(train_dist)
    write(out, "shortcut_constant_train_median", {pid: [c_med] * 64 for pid in all_ids})
    write(out, "shortcut_constant40", {pid: [40.0] * 64 for pid in all_ids})
    write(out, "shortcut_zero", {pid: [0.0] * 64 for pid in all_ids})
    write(out, "shortcut_short_length", {pid: patch_median_fill(v)[:2] for pid, v in quad.items()})

    def keep_closest(values: list, keep: int) -> list:
        valid = [v for v in values if v is not None]
        if not valid:
            return values
        m = st.median(valid)
        ranked = sorted((abs(v - m), i) for i, v in enumerate(values) if v is not None)[:keep]
        idx = {i for _, i in ranked}
        return [v if i in idx else None for i, v in enumerate(values)]

    write(out, "shortcut_null_filter25", {pid: keep_closest(v, 16) for pid, v in quad.items()})
    write(out, "shortcut_empty", {pid: [] for pid in all_ids})
    write(out, "shortcut_nan", None, raw_text=json.dumps({"patches": {pid: [float("nan")] * 64 for pid in all_ids}}))
    write(out, "shortcut_infinity", None, raw_text=json.dumps({"patches": {pid: [float("inf")] * 64 for pid in all_ids}}))
    write(out, "shortcut_negative", {pid: [-(v or 0.0) for v in vals] for pid, vals in quad.items()})

    # copy the paper's published real-scene ranges onto the real patches, reference elsewhere
    real_copy = dict(quad)
    for pid, d in (("ih_p5s1_a", 31.01), ("ih_p5s1_b", 46.51), ("ih_p5s1_c", 57.84)):
        real_copy[pid] = [d] * 64
    write(out, "shortcut_real_label_copy", real_copy)

    # fabricated score fields riding along with the reference predictions
    write(
        out,
        "shortcut_score_forgery",
        quad,
        extra={
            "metrics": {"reflective_mae_m": 0.0, "reflective_patch_abs_error_m": 0.0, "ordinary_mae_m": 0.0},
            "run_failed": False,
            "success": True,
        },
    )

    # supervised shortcuts trained on the visible train labels
    feats = {pid: patch_features(atm, px) for s in SPLITS for pid, px in splits[s]}
    tr_ids = [pid for pid, _ in splits["train"]]
    y = [sum(train_labels[p]["distance_m"]) / 64 for p in tr_ids]
    k = len(feats[tr_ids[0]])
    mu = [sum(feats[p][c] for p in tr_ids) / len(tr_ids) for c in range(k)]
    sd = [math.sqrt(sum((feats[p][c] - mu[c]) ** 2 for p in tr_ids) / len(tr_ids)) or 1.0 for c in range(k)]
    z = {pid: [(f[c] - mu[c]) / sd[c] for c in range(k)] for pid, f in feats.items()}
    # kNN label copy (k=5) in standardised radiance-feature space
    knn = {}
    for pid in all_ids:
        near = sorted(tr_ids, key=lambda t: sum((a - b) ** 2 for a, b in zip(z[pid], z[t])))[:5]
        guess = sum(y[tr_ids.index(t)] for t in near) / 5
        knn[pid] = [guess] * 64
    write(out, "shortcut_train_knn_label_copy", knn)
    # ridge regression from standardised features to range
    ym = sum(y) / len(y)
    lam_reg = 1.0
    xtx = [[sum(z[p][a] * z[p][b] for p in tr_ids) + (lam_reg if a == b else 0.0) for b in range(k)] for a in range(k)]
    xty = [sum(z[p][a] * (yy - ym) for p, yy in zip(tr_ids, y)) for a in range(k)]
    w = solve(xtx, xty)
    ridge = {pid: [max(0.0, ym + sum(wi * zi for wi, zi in zip(w, z[pid])))] * 64 for pid in all_ids}
    write(out, "shortcut_train_ridge_regression", ridge)
    # affine recalibration of the reference fitted on train patch medians
    pm = [st.median([v for v in quad[p] if v is not None]) for p in tr_ids]
    xm, ym2 = sum(pm) / len(pm), sum(y) / len(y)
    slope = sum((a - xm) * (b - ym2) for a, b in zip(pm, y)) / sum((a - xm) ** 2 for a in pm)
    icpt = ym2 - slope * xm
    calib = {pid: [None if v is None else max(0.0, icpt + slope * v) for v in vals] for pid, vals in quad.items()}
    write(out, "shortcut_train_affine_calibration", calib)
    print("affine calibration slope %.4f intercept %.3f" % (slope, icpt))


if __name__ == "__main__":
    main()
