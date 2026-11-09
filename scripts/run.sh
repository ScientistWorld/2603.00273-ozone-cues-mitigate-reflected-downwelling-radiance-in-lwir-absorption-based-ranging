#!/bin/bash
# Job entry point: reproduce the reference, score train and held-out test,
# validate. (This iteration also runs the hardening audit.)
set -e
cd /home/user

bash scripts/reproduce.sh
bash scripts/evaluate_train.sh
bash scripts/evaluate_test.sh
bash redteam/hardening/run_audit.sh
python validate.py --compare --post-reproducer
