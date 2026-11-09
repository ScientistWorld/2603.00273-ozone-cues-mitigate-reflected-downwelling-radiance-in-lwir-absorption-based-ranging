# Scientist Constraints

Use the provided LWIR radiance (`data/lwir_scenes/*_radiance.f32`) and the
fixed metadata in `data/lwir_scenes/atmosphere.json` (band wavelengths,
attenuation, air temperature, downwelling sky dictionary, nominal noise).

Methods may change the range estimator in any way, but every estimate must be
inferred from the radiance and that metadata, by the same procedure for every
patch of every split.

- Do not use labels to fit the estimator. `eval/train/train_labels.json` is
  for scoring and comparing method variants only: do not train regressors,
  nearest-neighbour lookups, calibration offsets/scales or range priors on it.
- Do not hard-code, look up or special-case ranges for particular patches or
  patch ids (including the real-scene patches, whose ranges are published
  elsewhere), and do not use the patch id or split membership as an input.
- Do not use other modalities (RGB, lidar, external imagery) or external
  range data, and do not read or modify anything under `eval/test/`.
- Do not edit the data, labels or evaluators; evaluate through
  `scripts/evaluate.sh`, `scripts/evaluate_train.sh` or
  `scripts/evaluate_test.sh`.

## Compliance Checklist

- [ ] Predictions are produced only from the packaged LWIR radiance and fixed
  metadata, with one procedure for all patches.
- [ ] Train labels are used only to score/compare variants, never as fitting
  targets.
- [ ] No per-patch hard-coded ranges, no use of patch ids or split names.
- [ ] No RGB, lidar, external images or additional labelled range data.
- [ ] Evaluation is run through the provided scripts without modifying
  labels or evaluator code.
