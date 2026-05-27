#!/usr/bin/env python3
from __future__ import annotations

import argparse

from ozone_lwir import write_synthetic_dataset


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", default="data/synthetic/quadspectral_core.json")
    parser.add_argument("--seed", type=int, default=7)
    args = parser.parse_args()
    write_synthetic_dataset(args.output, seed=args.seed)


if __name__ == "__main__":
    main()

