#!/usr/bin/env python3
"""Closed-form quadspectral ozone-cue ranging (Sec. IV of the paper).

lambda1/lambda2: water-vapour absorption band and nearby clear band
lambda3/lambda4: ozone absorption band and nearby clear band
The reflected-downwelling bias b of the air-centred bispectral ratio is
estimated as s * (L(lambda4) - L(lambda3)) (Eq. 22), with s the least-squares
slope between the water-vapour and ozone differences of the downwelling
spectra at the dictionary's zenith angles (Eq. 21), then removed before the
Beer's-law closed form (Eq. 18). Band choice follows the authors' Table I
script (bands 23/25 and 77/81 of the instrument).
"""

from __future__ import annotations

import argparse
import json
import math
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "data"))
from lwir_physics import SPLITS, band_columns, blackbody_microflick, load_atmosphere, load_split  # noqa: E402

BANDS_1BASED = (23, 25, 77, 81)


def sky_cue_slope(atm: dict, water_abs: int, water_clear: int, ozone_abs: int, ozone_clear: int) -> float:
    """Eq. (21): least-squares slope of (L_D(l1)-L_D(l2)) on (L_D(l3)-L_D(l4)) across zenith angles."""
    c = band_columns(atm, [water_abs, water_clear, ozone_abs, ozone_clear])
    dw = atm["downwelling_microflick"]
    xs = [dw[c[2]][q] - dw[c[3]][q] for q in range(len(atm["downwelling_zenith_deg"]))]
    ys = [dw[c[0]][q] - dw[c[1]][q] for q in range(len(xs))]
    return sum(x * y for x, y in zip(xs, ys)) / sum(x * x for x in xs)


def estimate_distance(l1, l2, l3, l4, bb1, bb2, slope, alpha1, alpha2) -> float | None:
    """Eqs. (18) and (22); returns None where the closed form has no real non-negative solution."""
    denominator = l1 - bb1
    if denominator == 0.0:
        return None
    gamma = (l2 - bb2 - slope * (l4 - l3)) / denominator
    if not math.isfinite(gamma) or gamma <= 0.0:
        return None
    distance = -10.0 * math.log10(gamma) / (alpha2 - alpha1)
    if not math.isfinite(distance) or distance < 0.0:
        return None
    return distance


def predict(data_dir: Path, slope_scale: float = 1.0) -> dict[str, list]:
    atm = load_atmosphere(data_dir)
    cols = band_columns(atm, list(BANDS_1BASED))
    lam = [atm["wavelengths_um"][c] for c in cols]
    alpha = [atm["attenuation_db_per_m"][c] for c in cols]
    t_air = float(atm["t_air_k"])
    bb1, bb2 = blackbody_microflick(lam[0], t_air), blackbody_microflick(lam[1], t_air)
    slope = slope_scale * sky_cue_slope(atm, *BANDS_1BASED)
    out: dict[str, list] = {}
    for split in SPLITS:
        for pid, pixels in load_split(data_dir, split):
            out[pid] = [
                estimate_distance(p[cols[0]], p[cols[1]], p[cols[2]], p[cols[3]], bb1, bb2, slope, alpha[0], alpha[1])
                for p in pixels
            ]
    return out


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--data-dir", default=str(ROOT / "data" / "lwir_scenes"))
    parser.add_argument("--output", default=str(ROOT / "outputs" / "quadspectral_predictions.json"))
    args = parser.parse_args()
    payload = {"method": "quadspectral", "patches": predict(Path(args.data_dir))}
    out = Path(args.output)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(payload) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
