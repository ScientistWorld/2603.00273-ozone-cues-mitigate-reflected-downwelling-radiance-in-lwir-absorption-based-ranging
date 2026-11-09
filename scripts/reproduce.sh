#!/bin/bash
# Reproduce the reference end to end: baseline, proposed method, evaluation.
#
# Assumes scripts/download.sh has been run (the committed data/lwir_scenes/
# inputs are enough; the raw cube is only needed to rebuild them).

set -e
cd /home/user

for f in atmosphere.json train_index.json test_index.json real_index.json; do
  if [ ! -f "data/lwir_scenes/$f" ]; then
    echo "Missing data/lwir_scenes/$f. Run scripts/download.sh on an internet-enabled node first." >&2
    exit 1
  fi
done

bash scripts/baseline.sh
bash scripts/method.sh
bash scripts/evaluate.sh
