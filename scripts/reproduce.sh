#!/bin/bash
# Reproduce the paper's results end-to-end.
#
# This script runs inside the compute container and calls scripts/baseline.sh,
# scripts/method.sh, and scripts/evaluate.sh.
#
# Assumes:
#   - Container is built (environment/container.sif)
#   - Data and models are downloaded (via scripts/download.sh)
#   - Working directory is /home/user
#
# This is the "gold standard" reproduction — 
# You do not need to run this, but keep this in good shape
# so other agents can easily run a full loop of reproduction and get the paper's numbers.

set -e

cd /home/user

if [ ! -f data/synthetic/lwir_patch_core.json ]; then
  echo "Missing data/synthetic/lwir_patch_core.json. Run scripts/download.sh on an internet-enabled login node before submitting compute jobs." >&2
  exit 1
fi

bash scripts/baseline.sh
bash scripts/method.sh
bash scripts/evaluate.sh
