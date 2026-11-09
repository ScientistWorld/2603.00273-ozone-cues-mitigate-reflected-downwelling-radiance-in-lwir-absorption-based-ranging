#!/bin/bash
# Evaluation script: scores every outputs/*_predictions.json on the labelled
# development (train) targets and writes scoring/scores.json.
#
# Self-contained in eval/; never imports method/. Any method that writes the
# documented prediction format (see briefing/evaluation.md) can be scored.
#
# Usage:
#   bash scripts/evaluate.sh

set -e
cd /home/user
mkdir -p scoring
python eval/train/evaluate.py --outputs-dir outputs --labels eval/train/train_labels.json --output scoring/scores.json
