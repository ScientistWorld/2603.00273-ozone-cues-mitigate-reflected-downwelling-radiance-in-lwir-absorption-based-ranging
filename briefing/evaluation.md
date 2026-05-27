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
