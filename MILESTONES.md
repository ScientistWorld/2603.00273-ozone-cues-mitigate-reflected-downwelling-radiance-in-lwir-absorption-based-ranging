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

### [2026-05-27 11:15] - core_claim
- Replaced the synthetic core benchmark with public IHTest_202104 Path 5 Step 1
  raw LWIR HSI patches extracted from the paper's released crop, band, and
  patch-center settings.
- The reproduced quadspectral method reduces reflective-patch MAE from
  139.00 m for the bispectral baseline to 34.63 m on the real patch subset.
- `scripts/reproduce.sh` and `python validate.py --compare` pass locally.

## Stop Justification
- Not stopped. The core claim is reproduced on a real public-data patch subset;
  higher milestones would require reproducing the authors' processed
  hyperspectral cube calibration or the full hyperspectral optimizer.
