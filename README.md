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
bispectral baseline on public IHTest_202104 Path 5 Step 1 LWIR HSI patches.

## Key Results

- Paper Table I reports reflective checkerboard errors dropping from over 100 m
  with the bispectral baseline to paper-scale residual errors with the
  quadspectral correction.
- This reproduction shows the same qualitative effect on a small real-data
  benchmark: reflective-patch error drops sharply relative to the bispectral
  baseline and the proposed-method primary metric is close to the paper's
  Table I value, though the raw public cube is not the authors' processed
  MATLAB cube.

---

# Problem Definition

## Research Question

Estimate object range from passive long-wave infrared spectral radiance in
natural outdoor scenes. The input is measured LWIR radiance at known wavelengths
plus scene-level atmospheric metadata such as attenuation coefficients and air
temperature. The output is range in meters for each spatial sample or patch.

The difficult regime is a reflective surface under open sky. Reflected ambient
thermal radiation can carry absorption structure unrelated to the
object-to-sensor path, causing ordinary absorption-based ranging to infer a
distance that is much too large.

## Why It Matters

Passive thermal ranging can work in darkness without active illumination,
texture, or stereo baselines. Robustness to reflected sky radiance is needed for
the method to be useful on real materials rather than only high-emissivity
surfaces.

## Success Criteria

A successful solution should reduce reflective-target range error while keeping
ordinary low-reflectance target estimates stable. It must estimate range from
the radiance measurements and atmospheric metadata, not from RGB texture, lidar,
or supervised fitting to the evaluation distances.

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

The paper also proposes a hyperspectral optimizer that uses many wavelengths,
smooth-emissivity regularization, optional total variation on range, and a
weighted set of downwelling spectra at different zenith angles. This
reproduction focuses on the quadspectral claim because it is the smallest
self-contained experiment that directly tests reflected-downwelling correction.

## Main Claims

The primary claim is that accounting for reflected downwelling radiance greatly
reduces range overestimation on reflective LWIR targets. The constraint is that
the correction should not catastrophically break ordinary ranging on
low-reflectance objects.

The upstream author repository is cloned under `method/upstream/`. It contains
the authors' Python hyperspectral optimizer and MATLAB quadspectral code. The
portable reproduction in `method/ozone_cues/` is a Python implementation of
the closed-form quadspectral equations used for the core experiment.

---

# Evaluation

## Metrics

Evaluation compares estimated ranges to ground-truth patch ranges. Following
the paper's quantitative protocol, metrics are computed over 8x8 patches and
reported as absolute error in meters plus the standard deviation of estimates
within each patch.

The primary metric is `reflective_mean_abs_error_m`, the mean absolute error
over the two reflective checkerboard patches. Lower is better. Constraint
metrics include absolute error on the low-reflectance tree patch, patch
standard deviations, and invalid estimate fraction.

## Baselines and Targets

The baseline is an air-aware bispectral range estimator that does not model
reflected radiance. The target method should substantially improve reflective
patch error relative to that baseline while keeping invalid estimates at zero
and avoiding severe degradation on the low-reflectance patch.

## Evaluation Protocol

The reusable evaluator reads prediction JSON files from `outputs/` and writes
`scoring/scores.json`. It does not import from `method/`. To compare methods
fairly, generate predictions for the same packaged patch dataset and keep the
wavelength, attenuation, air-temperature, and evaluation-label metadata fixed.

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


---

# Reproduction Milestones

**Current: core_claim**
