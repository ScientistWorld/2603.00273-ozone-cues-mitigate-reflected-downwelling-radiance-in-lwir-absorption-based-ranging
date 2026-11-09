#!/bin/bash
# Job entry point: reproduce the reference end to end (baseline + proposed
# method + development-split scoring), score the train and held-out test
# slices, and validate the workspace.
# The hardening audit is separate: bash redteam/hardening/run_audit.sh
set -e
cd /home/user

bash scripts/reproduce.sh
bash scripts/evaluate_train.sh
bash scripts/evaluate_test.sh
python validate.py --compare --post-reproducer
