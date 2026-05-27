# Reproduction Milestones

**Current: core_claim**

<!-- Milestone levels (update "Current" above as you progress):
  none             — just started, no meaningful progress yet
  method_runs      — the paper's method executes end-to-end without errors
  core_claim       — minimum experiment supports the paper's central claim
  core_claim_plus  — core claim reproduced on additional settings
  secondary_claims — secondary results or contributions reproduced
  majority         — more than half of reported results reproduced
  near_complete    — most results reproduced, only minor gaps remain
  full             — all reported results reproduced
-->

## Progress Log

<!-- Write your progress here -->

### [2026-05-27 10:35] - none
- Started reproduction work and read the paper's measurement model, quadspectral estimator, hyperspectral estimator, and reported patch metrics.

### [2026-05-27 11:05] - method_runs
- Implemented the paper's quadspectral closed-form ozone correction and the air-aware bispectral baseline.
- Built scripts that run data generation, prediction, and evaluation end to end locally.

### [2026-05-27 11:20] - core_claim
- On a synthetic benchmark generated from the paper's radiative-transfer model, quadspectral ozone correction reduced reflective-patch MAE from 85.22 m to 5.92 m.
- Constraint metrics remained valid: tree MAE stayed low and invalid fraction was 0.0.

### [2026-05-27 11:32] - core_claim
- Scheduler job `ef89eced-1b5` completed the reproduction and `validate.py --compare` successfully.
- The job failed only after that because stale template commands in `scripts/run.sh` invoked missing `method/train.py`; those lines were removed before resubmission.

## Stop Justification
- Not stopped. Submitting a scheduler smoke job to verify the packaged CPU pipeline in-container.
