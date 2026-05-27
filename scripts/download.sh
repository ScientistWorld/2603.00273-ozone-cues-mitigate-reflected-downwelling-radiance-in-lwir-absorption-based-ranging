#!/bin/bash
# Download all data and models needed for this environment.
#
# Run on a node with internet access BEFORE building the container
# or submitting compute jobs.
#
# This script should be idempotent — safe to run multiple times.
# It should skip files that already exist.
#
# Update the storage estimate below as you add downloads.
#
# Estimated total download size: 0.43 GB
# Estimated disk usage after generation: 0.43 GB
#
# This script downloads the public IHTest_202104 Path 5 Step 1 LWIR HSI
# collect used by the paper's released example, then extracts the three
# Table I 8x8 patch measurements used by this benchmark.

set -e

cd /home/user

mkdir -p data/downloads/ihdataset_path5_step1
base_url="https://ihdataset-01.s3.us-east-2.amazonaws.com/IHTest_202104_DistStA/Path5_DistStA/Path5_Step1_DistStA"
hdr="data/downloads/ihdataset_path5_step1/IHTest_202104_Path5_Step1_LWHSI1_collect1_DistStA.hdr"
bsq="data/downloads/ihdataset_path5_step1/IHTest_202104_Path5_Step1_LWHSI1_collect1_DistStA.bsq"

[ -e "$hdr" ] || curl -L -o "$hdr" "$base_url/IHTest_202104_Path5_Step1_LWHSI1_collect1_DistStA.hdr"
[ -e "$bsq" ] || curl -L -o "$bsq" "$base_url/IHTest_202104_Path5_Step1_LWHSI1_collect1_DistStA.bsq"

python data/generate_ih_patches.py --hdr "$hdr" --bsq "$bsq" \
  --output data/synthetic/lwir_patch_core.json \
  --labels-output eval/lwir_patch_labels.json
