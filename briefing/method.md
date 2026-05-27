# Paper's Method

How the paper approaches the problem, i.e. the paper's core contributions.

## Key Contribution

<!-- What is the paper's main contribution? -->

## Approach

<!-- How does the paper solve the problem? Key ideas, architecture, algorithm. -->

## Main Claims

<!-- What are the paper's central claims? Which are primary vs. secondary? -->
The paper introduces ozone-cue mitigation for reflected downwelling radiance in
LWIR absorption-based ranging.

The implemented core method is the quadspectral estimator from Sec. IV. It uses
two bands around a water-vapor absorption feature and two bands around the
9.5 um ozone feature. The baseline air-aware bispectral estimator computes a
range from the ratio of air-centered radiances at the water-vapor pair. The
quadspectral estimator additionally estimates the reflected-downwelling bias as
`s * (L(lambda4) - L(lambda3))`, where `s` is the simulated linear relation
between water-vapor and ozone downwelling differences, and subtracts this bias
before applying the Beer-law closed form.

The upstream author repository is cloned under `method/upstream/`. It contains
the authors' Python hyperspectral optimizer and MATLAB quadspectral code. The
reproduction code in `method/ozone_cues/` is a Python implementation of the
closed-form quadspectral equations used for the core claim.
