# Reproduction Milestones

**Current: core_claim**

## Progress Log

### [2026-05-27 10:41] - method_runs
- Implemented the Section IV air-aware bispectral baseline and quadspectral ozone-cue estimator.
- Packaged public IHTest_202104 four-band patch extraction, prediction, and evaluation scripts.

### [2026-05-27 10:55] - core_claim
- Ran the end-to-end pipeline on real public IHTest Path 5 Step 1 LWIR patches.
- Reproduced the paper's central quadspectral effect: reflective-patch error drops sharply relative to the bispectral baseline, with the proposed-method primary metric close to the paper's Table I value.
