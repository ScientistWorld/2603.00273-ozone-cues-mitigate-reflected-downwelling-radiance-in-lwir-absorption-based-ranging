#!/bin/bash
set -euo pipefail
cd /home/user
for trial in better_patch_tls better_local_tls1 better_local_tls2 better_estimate_smooth1; do
    bash "redteam/$trial/run.sh"
done
python redteam/summarize.py
