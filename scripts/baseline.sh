#!/bin/bash
# Run the paper's comparison baseline: air-aware bispectral ranging that
# ignores reflected downwelling radiance (paper Eq. 14).
#
# Usage:
#   bash scripts/baseline.sh
# Writes outputs/bispectral_predictions.json for every train, test and real patch.

set -e
cd /home/user
mkdir -p outputs
python baseline/bispectral.py --data-dir data/lwir_scenes --output outputs/bispectral_predictions.json
