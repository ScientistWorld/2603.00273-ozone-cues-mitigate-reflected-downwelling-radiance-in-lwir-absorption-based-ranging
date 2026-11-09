#!/usr/bin/env python3
"""Build data/lwir_scenes/atmosphere.json from the authors' released assets.

Inputs are the public Path 5 Step 1 files from the paper's code release
(fetched by scripts/download.sh into data/downloads/ozone_cues_assets/):
  lambda.mat            raw instrument band centres (um)
  attenuation.mat       SpectralCalc/HITRAN2020 attenuation (dB/m) for the
                        on-site weather, on the -0.12 um calibrated grid
  I_downwelling_res.mat downwelling sky radiance (microflick) at ten zenith angles
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from matfile import load_mat

N_BANDS = 96  # instrument bands 1..96 (about 7.98-9.86 um after calibration)
WAVELENGTH_SHIFT_UM = -0.12
T_AIR_K = 289.7
ZENITH_DEG = [0, 30, 60, 70, 80, 82, 84, 86, 88, 89]
NOMINAL_NOISE_MICROFLICK = 1.0


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--assets", default="data/downloads/ozone_cues_assets")
    parser.add_argument("--output", default="data/lwir_scenes/atmosphere.json")
    args = parser.parse_args()
    assets = Path(args.assets)

    _, lam = load_mat(assets / "lambda.mat")["lambda"]
    _, att = load_mat(assets / "attenuation.mat")["attenuation"]
    (n_dw_bands, n_angles), dw = load_mat(assets / "I_downwelling_res.mat")["I_downwelling_res"]
    if n_angles != len(ZENITH_DEG):
        raise ValueError("unexpected number of downwelling zenith angles")

    bands = list(range(1, N_BANDS + 1))
    payload = {
        "description": (
            "Atmospheric metadata for IHTest_202104 Path 5 Step 1 (on-site weather), shared by every "
            "patch in this gym. Radiance in microflicks (uW sr^-1 cm^-2 um^-1)."
        ),
        "source": "https://github.com/unaydorken/Ozone-Cues-Mitigate-Reflected-Downwelling-Radiance-in-LWIR-Absorption-Based-Ranging (data/)",
        "band_index_1based": bands,
        "wavelengths_um": [round(lam[b - 1] + WAVELENGTH_SHIFT_UM, 9) for b in bands],
        "attenuation_db_per_m": [att[b - 1] for b in bands],
        "t_air_k": T_AIR_K,
        "nominal_noise_microflick": NOMINAL_NOISE_MICROFLICK,
        "downwelling_zenith_deg": ZENITH_DEG,
        "downwelling_microflick": [
            [dw[(b - 1) + q * n_dw_bands] for q in range(n_angles)] for b in bands
        ],
    }
    out = Path(args.output)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(payload, indent=1) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
