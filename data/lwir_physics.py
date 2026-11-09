"""Shared LWIR radiometry and data-access helpers for the patch-ranging gym.

Standard library only. Radiance unit is the microflick
(uW sr^-1 cm^-2 um^-1); attenuation is in dB/m; range is in meters.
"""

from __future__ import annotations

import array
import json
import math
import sys
from pathlib import Path

PLANCK_H = 6.63e-34
LIGHT_C = 3.0e8
BOLTZMANN_K = 1.38e-23

DEFAULT_DATA_DIR = Path(__file__).resolve().parent / "lwir_scenes"
SPLITS = ("train", "test", "real")


def blackbody_microflick(lambda_um: float, temperature_k: float) -> float:
    """Planck spectral radiance in microflicks."""
    lambda_m = lambda_um * 1e-6
    exponent = PLANCK_H * LIGHT_C / (lambda_m * BOLTZMANN_K * temperature_k)
    return 1e-4 * (2.0 * PLANCK_H * LIGHT_C**2 / lambda_m**5) / (math.exp(exponent) - 1.0)


def transmittance(alpha_db_per_m: float, distance_m: float) -> float:
    """Beer's-law transmittance for attenuation in dB/m."""
    return 10.0 ** (-alpha_db_per_m * distance_m / 10.0)


def load_atmosphere(data_dir: str | Path = DEFAULT_DATA_DIR) -> dict:
    """Scene metadata shared by every patch: bands, attenuation, air temperature, sky dictionary."""
    return json.loads((Path(data_dir) / "atmosphere.json").read_text(encoding="utf-8"))


def load_split(data_dir: str | Path, split: str) -> list[tuple[str, list[list[float]]]]:
    """Return [(patch_id, pixels)] for one split.

    ``pixels`` has ``patch_size**2`` rows in row-major order; each row holds
    the radiance of every band listed in ``atmosphere.json``.
    """
    data_dir = Path(data_dir)
    index = json.loads((data_dir / f"{split}_index.json").read_text(encoding="utf-8"))
    n_pix = int(index["patch_size"]) ** 2
    n_bands = int(index["n_bands"])
    raw = array.array("f")
    raw.frombytes((data_dir / index["radiance_file"]).read_bytes())
    if sys.byteorder == "big":
        raw.byteswap()
    if raw.itemsize != 4:
        raise RuntimeError("float32 array itemsize must be 4 bytes")
    expected = len(index["patch_ids"]) * n_pix * n_bands
    if len(raw) != expected:
        raise ValueError(f"{split}: radiance file has {len(raw)} values, expected {expected}")
    values = raw.tolist()
    patches = []
    stride = n_pix * n_bands
    for p, patch_id in enumerate(index["patch_ids"]):
        base = p * stride
        pixels = [values[base + i * n_bands : base + (i + 1) * n_bands] for i in range(n_pix)]
        patches.append((patch_id, pixels))
    return patches


def write_split(
    data_dir: str | Path,
    split: str,
    patches: list[tuple[str, list[list[float]]]],
    n_bands: int,
    patch_size: int = 8,
    description: str = "",
) -> None:
    """Write one split in the float32 patch-cube format read by ``load_split``."""
    data_dir = Path(data_dir)
    data_dir.mkdir(parents=True, exist_ok=True)
    raw = array.array("f")
    for _, pixels in patches:
        if len(pixels) != patch_size * patch_size:
            raise ValueError("wrong pixel count")
        for row in pixels:
            if len(row) != n_bands:
                raise ValueError("wrong band count")
            raw.extend(row)
    if sys.byteorder == "big":
        raw.byteswap()
    radiance_file = f"{split}_radiance.f32"
    (data_dir / radiance_file).write_bytes(raw.tobytes())
    index = {
        "split": split,
        "description": description,
        "radiance_file": radiance_file,
        "dtype": "float32",
        "byte_order": "little",
        "layout": "[patch][pixel row-major over patch_size x patch_size][band]",
        "patch_size": patch_size,
        "n_bands": n_bands,
        "patch_ids": [patch_id for patch_id, _ in patches],
    }
    (data_dir / f"{split}_index.json").write_text(json.dumps(index, indent=1) + "\n", encoding="utf-8")


def band_columns(atmosphere: dict, bands_1based: list[int]) -> list[int]:
    """Map 1-based instrument band numbers to columns of the stored radiance rows."""
    lookup = {int(b): i for i, b in enumerate(atmosphere["band_index_1based"])}
    return [lookup[int(b)] for b in bands_1based]
