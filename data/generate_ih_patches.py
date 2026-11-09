#!/usr/bin/env python3
"""Extract the real IHTest_202104 Path 5 Step 1 patches used as the real-scene check.

Reads three 8x8 patches (two calibration checkerboards and a tree, at the
crop coordinates of the paper's released figure script) from the public
collect1 LWIR cube and stores bands 1..N in the gym's patch-cube format
(data/lwir_scenes/real_*). Ground-truth ranges are not stored here.
"""

from __future__ import annotations

import argparse
import json
import re
import struct
from pathlib import Path

from lwir_physics import write_split

# (patch id, centre row, centre column in the 256-wide crop starting at column 901), 1-based
REAL_PATCHES = [
    ("ih_p5s1_a", 187, 86),
    ("ih_p5s1_b", 145, 18),
    ("ih_p5s1_c", 70, 160),
]
CROP_COL_START_1BASED = 901


def parse_envi_header(path: Path) -> dict[str, int]:
    text = path.read_text(encoding="utf-8")
    out: dict[str, int] = {}
    for key in ("samples", "lines", "bands", "data type", "header offset", "byte order"):
        match = re.search(rf"^{re.escape(key)}\s*=\s*([0-9]+)", text, flags=re.MULTILINE)
        if not match:
            raise ValueError(f"missing ENVI header field {key!r}")
        out[key] = int(match.group(1))
    interleave = re.search(r"^interleave\s*=\s*([A-Za-z]+)", text, flags=re.MULTILINE)
    if not interleave or interleave.group(1).upper() != "BSQ":
        raise ValueError("expected BSQ interleave")
    return out


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--hdr", default="data/downloads/ihdataset_path5_step1/IHTest_202104_Path5_Step1_LWHSI1_collect1_DistStA.hdr")
    parser.add_argument("--bsq", default="data/downloads/ihdataset_path5_step1/IHTest_202104_Path5_Step1_LWHSI1_collect1_DistStA.bsq")
    parser.add_argument("--atmosphere", default="data/lwir_scenes/atmosphere.json")
    parser.add_argument("--output-dir", default="data/lwir_scenes")
    parser.add_argument("--patch-size", type=int, default=8)
    args = parser.parse_args()

    meta = parse_envi_header(Path(args.hdr))
    samples, lines = meta["samples"], meta["lines"]
    if meta["data type"] != 4 or meta["byte order"] != 0 or meta["header offset"] != 0:
        raise ValueError("only little-endian float32 ENVI files without header offset are supported")
    bands = json.loads(Path(args.atmosphere).read_text(encoding="utf-8"))["band_index_1based"]
    half = args.patch_size // 2
    patches = []
    with Path(args.bsq).open("rb") as fh:
        for patch_id, centre_row, centre_col in REAL_PATCHES:
            col_full = CROP_COL_START_1BASED + centre_col - 1
            pixels = []
            for row in range(centre_row - half + 1, centre_row + half + 1):
                for col in range(col_full - half + 1, col_full + half + 1):
                    values = []
                    for band in bands:
                        fh.seek((((band - 1) * lines + (row - 1)) * samples + (col - 1)) * 4)
                        values.append(struct.unpack("<f", fh.read(4))[0])
                    pixels.append(values)
            patches.append((patch_id, pixels))
    write_split(
        args.output_dir,
        "real",
        patches,
        n_bands=len(bands),
        patch_size=args.patch_size,
        description="Real IHTest_202104 Path 5 Step 1 collect1 radiance (public raw cube), three 8x8 patches.",
    )


if __name__ == "__main__":
    main()
