# Problem Definition

## Research Question

Estimate object range from passive long-wave infrared (LWIR) spectral
radiance in natural outdoor scenes. Range information comes from atmospheric
absorption: radiance from an object is attenuated along the horizontal path
to the sensor in a wavelength-dependent way (Beer's law with known
attenuation coefficients), while the air along the path adds its own thermal
emission. The input is measured spectral radiance per pixel plus scene-level
atmospheric metadata; the output is a range in meters for every pixel.

The difficult regime is a reflective surface under open sky. A surface with
emissivity below one also reflects ambient thermal radiation, including
downwelling radiance from the sky. Sky radiance has travelled through a long
atmospheric column and carries strong absorption/emission structure of its
own, so a ranging method that treats all spectral structure as path
absorption can infer a range that is far too large on such surfaces. Ordinary
(high-emissivity, low-reflectance) content such as vegetation must keep being
ranged correctly. Object temperatures are close to the air temperature (a few
kelvin), so the range signal is weak relative to sensor noise.

## Data

All inputs live in `data/lwir_scenes/`:

- `atmosphere.json`: shared metadata for every patch: 96 instrument bands
  (centre wavelengths, already calibrated), ground-level attenuation per band
  (dB/m) for the on-site weather, air temperature (K), the nominal sensor
  noise (microflick), and a dictionary of downwelling sky radiance spectra at
  ten zenith angles (0-89 deg) computed for this atmosphere.
- `{train,test,real}_index.json` + `*_radiance.f32`: 8x8-pixel target
  patches, radiance in microflicks (uW sr^-1 cm^-2 um^-1), little-endian
  float32, layout `[patch][pixel row-major][band]`. Use
  `data/lwir_physics.py:load_split` to read them.
  - `train`: 144 labelled targets (labels in `eval/train/train_labels.json`).
  - `test`: 288 unlabelled targets, scored by the hidden evaluator.
  - `real`: three patches from a real LWIR hyperspectral image
    (IHTest_202104 Path 5 Step 1), unlabelled, scored by the hidden evaluator.

Train and test targets are drawn from the same distribution: a mix of
reflective panels and ordinary low-reflectance targets, each patch covering a
single object at a nearly constant range (tens to a couple of hundred
meters), seen under the same atmosphere, with unknown temperature, unknown
spectral emissivity and unknown sky exposure.

## Why It Matters

Passive thermal ranging works in darkness without illumination, texture or a
stereo baseline. It is only useful on real materials if it is robust to
reflected sky radiance.

## Success Criteria

Lower range error on reflective targets, without degrading ordinary targets,
on unseen targets and on the real scene. Range must be inferred from the
radiance and the provided metadata, not from labels, other modalities or
patch identity.
