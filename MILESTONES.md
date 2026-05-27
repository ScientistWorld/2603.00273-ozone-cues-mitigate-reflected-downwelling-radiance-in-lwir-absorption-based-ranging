# Reproduction Milestones

**Current: core_claim**

## Progress Log

### [2026-05-27 10:41] - method_runs
- Implemented the Section IV air-aware bispectral baseline and quadspectral ozone-cue estimator.
- Packaged public IHTest_202104 four-band patch extraction, prediction, and evaluation scripts.

### [2026-05-27 10:55] - core_claim
- Ran the end-to-end pipeline on real public IHTest Path 5 Step 1 LWIR patches.
- Reproduced the paper's central quadspectral effect: reflective-patch error drops sharply relative to the bispectral baseline, with the proposed-method primary metric close to the paper's Table I value.

### [2026-05-27 10:48] - core_claim
- Audited the continued workspace after milestone reset and confirmed the implementation uses the paper's closed-form quadspectral ozone-cue computation rather than a surrogate.
- Confirmed evaluation reads method outputs independently, does not import from `method/`, and reproduces the reflective-patch error reduction on the packaged public IHTest patch benchmark.

### [2026-05-27 10:51] - core_claim
- CPU scheduler job `669d3422-e57` exited with code 0 in the Apptainer environment.
- The job reran `scripts/run.sh`, regenerated scores, and passed `python validate.py --compare --post-reproducer` with the same reflective-patch core-claim result.

### [2026-05-27 11:10] - core_claim
- Tightened the default job entrypoint so `scripts/run.sh` runs the full reproduction, train/test slice scoring, and post-reproducer validation.
- Expanded the main evaluator to report all declared reflective-error summary metrics in `scoring/scores.json`.
