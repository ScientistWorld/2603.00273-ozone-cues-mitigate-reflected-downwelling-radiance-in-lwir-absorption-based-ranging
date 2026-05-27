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
bispectral baseline on a portable radiative-transfer benchmark.

## Key Results

- Paper Table I reports reflective checkerboard errors dropping from over 100 m
  with the bispectral baseline to paper-scale residual errors with the
  quadspectral correction.
- This reproduction shows the same qualitative effect on a small benchmark:
  reflective-patch error drops sharply while invalid estimates remain zero.
