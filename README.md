# Overview

- **Paper ID:** <!-- e.g. 1706.03762 -->
- **Title:** <!-- e.g. Attention Is All You Need -->
- **Domain:** <!-- e.g. Computer Vision / Object Detection -->
- **TL;DR:** <!-- One sentence: what this paper does and why it matters -->

## Short Summary

<!-- 3-5 sentences covering the problem, approach, and main findings -->

## Key Results

<!-- 2-3 bullet points: main findings or numbers in bullet points -->
This paper studies passive LWIR range estimation in scenes where reflective
surfaces mirror downwelling sky radiance. Ordinary absorption-based ranging can
interpret those reflected absorption features as a much longer object-to-camera
path, producing large overestimates.

The reproduction implements the paper's quadspectral ozone-cue correction. On a
small radiative-transfer benchmark generated from the paper's measurement model,
the ozone correction substantially reduces reflective-patch range error compared
with the air-aware bispectral baseline.

---

# Problem Definition

What problem does this paper address? Write this so that someone with no knowledge of the paper can understand what needs to be solved and how success is measured.

Do NOT describe the paper's method or solution here — only the problem itself. Think about if a future scientist agent try to solve this problem from scratch without knowing what approach the paper took. If you leak the solution, you compromise the benchmark.

## Research Question

<!-- What problem or challenge does this paper tackle? What gap in existing work does it address? -->

## Why It Matters

<!-- Why is this problem important? What would a good solution enable? Make it short -->

## Success Criteria

<!-- What would a successful solution look like? What properties should it have? This is about the goal, not the paper's specific approach. Make it short -->
Estimate passive long-wave infrared range from spectral radiance measurements.
The input is radiance measured at LWIR wavelengths, known atmospheric
attenuation coefficients, and air temperature. The output is object range in
meters for each spatial sample or patch.

The difficult case is a reflective natural-scene object under open sky.
Reflected downwelling sky radiance carries atmospheric absorption structure and
can make ordinary absorption-based ranging overestimate distance. A valid
solution must estimate range from the radiance physics rather than from RGB
texture, lidar, or learned scene priors.

---

# Paper's Method

How the paper approaches the problem, i.e. the paper's core contributions.

## Key Contribution

<!-- What is the paper's main contribution? -->

## Approach

<!-- How does the paper solve the problem? Key ideas, architecture, algorithm. -->

## Main Claims

<!-- What are the paper's central claims? Which are primary vs. secondary? -->
The paper introduces ozone-cue mitigation for reflected downwelling radiance in
LWIR absorption-based ranging.

The implemented core method is the quadspectral estimator from Sec. IV. It uses
two bands around a water-vapor absorption feature and two bands around the
9.5 um ozone feature. The baseline air-aware bispectral estimator computes a
range from the ratio of air-centered radiances at the water-vapor pair. The
quadspectral estimator additionally estimates the reflected-downwelling bias as
`s * (L(lambda4) - L(lambda3))`, where `s` is the simulated linear relation
between water-vapor and ozone downwelling differences, and subtracts this bias
before applying the Beer-law closed form.

The upstream author repository is cloned under `method/upstream/`. It contains
the authors' Python hyperspectral optimizer and MATLAB quadspectral code. The
reproduction code in `method/ozone_cues/` is a Python implementation of the
closed-form quadspectral equations used for the core claim.

---

# Evaluation

How success is measured. Describe only the metrics, targets, and evaluation procedure — do NOT describe the paper's method or how they achieved these results. Think of this as a general evaluation protocal for other scientists trying to solve the same problem, where they should not see this paper's solution.

## Metrics

<!-- What metrics are used? How are they computed? What does higher/lower mean? -->

## Baselines and Targets

<!-- What performance levels exist as reference points? Include the paper's reported numbers as targets, and any standard baselines. A scientist agent should know what "good" looks like. -->

## Evaluation Protocol

<!-- How should evaluation be run? What data split, what conditions? Any important details about how to compare fairly (e.g., fixed seeds, specific test sets, averaging over runs). -->
Evaluation compares estimated ranges to ground-truth patch ranges. Following
the paper's quantitative protocol, metrics are computed over 8x8 patches and
reported as absolute error in meters plus the standard deviation of estimates
within each patch.

The primary metric is mean absolute error on reflective checkerboard patches,
because these are where reflected downwelling radiance causes the failure mode.
The low-reflectance tree patch is a constraint metric: a method should not gain
on reflective surfaces by destroying ordinary air-aware absorption ranging on
surfaces with little downwelling reflection. Invalid estimates are also counted.

The reusable evaluator reads prediction JSON files from `outputs/` and writes
`scoring/scores.json`. It does not import from `method/`.

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


---

# Reproduction Milestones

**Current: core_claim**

## Stop Justification
- Completed at milestone `core_claim`.
