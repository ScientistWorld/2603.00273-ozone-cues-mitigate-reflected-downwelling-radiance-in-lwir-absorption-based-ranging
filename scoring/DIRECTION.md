# Research Direction

## Research Problem

Improve passive LWIR absorption-based range estimation in outdoor scenes where
reflected ambient thermal radiance (especially downwelling sky radiance) can
make reflective surfaces appear much farther away than they are, while keeping
ordinary low-reflectance content accurate, under low temperature contrast and
realistic sensor noise.

## Approach Scope

In-scope improvements operate on the LWIR spectral radiance and the physical
metadata: better radiative-transfer modelling of emitted and reflected
radiance, better use of spectral cues across the 96 provided bands, joint
estimation of range with temperature/emissivity/sky contributions, robust or
regularised inversion (including spatial priors within a patch), handling of
pixels where an estimator has no valid solution, and uncertainty handling.

## Out of Bounds

Supervised fitting to labelled ranges (train labels included), non-LWIR
modalities, hard-coded or per-patch ranges, external scene priors that bypass
the radiance problem, and changes to the benchmark data, labels or evaluators.
