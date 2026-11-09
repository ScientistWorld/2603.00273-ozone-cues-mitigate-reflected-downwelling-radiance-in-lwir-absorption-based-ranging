#!/bin/bash
# Download all public inputs for this environment (run on a node with internet).
#
# Idempotent: every fetch is skipped when its file already exists.
#
# Estimated total download size: 0.43 GB
# Estimated disk usage after generation: 0.45 GB
#
# 1. Public IHTest_202104 Path 5 Step 1 LWIR hyperspectral cube (collect1),
#    DARPA Invisible Headlights dataset (AWS open data).
# 2. The paper authors' released atmosphere assets for that scene
#    (band centres, SpectralCalc attenuation, zenith-resolved downwelling).
# 3. Derived gym inputs under data/lwir_scenes/ (atmosphere.json and the
#    real-scene patches). These are committed; they are rebuilt here only
#    if missing. The simulated train/test target sets are committed data.

set -e

cd /home/user

mkdir -p data/downloads/ihdataset_path5_step1
base_url="https://ihdataset-01.s3.us-east-2.amazonaws.com/IHTest_202104_DistStA/Path5_DistStA/Path5_Step1_DistStA"
hdr="data/downloads/ihdataset_path5_step1/IHTest_202104_Path5_Step1_LWHSI1_collect1_DistStA.hdr"
bsq="data/downloads/ihdataset_path5_step1/IHTest_202104_Path5_Step1_LWHSI1_collect1_DistStA.bsq"
[ -e "$hdr" ] || curl -L --fail -o "$hdr" "$base_url/IHTest_202104_Path5_Step1_LWHSI1_collect1_DistStA.hdr"
[ -e "$bsq" ] || curl -L --fail -o "$bsq" "$base_url/IHTest_202104_Path5_Step1_LWHSI1_collect1_DistStA.bsq"

mkdir -p data/downloads/ozone_cues_assets
assets_url="https://raw.githubusercontent.com/unaydorken/Ozone-Cues-Mitigate-Reflected-Downwelling-Radiance-in-LWIR-Absorption-Based-Ranging/main/data"
for f in lambda.mat attenuation.mat I_downwelling_res.mat; do
  [ -e "data/downloads/ozone_cues_assets/$f" ] || curl -L --fail -o "data/downloads/ozone_cues_assets/$f" "$assets_url/$f"
done

[ -e data/lwir_scenes/atmosphere.json ] || python data/build_atmosphere.py \
  --assets data/downloads/ozone_cues_assets --output data/lwir_scenes/atmosphere.json
[ -e data/lwir_scenes/real_index.json ] || python data/generate_ih_patches.py \
  --hdr "$hdr" --bsq "$bsq" --atmosphere data/lwir_scenes/atmosphere.json --output-dir data/lwir_scenes
