#!/usr/bin/env python3
"""Three independently seeded executions of the actual reference entry point."""
import random
import runpy
import sys

seed = int(sys.argv[1])
random.seed(seed)
sys.argv = ["method/ozone_cues/quadspectral.py"]
runpy.run_path("method/ozone_cues/quadspectral.py", run_name="__main__")
