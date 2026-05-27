# Problem Definition

## Research Question

Estimate object range from passive long-wave infrared spectral radiance in
natural outdoor scenes. The input is measured LWIR radiance at known wavelengths
plus scene-level atmospheric metadata such as attenuation coefficients and air
temperature. The output is range in meters for each spatial sample or patch.

The difficult regime is a reflective surface under open sky. Reflected ambient
thermal radiation can carry absorption structure unrelated to the
object-to-sensor path, causing ordinary absorption-based ranging to infer a
distance that is much too large.

## Why It Matters

Passive thermal ranging can work in darkness without active illumination,
texture, or stereo baselines. Robustness to reflected sky radiance is needed for
the method to be useful on real materials rather than only high-emissivity
surfaces.

## Success Criteria

A successful solution should reduce reflective-target range error while keeping
ordinary low-reflectance target estimates stable. It must estimate range from
the radiance measurements and atmospheric metadata, not from RGB texture, lidar,
or supervised fitting to the evaluation distances.
