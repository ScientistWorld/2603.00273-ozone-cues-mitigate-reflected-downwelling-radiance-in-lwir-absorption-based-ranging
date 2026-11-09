#!/usr/bin/env python3
"""Air-aware bispectral baseline (Eq. 14): ignores reflected downwelling radiance."""

from __future__ import annotations

import argparse
import json
import math
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "data"))
from lwir_physics import SPLITS, band_columns, blackbody_microflick, load_atmosphere, load_split  # noqa: E402

BANDS_1BASED = (23, 25)


def estimate_distance(l1, l2, bb1, bb2, alpha1, alpha2) -> float | None:
    denominator = l1 - bb1
    if denominator == 0.0:
        return None
    gamma = (l2 - bb2) / denominator
    if not math.isfinite(gamma) or gamma <= 0.0:
        return None
    distance = -10.0 * math.log10(gamma) / (alpha2 - alpha1)
    if not math.isfinite(distance) or distance < 0.0:
        return None
    return distance


def predict(data_dir: Path) -> dict[str, list]:
    atm = load_atmosphere(data_dir)
    cols = band_columns(atm, list(BANDS_1BASED))
    lam = [atm["wavelengths_um"][c] for c in cols]
    alpha = [atm["attenuation_db_per_m"][c] for c in cols]
    t_air = float(atm["t_air_k"])
    bb1, bb2 = blackbody_microflick(lam[0], t_air), blackbody_microflick(lam[1], t_air)
    out: dict[str, list] = {}
    for split in SPLITS:
        for pid, pixels in load_split(data_dir, split):
            out[pid] = [estimate_distance(p[cols[0]], p[cols[1]], bb1, bb2, alpha[0], alpha[1]) for p in pixels]
    return out


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--data-dir", default=str(ROOT / "data" / "lwir_scenes"))
    parser.add_argument("--output", default=str(ROOT / "outputs" / "bispectral_predictions.json"))
    args = parser.parse_args()
    payload = {"method": "bispectral", "patches": predict(Path(args.data_dir))}
    out = Path(args.output)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(payload) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
