#!/bin/bash
# Train-slice evaluation for the LWIR patch-ranging gym.
#
# Mirrors scripts/evaluate.sh: read method prediction artifacts from outputs/
# and write a scoring JSON without importing or running method code.

set -e

cd /home/user

mkdir -p scoring

python eval/train/evaluate.py \
  --outputs-dir outputs \
  --labels eval/train/lwir_patch_train_labels.json \
  --output scoring/scores_train.json
