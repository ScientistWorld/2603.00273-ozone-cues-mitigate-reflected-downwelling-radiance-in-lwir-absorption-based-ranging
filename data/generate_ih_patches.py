#!/usr/bin/env python3
"""Extract the paper's Path 5 Step 1 quadspectral patches from public IH data."""

from __future__ import annotations

import argparse
import json
import math
import re
import struct
from pathlib import Path

from ozone_lwir import ATTENUATION_DB_PER_M, OZONE_WATER_SLOPE, T_AIR_K


PATCHES = [
    {
        "name": "front_checkerboard",
        "type": "reflective",
        "center_row": 187,
        "center_col": 86,
        "distance_m": 31.01,
    },
    {
        "name": "rear_checkerboard",
        "type": "reflective",
        "center_row": 145,
        "center_col": 18,
        "distance_m": 46.51,
    },
    {
        "name": "tree",
        "type": "low_reflectance",
        "center_row": 70,
        "center_col": 160,
        "distance_m": 57.84,
    },
]

# MATLAB figure script settings from the paper's released code:
# measurements = measurements(1:256, 901:1156, 1:247)
# pair_index = 5 -> water/clear bands 23/25 and ozone/clear bands 77/81.
CROP_COL_START_1BASED = 901
BAND_INDICES_1BASED = [23, 25, 77, 81]
WAVELENGTH_SHIFT_UM = -0.12


def parse_envi_header(path: Path) -> dict[str, object]:
    text = path.read_text(encoding="utf-8")
    out: dict[str, object] = {}
    for key in ("samples", "lines", "bands", "data type", "header offset", "byte order"):
        match = re.search(rf"^{re.escape(key)}\s*=\s*([0-9]+)", text, flags=re.MULTILINE)
        if not match:
            raise ValueError(f"missing ENVI header field {key!r}")
        out[key] = int(match.group(1))
    interleave = re.search(r"^interleave\s*=\s*([A-Za-z]+)", text, flags=re.MULTILINE)
    if not interleave or interleave.group(1).upper() != "BSQ":
        raise ValueError("expected BSQ interleave")
    wavelengths_match = re.search(r"wavelength\s*=\s*\{([^}]*)\}", text, flags=re.DOTALL)
    if not wavelengths_match:
        raise ValueError("missing wavelength list")
    out["wavelength"] = [
        float(x)
        for x in re.findall(r"[-+]?(?:\d+\.\d*|\.\d+|\d+)(?:[Ee][-+]?\d+)?", wavelengths_match.group(1))
    ]
    return out


def read_float32_pixel(fh, band0: int, row0: int, col0: int, lines: int, samples: int) -> float:
    offset = ((band0 * lines + row0) * samples + col0) * 4
    fh.seek(offset)
    raw = fh.read(4)
    if len(raw) != 4:
        raise ValueError("unexpected EOF while reading BSQ pixel")
    value = struct.unpack("<f", raw)[0]
    if not math.isfinite(value):
        raise ValueError("non-finite radiance in BSQ file")
    return value


def extract_dataset(hdr: Path, bsq: Path, output: Path, labels_output: Path, patch_size: int) -> None:
    meta = parse_envi_header(hdr)
    samples = int(meta["samples"])
    lines = int(meta["lines"])
    bands = int(meta["bands"])
    if int(meta["data type"]) != 4 or int(meta["byte order"]) != 0:
        raise ValueError("only little-endian float32 ENVI files are supported")
    expected_size = samples * lines * bands * 4
    if bsq.stat().st_size != expected_size:
        raise ValueError(f"unexpected BSQ size: got {bsq.stat().st_size}, expected {expected_size}")

    wavelengths = meta["wavelength"]
    selected_bands0 = [idx - 1 for idx in BAND_INDICES_1BASED]
    selected_wavelengths = [
        round(float(wavelengths[band]) + WAVELENGTH_SHIFT_UM, 6) for band in selected_bands0
    ]

    half = patch_size // 2
    patches = []
    labels = []
    with bsq.open("rb") as fh:
        for patch in PATCHES:
            center_row = int(patch["center_row"])
            center_col_crop = int(patch["center_col"])
            center_col_full = CROP_COL_START_1BASED + center_col_crop - 1
            pixels = []
            for row_1based in range(center_row - half + 1, center_row + half + 1):
                for col_1based in range(center_col_full - half + 1, center_col_full + half + 1):
                    row0 = row_1based - 1
                    col0 = col_1based - 1
                    pixels.append(
                        [
                            read_float32_pixel(fh, band0, row0, col0, lines, samples)
                            for band0 in selected_bands0
                        ]
                    )
            patches.append(
                {
                    "name": patch["name"],
                    "type": patch["type"],
                    "source_center_crop_row_col": [center_row, center_col_crop],
                    "measurements": pixels,
                }
            )
            labels.append(
                {
                    "name": patch["name"],
                    "type": patch["type"],
                    "distance_m": patch["distance_m"],
                }
            )

    payload = {
        "description": "Four-band 8x8 patches extracted from public IHTest_202104 Path 5 Step 1 LWIR HSI collect1 using the paper's released MATLAB coordinates.",
        "source": "s3://ihdataset-01/IHTest_202104_DistStA/Path5_DistStA/Path5_Step1_DistStA/",
        "wavelengths_um": selected_wavelengths,
        "attenuation_db_per_m": ATTENUATION_DB_PER_M,
        "t_air_k": T_AIR_K,
        "ozone_water_slope": OZONE_WATER_SLOPE,
        "patch_size": patch_size,
        "bands_1based": BAND_INDICES_1BASED,
        "patches": patches,
    }
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    labels_output.parent.mkdir(parents=True, exist_ok=True)
    labels_output.write_text(
        json.dumps(
            {
                "description": "Patch labels from the paper's Table I lidar ground-truth distances.",
                "patches": labels,
            },
            indent=2,
        )
        + "\n",
        encoding="utf-8",
    )


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--hdr", default="data/downloads/ihdataset_path5_step1/IHTest_202104_Path5_Step1_LWHSI1_collect1_DistStA.hdr")
    parser.add_argument("--bsq", default="data/downloads/ihdataset_path5_step1/IHTest_202104_Path5_Step1_LWHSI1_collect1_DistStA.bsq")
    parser.add_argument("--output", default="data/synthetic/quadspectral_core.json")
    parser.add_argument("--labels-output", default="eval/quadspectral_core_labels.json")
    parser.add_argument("--patch-size", type=int, default=8)
    args = parser.parse_args()
    extract_dataset(Path(args.hdr), Path(args.bsq), Path(args.output), Path(args.labels_output), args.patch_size)


if __name__ == "__main__":
    main()
