#!/bin/bash
set -euo pipefail
cd /home/user
for trial in reference_seed0 reference_seed1 reference_seed2 \
  better_smooth1 better_smooth2 better_patch_pool weaker_no_sky brute_force_physics \
  label_leak_shortcut constant40_shortcut short_length_shortcut \
  null_filter10_shortcut null_filter25_shortcut null_filter50_shortcut \
  score_forgery_shortcut baseline_move_shortcut zero_shortcut empty_shortcut \
  nan_shortcut infinity_shortcut; do
    bash "redteam/$trial/run.sh"
done
python redteam/summarize.py
