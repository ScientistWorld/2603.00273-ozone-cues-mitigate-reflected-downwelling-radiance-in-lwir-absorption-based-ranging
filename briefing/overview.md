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
bispectral baseline on held-out targets simulated from the paper's
radiative-transfer model with the authors' released Path 5 Step 1 atmosphere
(attenuation and zenith-resolved downwelling spectra), and on three real
IHTest_202104 Path 5 Step 1 patches (two checkerboards, a tree).

## Key Results

- Paper Table I reports reflective checkerboard errors dropping from over 100 m
  with the bispectral baseline to paper-scale residual errors with the
  quadspectral correction.
- This gym shows the same effect: on 192 held-out simulated reflective
  targets the per-pixel error drops from 78 m (bispectral, which fails the
  gym's validity gate) to 21 m (quadspectral); on the real checkerboards from
  about 130 m to 18 m (raw public cube, not the authors' processed cube).
