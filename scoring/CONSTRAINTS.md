# Scientist Constraints

Use the provided four-band LWIR radiance dataset and the same fixed wavelength,
attenuation, air-temperature, and evaluation-label metadata.

Methods may change the range estimator, but prediction must use only the
provided radiance measurements and metadata. Do not use the ground-truth patch
distances during prediction. Do not replace the task with RGB, lidar, scene
labels, external imagery, or supervised fitting to the evaluation distances.

## Compliance Checklist

- [ ] Predictions are produced only from the packaged LWIR radiance data and
  fixed metadata.
- [ ] Ground-truth patch distances are used only by evaluation code.
- [ ] No RGB, lidar, scene labels, external images, or additional labeled range
  data are used during prediction.
- [ ] Evaluation is run through `scripts/evaluate.sh`,
  `scripts/evaluate_train.sh`, or `scripts/evaluate_test.sh` without modifying
  the labels.
