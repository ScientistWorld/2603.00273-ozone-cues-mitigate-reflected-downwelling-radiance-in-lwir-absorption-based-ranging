#!/bin/bash
set -e
cd /home/user

bash scripts/reproduce.sh
python validate.py --compare
