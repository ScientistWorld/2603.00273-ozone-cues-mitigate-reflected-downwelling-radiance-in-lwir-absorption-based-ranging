#!/bin/bash
# Run the paper's proposed method.
#
# This script trains/runs the paper's method using code in method/.
#
# Usage:
#   bash scripts/method.sh

set -e

cd /home/user

mkdir -p outputs
if [ ! -f data/synthetic/quadspectral_core.json ]; then
  python data/generate_ih_patches.py \
    --output data/synthetic/quadspectral_core.json \
    --labels-output eval/quadspectral_core_labels.json
fi
python method/ozone_cues/quadspectral.py \
  --data data/synthetic/quadspectral_core.json \
  --output outputs/quadspectral_predictions.json
