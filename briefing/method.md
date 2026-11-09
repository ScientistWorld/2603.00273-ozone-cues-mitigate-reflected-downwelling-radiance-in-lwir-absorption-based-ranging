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

The slope `s` is the least-squares fit of the water-vapor difference on the
ozone difference across the downwelling spectra of the zenith-angle
dictionary in `data/lwir_scenes/atmosphere.json` (paper Eq. 21; authors'
Table I band pair, instrument bands 23/25 and 77/81). The reference
implementation is `method/ozone_cues/quadspectral.py` (standard library only);
the baseline is `baseline/bispectral.py`.

The paper also proposes a hyperspectral optimizer that uses many wavelengths,
smooth-emissivity regularization, optional total variation on range, and a
weighted set of downwelling spectra at different zenith angles. The paper
reports it to be more accurate than the quadspectral estimator because more
bands reduce the influence of noise and its assumptions are weaker. It is not
the reference here; the gym provides 96 bands and the downwelling dictionary
so that such multi-band methods can be built and scored.

## Main Claims

The primary claim is that accounting for reflected downwelling radiance greatly
reduces range overestimation on reflective LWIR targets. The constraint is that
the correction should not catastrophically break ordinary ranging on
low-reflectance objects.

The upstream author repository is cloned under `method/upstream/` (its
registered lidar map, the source of the real-scene ground truth, was removed
from the gym). It contains the authors' Python hyperspectral optimizer and
MATLAB quadspectral code.

## Known Limitations of the Reference (where headroom is)

- Per-pixel noise: four bands at ~1 microflick noise and a few kelvin of
  temperature contrast give pixel errors of tens of meters; spatial
  regularisation (the paper's TV term) or more bands reduce it.
- Closed-form approximations: Planck-function and emissivity differences
  between the four bands are neglected, leaving a systematic error even
  without noise (the paper notes a negative bias on the real scene).
- A single sky slope `s` for every surface orientation.
- The closed form has no solution for some pixels (null estimates).
