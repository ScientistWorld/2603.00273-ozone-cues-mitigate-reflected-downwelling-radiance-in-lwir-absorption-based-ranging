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
