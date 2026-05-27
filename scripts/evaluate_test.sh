#!/bin/bash
# Held-out test-slice evaluation for the quadspectral ranging gym.
#
# Scores the same method keys found by the train-slice evaluator, using the
# held-out eval/test/ code path and writing only scoring/scores_test.json.

set -e

cd /home/user

mkdir -p scoring

python eval/test/evaluate.py \
  --outputs-dir outputs \
  --labels eval/test/quadspectral_test_labels.json \
  --method-source scoring/scores_train.json \
  --output scoring/scores_test.json
