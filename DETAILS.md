# Overview

- **Paper ID:** 2603.00273
- **Title:** Ozone Cues Mitigate Reflected Downwelling Radiance in LWIR Absorption-Based Ranging
- **Domain:** Computational imaging / thermal remote sensing
- **TL;DR:** The paper uses ozone absorption structure in reflected sky radiance to correct passive LWIR range overestimates on reflective objects.

## Short Summary

Passive LWIR absorption-based ranging estimates depth from spectral
attenuation, but reflective surfaces can mirror downwelling sky radiance and
produce large overestimates. The paper proposes a closed-form four-band
estimator and a richer hyperspectral optimizer that explicitly account for
reflected downwelling radiance. The packaged reproduction implements the
closed-form quadspectral estimator and compares it against the air-aware
bispectral baseline on held-out targets simulated from the paper's
radiative-transfer model with the authors' released Path 5 Step 1 atmosphere
(attenuation and zenith-resolved downwelling spectra), and on three real
IHTest_202104 Path 5 Step 1 patches (two checkerboards, a tree).

## Key Results

- Paper Table I reports reflective checkerboard errors dropping from over 100 m
  with the bispectral baseline to paper-scale residual errors with the
  quadspectral correction.
- This gym shows the same effect: on 192 held-out simulated reflective
  targets the per-pixel error drops from 78 m (bispectral, which fails the
  gym's validity gate) to 21 m (quadspectral); on the real checkerboards from
  about 130 m to 18 m (raw public cube, not the authors' processed cube).

---

# Problem Definition

## Research Question

Estimate object range from passive long-wave infrared (LWIR) spectral
radiance in natural outdoor scenes. Range information comes from atmospheric
absorption: radiance from an object is attenuated along the horizontal path
to the sensor in a wavelength-dependent way (Beer's law with known
attenuation coefficients), while the air along the path adds its own thermal
emission. The input is measured spectral radiance per pixel plus scene-level
atmospheric metadata; the output is a range in meters for every pixel.

The difficult regime is a reflective surface under open sky. A surface with
emissivity below one also reflects ambient thermal radiation, including
downwelling radiance from the sky. Sky radiance has travelled through a long
atmospheric column and carries strong absorption/emission structure of its
own, so a ranging method that treats all spectral structure as path
absorption can infer a range that is far too large on such surfaces. Ordinary
(high-emissivity, low-reflectance) content such as vegetation must keep being
ranged correctly. Object temperatures are close to the air temperature (a few
kelvin), so the range signal is weak relative to sensor noise.

## Data

All inputs live in `data/lwir_scenes/`:

- `atmosphere.json`: shared metadata for every patch: 96 instrument bands
  (centre wavelengths, already calibrated), ground-level attenuation per band
  (dB/m) for the on-site weather, air temperature (K), the nominal sensor
  noise (microflick), and a dictionary of downwelling sky radiance spectra at
  ten zenith angles (0-89 deg) computed for this atmosphere.
- `{train,test,real}_index.json` + `*_radiance.f32`: 8x8-pixel target
  patches, radiance in microflicks (uW sr^-1 cm^-2 um^-1), little-endian
  float32, layout `[patch][pixel row-major][band]`. Use
  `data/lwir_physics.py:load_split` to read them.
  - `train`: 144 labelled targets (labels in `eval/train/train_labels.json`).
  - `test`: 288 unlabelled targets, scored by the hidden evaluator.
  - `real`: three patches from a real LWIR hyperspectral image
    (IHTest_202104 Path 5 Step 1), unlabelled, scored by the hidden evaluator.

Train and test targets are drawn from the same distribution: a mix of
reflective panels and ordinary low-reflectance targets, each patch covering a
single object at a nearly constant range (tens to a couple of hundred
meters), seen under the same atmosphere, with unknown temperature, unknown
spectral emissivity and unknown sky exposure.

## Why It Matters

Passive thermal ranging works in darkness without illumination, texture or a
stereo baseline. It is only useful on real materials if it is robust to
reflected sky radiance.

## Success Criteria

Lower range error on reflective targets, without degrading ordinary targets,
on unseen targets and on the real scene. Range must be inferred from the
radiance and the provided metadata, not from labels, other modalities or
patch identity.

---

# Paper's Method

## Key Contribution

The paper introduces ozone-cue mitigation for reflected downwelling radiance in
LWIR absorption-based ranging. It uses spectral structure that appears strongly
in sky radiance but is negligible in ground-level horizontal propagation to
estimate and remove the reflected-radiance bias that makes reflective objects
look farther away.

## Approach

The implemented core method is the closed-form quadspectral estimator from
Section IV. It uses two bands around a water-vapor absorption feature and two
bands around the 9.5 um ozone feature. The air-aware bispectral baseline
computes range from the ratio of air-centered radiances at the water-vapor
pair. The quadspectral estimator additionally estimates the reflected
downwelling bias as `s * (L(lambda4) - L(lambda3))`, where `s` is the modeled
linear relation between water-vapor and ozone downwelling differences, and
subtracts this bias before applying the Beer-law closed form.

The slope `s` is the least-squares fit of the water-vapor difference on the
ozone difference across the downwelling spectra of the zenith-angle
dictionary in `data/lwir_scenes/atmosphere.json` (paper Eq. 21; authors'
Table I band pair, instrument bands 23/25 and 77/81). The reference
implementation is `method/ozone_cues/quadspectral.py` (standard library only);
the baseline is `baseline/bispectral.py`.

The paper also proposes a hyperspectral optimizer that uses many wavelengths,
smooth-emissivity regularization, optional total variation on range, and a
weighted set of downwelling spectra at different zenith angles. The paper
reports it to be more accurate than the quadspectral estimator because more
bands reduce the influence of noise and its assumptions are weaker. It is not
the reference here; the gym provides 96 bands and the downwelling dictionary
so that such multi-band methods can be built and scored.

## Main Claims

The primary claim is that accounting for reflected downwelling radiance greatly
reduces range overestimation on reflective LWIR targets. The constraint is that
the correction should not catastrophically break ordinary ranging on
low-reflectance objects.

The upstream author repository is cloned under `method/upstream/` (its
registered lidar map, the source of the real-scene ground truth, was removed
from the gym). It contains the authors' Python hyperspectral optimizer and
MATLAB quadspectral code.

## Known Limitations of the Reference (where headroom is)

- Per-pixel noise: four bands at ~1 microflick noise and a few kelvin of
  temperature contrast give pixel errors of tens of meters; spatial
  regularisation (the paper's TV term) or more bands reduce it.
- Closed-form approximations: Planck-function and emissivity differences
  between the four bands are neglected, leaving a systematic error even
  without noise (the paper notes a negative bias on the real scene).
- A single sky slope `s` for every surface orientation.
- The closed form has no solution for some pixels (null estimates).

---

# Evaluation

## Prediction Format

Write one file per method, `outputs/<method_name>_predictions.json`:

```json
{"method": "<method_name>",
 "patches": {"<patch_id>": [64 range estimates in meters, row-major, or null], ...}}
```

Include every patch id of the `train`, `test` and `real` splits. Each list
must have exactly 64 entries; an entry is a finite, non-negative number or
`null` (no estimate). The method key in the score files is the file-name
stem. Nothing else in the file is read.

## Metrics (all in meters, lower is better)

Per-pixel absolute errors are clipped at 100 m; a `null` costs 100 m.

| Metric | Coefficient | Meaning |
|---|---:|---|
| `reflective_mae_m` (primary) | 1.0 | mean per-pixel error over reflective targets |
| `reflective_patch_abs_error_m` | 0.5 | mean over reflective targets of the error of the patch's median estimate (systematic error after averaging noise) |
| `ordinary_mae_m` | 0.5 | mean per-pixel error over low-reflectance targets |

## Validity Gates

A run is scored as failed (all three metrics set to 100 m) if:

- the prediction file is malformed: a required patch is missing, a list does
  not have 64 entries, or an entry is non-numeric, NaN/Infinity or negative;
- on either target class (reflective, ordinary) its per-pixel MAE is not
  lower than the MAE of the best constant range guess for that class;
- (held-out test only) on the two reflective patches of the real scene its
  per-pixel MAE is above 35 m.

Failure reasons and unscored diagnostics (patch standard deviations, null
fractions, real-scene errors, the ungated metric values) are written under
`_diagnostics` in the score files.

## Scripts

- `bash scripts/evaluate_train.sh` -> `scoring/scores_train.json` (labelled
  train targets; same metrics and gates except the real-scene gate).
- `bash scripts/evaluate.sh` -> `scoring/scores.json` (same as train).
- `bash scripts/evaluate_test.sh` -> `scoring/scores_test.json` (hidden test:
  held-out targets plus the real-scene check). Not available to methods.

Each script scores every `outputs/*_predictions.json`; none of them runs or
imports method code.

## Reference Comparison

The provided baseline ignores reflected sky radiance and fails the
reflective-target gate (its ungated reflective MAE is about 78 m on test).
The reference method reaches about 21 m reflective MAE on the held-out test.
Ranking is relative to the reference's held-out test scores.

---

# Reproduction Log

### Iteration 1: gpt-5.5
- **Milestone**: `core_claim` | **Status**: done
- **Working time**: 11m | **GPU**: 0.0h
- **Jobs**: 2 total (1 completed, 1 failed)

<details>
<summary>Progress Log</summary>

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

### [2026-05-27 11:38] - core_claim
- Scheduler retry job `2d92bd6f-811` exited with code 0.
- The packaged CPU reproduction passed `scripts/reproduce.sh`, `validate.py --compare`, import-separation checks, and eval-output checks inside the compute container.

</details>

### Iteration 2: gpt-5.5
- **Milestone**: `core_claim` | **Status**: done
- **Working time**: 13m | **GPU**: 0.0h
- **Jobs**: 3 total (2 completed, 1 failed)

<details>
<summary>Progress Log</summary>

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
  139.00 m for the bispectral baseline to 34.63 m on the real patch subset.
- `scripts/reproduce.sh` and `python validate.py --compare` pass locally.

### [2026-05-27 10:36] - core_claim
- Scheduler job `f031ddb2-f53` reran the packaged reproduction in the container
  and exited with code 0.
- The job reproduced the real-patch scores and passed all validation checks.

</details>

### Iteration 3: gpt-5.5
- **Milestone**: `core_claim` | **Status**: done
- **Working time**: 8m | **GPU**: 0.0h
- **Jobs**: 4 total (3 completed, 1 failed)

<details>
<summary>Progress Log</summary>

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

</details>

### Iteration 4: gpt-5.5 (designer_stage_1)
- **Milestone**: `core_claim` | **Status**: done
- **Working time**: 5m | **GPU**: 0.0h
- **Jobs**: 4 total (3 completed, 1 failed)

<details>
<summary>Progress Log</summary>

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

</details>

### Iteration 5: gpt-5.5 (designer_stage_2)
- **Milestone**: `core_claim` | **Status**: done
- **Working time**: 4m | **GPU**: 0.0h
- **Jobs**: 4 total (3 completed, 1 failed)

<details>
<summary>Progress Log</summary>

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

</details>

### Iteration 6: gpt-5.5 (designer_stage_3)
- **Milestone**: `core_claim` | **Status**: done
- **Working time**: 3m | **GPU**: 0.0h
- **Jobs**: 5 total (4 completed, 1 failed)

<details>
<summary>Progress Log</summary>

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

</details>

### Iteration 7: gpt-5.5 (packager)
- **Milestone**: `core_claim` | **Status**: done
- **Working time**: 1m | **GPU**: 0.0h
- **Jobs**: 5 total (4 completed, 1 failed)

<details>
<summary>Progress Log</summary>

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

</details>

### Iteration 8: gpt-5.5 (verifier)
- **Milestone**: `core_claim` | **Status**: done
- **Working time**: 5m | **GPU**: 0.0h
- **Jobs**: 5 total (4 completed, 1 failed)

<details>
<summary>Progress Log</summary>

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

### [2026-05-27 11:13] - core_claim
- Final verification confirmed the latest CPU test job and local validation pass.
- Main evaluator now discovers arbitrary prediction files, and method-safe scoring guidance has been cleaned up for future scientist agents.

</details>

### Iteration 9: gpt-5.5 (verifier)
- **Milestone**: `core_claim` | **Status**: done
- **Working time**: 11m | **GPU**: 0.0h
- **Jobs**: 5 total (4 completed, 1 failed)

<details>
<summary>Progress Log</summary>

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

### [2026-05-27 11:13] - core_claim
- Final verification confirmed the latest CPU test job and local validation pass.
- Main evaluator now discovers arbitrary prediction files, and method-safe scoring guidance has been cleaned up for future scientist agents.

### [2026-05-27 11:16] - core_claim
- Re-ran the full local reproduction entrypoint, including train/test scoring and post-reproducer validation.
- Confirmed the existing scheduler-verified environment remains valid for the paper's Table I quadspectral core claim.

### [2026-05-27 11:20] - core_claim
- Final verification renamed public experiment/data/evaluator paths to method-neutral LWIR patch-ranging terms.
- Verified download URLs, reran `scripts/run.sh`, and passed `python validate.py --compare --post-reproducer`.

</details>

### Iteration 10: gpt-6.1-sol (redteam)
- **Milestone**: `core_claim` | **Status**: done
- **Working time**: 8m | **GPU**: 0.0h

<details>
<summary>Progress Log</summary>

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

### [2026-05-27 11:13] - core_claim
- Final verification confirmed the latest CPU test job and local validation pass.
- Main evaluator now discovers arbitrary prediction files, and method-safe scoring guidance has been cleaned up for future scientist agents.

### [2026-05-27 11:16] - core_claim
- Re-ran the full local reproduction entrypoint, including train/test scoring and post-reproducer validation.
- Confirmed the existing scheduler-verified environment remains valid for the paper's Table I quadspectral core claim.

### [2026-05-27 11:20] - core_claim
- Final verification renamed public experiment/data/evaluator paths to method-neutral LWIR patch-ranging terms.
- Verified download URLs, reran `scripts/run.sh`, and passed `python validate.py --compare --post-reproducer`.

</details>

### Iteration 11: claude-opus-5-5 (hardener)
- **Milestone**: `core_claim` | **Status**: done
- **Working time**: 31m | **GPU**: 0.0h
- **Jobs**: 1 total (1 completed, 0 failed)

<details>
<summary>Progress Log</summary>

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

### [2026-05-27 11:13] - core_claim
- Final verification confirmed the latest CPU test job and local validation pass.
- Main evaluator now discovers arbitrary prediction files, and method-safe scoring guidance has been cleaned up for future scientist agents.

### [2026-05-27 11:16] - core_claim
- Re-ran the full local reproduction entrypoint, including train/test scoring and post-reproducer validation.
- Confirmed the existing scheduler-verified environment remains valid for the paper's Table I quadspectral core claim.

### [2026-05-27 11:20] - core_claim
- Final verification renamed public experiment/data/evaluator paths to method-neutral LWIR patch-ranging terms.
- Verified download URLs, reran `scripts/run.sh`, and passed `python validate.py --compare --post-reproducer`.

### [2026-11-09] - core_claim
- Hardening (iteration 11): hidden simulated held-out test from the paper's radiative-transfer model and the authors' Path 5 Step 1 atmosphere, strict evaluator with validity gates, real-scene transfer gate; reference reproduces the paper's direction (reflective MAE 78.2 m bispectral, ungated, vs 21.3 m quadspectral). Container job 37ffc6db-e58 verified. See HARDENING.md.

</details>


---

# Reproduction Milestones

**Current: core_claim**
