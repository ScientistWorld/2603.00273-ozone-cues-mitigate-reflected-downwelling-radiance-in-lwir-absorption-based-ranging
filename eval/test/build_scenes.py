#!/usr/bin/env python3
"""Generate the gym's simulated target sets (hidden generator; run once at packaging).

Writes radiance-only inputs to data/lwir_scenes/{train,test}_* (visible),
train labels to eval/train/train_labels.json (visible) and held-out test
labels to eval/test/test_labels.json (hidden). The key below seeds every
random draw; without it the held-out labels cannot be regenerated.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import random
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(ROOT / "data"))

from lwir_physics import write_split  # noqa: E402
from scene_simulator import simulate_patch  # noqa: E402

SECRET_KEY = "REDACTED"
SPLIT_SIZES = {"train": {"reflective": 96, "ordinary": 48}, "test": {"reflective": 192, "ordinary": 96}}


def build(split: str, atm: dict):
    rng = random.Random(f"{SECRET_KEY}:{split}")
    order = [c for c, n in SPLIT_SIZES[split].items() for _ in range(n)]
    rng.shuffle(order)
    patches, labels = [], {}
    prefix = "tr" if split == "train" else "te"
    for idx, cls in enumerate(order):
        pid = prefix + "_" + hashlib.sha256(f"{SECRET_KEY}:{split}:{idx}".encode()).hexdigest()[:10]
        pixels, distances, info = simulate_patch(rng, cls, atm)
        patches.append((pid, pixels))
        labels[pid] = {"class": cls, "distance_m": distances, **({"nuisance": info} if split == "test" else {})}
    patches.sort(key=lambda item: item[0])
    return patches, labels


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--data-dir", default=str(ROOT / "data" / "lwir_scenes"))
    parser.add_argument("--train-labels", default=str(ROOT / "eval" / "train" / "train_labels.json"))
    parser.add_argument("--test-labels", default=str(HERE / "test_labels.json"))
    parser.add_argument("--force", action="store_true")
    args = parser.parse_args()
    data_dir = Path(args.data_dir)
    outputs = [data_dir / "train_index.json", data_dir / "test_index.json", Path(args.train_labels), Path(args.test_labels)]
    if not args.force and all(p.is_file() for p in outputs):
        print("simulated target sets already present; use --force to rebuild")
        return
    atm = json.loads((data_dir / "atmosphere.json").read_text(encoding="utf-8"))
    for split, label_path in (("train", Path(args.train_labels)), ("test", Path(args.test_labels))):
        patches, labels = build(split, atm)
        write_split(
            data_dir,
            split,
            patches,
            n_bands=len(atm["band_index_1based"]),
            description=f"Simulated LWIR targets ({split}); radiance only, labels are held by the evaluator.",
        )
        label_path.write_text(
            json.dumps({"split": split, "patch_size": 8, "patches": labels}, separators=(",", ":")) + "\n",
            encoding="utf-8",
        )
        print(split, len(patches), "patches")


if __name__ == "__main__":
    main()
