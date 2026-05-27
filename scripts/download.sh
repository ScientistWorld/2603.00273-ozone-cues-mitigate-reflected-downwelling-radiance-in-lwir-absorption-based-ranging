#!/bin/bash
# Download all data and models needed for this environment.
#
# Run on a node with internet access BEFORE building the container
# or submitting compute jobs.
#
# This script should be idempotent — safe to run multiple times.
# It should skip files that already exist.
#
# Update the storage estimate below as you add downloads.
#
# Estimated total download size: 0 GB
# Estimated disk usage after generation: <1 MB
#
# No external downloads are required for the current packaged benchmark.
# This script regenerates the small tracked-style synthetic radiance dataset
# used for the CPU quadspectral reproduction.

set -e

cd /home/user

python data/generate_synthetic.py --output data/synthetic/quadspectral_core.json
