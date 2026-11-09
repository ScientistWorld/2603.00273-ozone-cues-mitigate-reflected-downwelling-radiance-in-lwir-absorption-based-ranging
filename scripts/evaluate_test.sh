#!/bin/bash
# Held-out test evaluation: scores every outputs/*_predictions.json on the
# hidden simulated targets plus the real-scene check. No arguments.

set -e
cd /home/user
mkdir -p scoring
python eval/test/evaluate.py --outputs-dir outputs --output scoring/scores_test.json
