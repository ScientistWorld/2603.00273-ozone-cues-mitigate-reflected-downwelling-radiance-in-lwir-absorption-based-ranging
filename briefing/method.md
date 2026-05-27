# Paper's Method

## Key Contribution

The paper introduces ozone-cue mitigation for reflected downwelling radiance in
LWIR absorption-based ranging. It uses spectral structure that appears strongly
in sky radiance but is negligible in ground-level horizontal propagation to
estimate and remove the reflected-radiance bias that makes reflective objects
look farther away.

## Approach

The implemented core method is the closed-form quadspectral estimator from
Section IV. It uses two bands around a water-vapor absorption feature and two
bands around the 9.5 um ozone feature. The air-aware bispectral baseline
computes range from the ratio of air-centered radiances at the water-vapor
pair. The quadspectral estimator additionally estimates the reflected
downwelling bias as `s * (L(lambda4) - L(lambda3))`, where `s` is the modeled
linear relation between water-vapor and ozone downwelling differences, and
subtracts this bias before applying the Beer-law closed form.

The paper also proposes a hyperspectral optimizer that uses many wavelengths,
smooth-emissivity regularization, optional total variation on range, and a
weighted set of downwelling spectra at different zenith angles. This
reproduction focuses on the quadspectral claim because it is the smallest
self-contained experiment that directly tests reflected-downwelling correction.

## Main Claims

The primary claim is that accounting for reflected downwelling radiance greatly
reduces range overestimation on reflective LWIR targets. The constraint is that
the correction should not catastrophically break ordinary ranging on
low-reflectance objects.

The upstream author repository is cloned under `method/upstream/`. It contains
the authors' Python hyperspectral optimizer and MATLAB quadspectral code. The
portable reproduction in `method/ozone_cues/` is a Python implementation of
the closed-form quadspectral equations used for the core experiment.
