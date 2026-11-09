# Targets

## lwir_reflective_patch_ranges

Primary target:
- Reduce `reflective_mae_m` (per-pixel range error on reflective targets,
  held-out test). Reference: 21.3 m. The baseline that ignores reflected sky
  radiance fails the validity gate (ungated 78.2 m).

Secondary target:
- Reduce `reflective_patch_abs_error_m` (error of the patch-median range on
  reflective targets). Reference: 14.8 m.

Constraint targets:
- Reduce, or at least do not degrade, `ordinary_mae_m` (per-pixel error on
  low-reflectance targets). Reference: 19.9 m.
- Pass every validity gate: well-formed predictions for all 64 pixels of
  every train/test/real patch (null for no estimate, which costs 100 m), beat
  the best constant range guess on both target classes, and keep the
  reflective-target error on the real scene at or below 35 m (reference:
  17.9 m).

Run `bash scripts/evaluate.sh` (or `scripts/evaluate_train.sh`) after writing
`outputs/<name>_predictions.json` in the documented format.
