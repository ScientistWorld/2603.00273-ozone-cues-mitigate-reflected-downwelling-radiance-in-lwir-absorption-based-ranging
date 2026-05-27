"""Shared LWIR radiative-transfer utilities for the ozone-cue ranging gym."""

from __future__ import annotations

import json
import math
import random
from pathlib import Path


WAVELENGTHS_UM = [8.42, 8.46, 9.49, 9.57]
ATTENUATION_DB_PER_M = [8.0e-3, 2.98e-4, 3.98e-4, 3.31e-4]
T_AIR_K = 289.7
# Absolute regression coefficient for the paper's Figure_bispectral_results.m
# pair_index=5, derived from method/upstream/data/I_downwelling_res.mat.
OZONE_WATER_SLOPE = 0.7977227816102535
# The portable benchmark includes a small scene/calibration mismatch so the
# closed-form estimator is tested under paper-scale measurement residuals.
SYNTHETIC_REFLECTION_SLOPE = 0.86


def blackbody_microflick(lambda_um: float, temperature_k: float) -> float:
    """Planck radiance in the microflick units used by the paper."""
    lambda_m = lambda_um * 1e-6
    h = 6.63e-34
    c = 3.0e8
    k_b = 1.38e-23
    exponent = h * c / (lambda_m * k_b * temperature_k)
    return 1e-4 * (2.0 * h * c**2 / lambda_m**5) / (math.exp(exponent) - 1.0)


def transmittance(alpha_db_per_m: float, distance_m: float) -> float:
    return 10.0 ** (-alpha_db_per_m * distance_m / 10.0)


def observed_radiance(
    distance_m: float,
    temperature_k: float,
    emissivity: float,
    reflected_radiance: list[float],
    noise_std: float,
    rng: random.Random,
) -> list[float]:
    """Evaluate Eq. (7) from the paper at the four quadspectral bands."""
    values = []
    for lambda_um, alpha, reflected in zip(
        WAVELENGTHS_UM, ATTENUATION_DB_PER_M, reflected_radiance
    ):
        tau = transmittance(alpha, distance_m)
        obj = emissivity * blackbody_microflick(lambda_um, temperature_k)
        air = blackbody_microflick(lambda_um, T_AIR_K)
        radiance = tau * (obj + reflected - air) + air
        values.append(radiance + rng.gauss(0.0, noise_std))
    return values


def patch_reflection(
    base: float,
    ozone_difference: float,
    slope: float = OZONE_WATER_SLOPE,
) -> list[float]:
    """Construct downwelling reflection with the paper's linear ozone cue."""
    return [
        base,
        base + slope * ozone_difference,
        base + 20.0,
        base + 20.0 + ozone_difference,
    ]


def write_synthetic_dataset(path: str | Path, seed: int = 7, patch_size: int = 8) -> None:
    """Create a small benchmark with reflective and low-reflectance patches.

    The generated measurements are not copied paper data; they are produced
    from the same radiative-transfer model and ozone/water-vapor correction
    assumption used in the paper. This keeps the environment portable while
    preserving the computation needed to test the quadspectral method.
    """
    rng = random.Random(seed)
    patches = [
        {
            "name": "front_checkerboard",
            "type": "reflective",
            "distance_m": 25.0,
            "temperature_k": 300.0,
            "emissivity": 0.85,
            "ozone_difference": 20.0,
            "noise_std": 0.35,
        },
        {
            "name": "rear_checkerboard",
            "type": "reflective",
            "distance_m": 45.0,
            "temperature_k": 300.0,
            "emissivity": 0.85,
            "ozone_difference": 20.0,
            "noise_std": 0.35,
        },
        {
            "name": "tree",
            "type": "low_reflectance",
            "distance_m": 58.0,
            "temperature_k": 300.0,
            "emissivity": 0.92,
            "ozone_difference": 0.0,
            "noise_std": 0.35,
        },
    ]

    label_patches = []
    for patch in patches:
        reflected = patch_reflection(
            80.0,
            patch["ozone_difference"],
            SYNTHETIC_REFLECTION_SLOPE,
        )
        pixels = []
        for _ in range(patch_size * patch_size):
            d = patch["distance_m"] + rng.gauss(0.0, 0.25)
            t = patch["temperature_k"] + rng.gauss(0.0, 0.2)
            eps = max(0.0, min(1.0, patch["emissivity"] + rng.gauss(0.0, 0.004)))
            pixels.append(
                observed_radiance(d, t, eps, reflected, patch["noise_std"], rng)
            )
        label_patches.append(
            {
                "name": patch["name"],
                "type": patch["type"],
                "distance_m": patch["distance_m"],
            }
        )
        for key in ("distance_m", "temperature_k", "emissivity", "ozone_difference", "noise_std"):
            del patch[key]
        patch["measurements"] = pixels

    payload = {
        "description": "Synthetic four-band LWIR radiance patches generated from the paper's Eq. (7).",
        "wavelengths_um": WAVELENGTHS_UM,
        "attenuation_db_per_m": ATTENUATION_DB_PER_M,
        "t_air_k": T_AIR_K,
        "ozone_water_slope": OZONE_WATER_SLOPE,
        "synthetic_reflection_slope": SYNTHETIC_REFLECTION_SLOPE,
        "patch_size": patch_size,
        "patches": patches,
    }
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")

    labels_path = path.with_name(path.stem + "_labels.json")
    labels_payload = {
        "description": "Evaluation labels for the synthetic four-band LWIR patch benchmark.",
        "patches": label_patches,
    }
    labels_path.write_text(json.dumps(labels_payload, indent=2) + "\n", encoding="utf-8")
