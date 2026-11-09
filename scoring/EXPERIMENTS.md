# Experiments

## lwir_reflective_patch_ranges

Establishes whether a passive LWIR ranging method stays accurate on
reflective surfaces under open sky, where reflected sky radiance otherwise
makes targets appear far too distant, without degrading ordinary
low-reflectance targets.

- Scored on 288 held-out 8x8 target patches (two thirds reflective) that the
  method has not seen labelled, drawn from the same distribution as the 144
  labelled train targets: one atmosphere (the measured IHTest_202104 Path 5
  Step 1 conditions), unknown target temperature, emissivity spectrum and sky
  exposure, ranges from tens to about two hundred meters, realistic sensor
  noise.
- Metrics: per-pixel range error on reflective targets (primary), patch-level
  error on reflective targets, and per-pixel error on ordinary targets.
- Validity: malformed or non-physical predictions, or doing no better than a
  constant range guess on either target class, fail the run. The held-out
  test also requires reflective-target error on a real LWIR scene (two real
  checkerboard panels) to stay below 35 m, so a method must transfer to real
  measurements, not only to the held-out targets.
