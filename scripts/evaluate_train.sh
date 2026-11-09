#!/bin/bash
# Train-slice evaluation: scores every outputs/*_predictions.json on the
# labelled training targets. No arguments.

set -e
cd /home/user
mkdir -p scoring
python eval/train/evaluate.py --outputs-dir outputs --labels eval/train/train_labels.json --output scoring/scores_train.json
