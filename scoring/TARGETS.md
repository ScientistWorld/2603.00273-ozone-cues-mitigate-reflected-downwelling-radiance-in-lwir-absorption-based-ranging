# Targets

## quadspectral_patch_ranges

Primary target:
- Reduce `reflective_mean_abs_error_m` on the reflective checkerboard patches.

Constraint targets:
- Keep `tree_abs_error_m` low on the low-reflectance patch.
- Keep `invalid_fraction` at zero.
- Avoid unstable patch estimates, measured by `front_std_m`, `rear_std_m`,
  and `tree_std_m`.
- Reduce reflective error tails and systematic bias, measured by
  `reflective_median_abs_error_m`, `reflective_p90_abs_error_m`, and
  `reflective_abs_bias_m`.

Run `bash scripts/evaluate.sh` after writing one or more
`outputs/*_predictions.json` files in the documented prediction format.
