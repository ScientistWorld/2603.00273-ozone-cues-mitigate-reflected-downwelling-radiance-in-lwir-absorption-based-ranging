#!/usr/bin/env python3
"""Closed-form quadspectral ozone-cue ranging from Sec. IV of the paper."""

from __future__ import annotations

import argparse
import json
import math
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parents[2] / "data"))
from ozone_lwir import blackbody_microflick  # noqa: E402


def estimate_distance(
    measurements: list[float],
    wavelengths_um: list[float],
    attenuation_db_per_m: list[float],
    t_air_k: float,
    ozone_water_slope: float,
) -> float | None:
    if len(measurements) != 4 or len(wavelengths_um) != 4 or len(attenuation_db_per_m) != 4:
        raise ValueError("quadspectral estimation requires exactly four bands")
    l1, l2, l3, l4 = measurements
    bb1 = blackbody_microflick(wavelengths_um[0], t_air_k)
    bb2 = blackbody_microflick(wavelengths_um[1], t_air_k)
    correction = ozone_water_slope * (l4 - l3)
    denominator = l1 - bb1
    if denominator == 0.0:
        return None
    gamma = (l2 - bb2 - correction) / denominator
    if gamma <= 0.0 or not math.isfinite(gamma):
        return None
    alpha1, alpha2 = attenuation_db_per_m[0], attenuation_db_per_m[1]
    if abs(alpha2 - alpha1) < 1.0e-12:
        raise ValueError("water-vapor band attenuations must be distinct")
    distance = -10.0 * math.log10(gamma) / (alpha2 - alpha1)
    if distance < 0.0 or not math.isfinite(distance):
        return None
    return distance


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--data", default="data/synthetic/quadspectral_core.json")
    parser.add_argument("--output", default="outputs/quadspectral_predictions.json")
    args = parser.parse_args()

    data = json.loads(Path(args.data).read_text(encoding="utf-8"))
    if data["attenuation_db_per_m"][0] <= data["attenuation_db_per_m"][1]:
        raise ValueError("expected band 1 to be the stronger water-vapor absorption band")
    if max(data["attenuation_db_per_m"][1:]) / min(data["attenuation_db_per_m"][1:]) > 2.0:
        raise ValueError("expected bands 2-4 to have similar near-transparent ground attenuation")
    results = {"method": "quadspectral", "patches": []}
    for patch in data["patches"]:
        estimates = [
            estimate_distance(
                pixel,
                data["wavelengths_um"],
                data["attenuation_db_per_m"],
                data["t_air_k"],
                data["ozone_water_slope"],
            )
            for pixel in patch["measurements"]
        ]
        results["patches"].append(
            {
                "name": patch["name"],
                "estimates_m": estimates,
            }
        )

    output = Path(args.output)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(results, indent=2) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
