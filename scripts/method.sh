#!/bin/bash
# Run the paper's proposed method (closed-form quadspectral ozone-cue ranging).
#
# Usage:
#   bash scripts/method.sh
# Writes outputs/quadspectral_predictions.json for every train, test and real patch.

set -e
cd /home/user
mkdir -p outputs
python method/ozone_cues/quadspectral.py --data-dir data/lwir_scenes --output outputs/quadspectral_predictions.json
