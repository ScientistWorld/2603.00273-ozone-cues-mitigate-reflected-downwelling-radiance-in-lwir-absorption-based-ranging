# Reproduction Milestones

**Current: core_claim**

## Progress Log

### [2026-05-27 10:23] - method_runs
- Implemented the closed-form quadspectral ozone-cue estimator and air-aware
  bispectral baseline.
- Packaged synthetic four-band LWIR patches generated from the paper's
  radiative-transfer model.
- Scheduler validation ran the end-to-end reproduction and `validate.py
  --compare` successfully.

### [2026-05-27 10:30] - core_claim
- Replaced the synthetic core benchmark with public IHTest_202104 Path 5 Step 1
  raw LWIR HSI patches extracted from the paper's released crop, band, and
  patch-center settings.
- The reproduced quadspectral method reduces reflective-patch MAE from
  139.00 m for the bispectral baseline to 11.83 m on the real patch subset.
- `scripts/reproduce.sh` and `python validate.py --compare` pass locally.

### [2026-05-27 10:36] - core_claim
- Scheduler job `f031ddb2-f53` reran the packaged reproduction in the container
  and exited with code 0.
- The job reproduced the then-current real-patch scores and passed all
  validation checks.

### [2026-05-27 10:45] - core_claim
- Restored the packaged public IHTest subset to raw `collect1` and replaced
  the rough ozone/water correction constant with the band-pair coefficient
  derived from the paper's released downwelling dictionary.
- `scripts/reproduce.sh`, `python validate.py --compare`, and
  `python validate.py` pass locally with quadspectral reflective MAE of
  11.83 m.

## Stop Justification
- Completed at milestone `core_claim`.
