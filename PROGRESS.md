# Progress

## What Works

- Read the paper and cloned the public author code release into
  `method/upstream/`.
- Implemented the paper's Sec. IV quadspectral ozone-cue estimator in Python.
- Implemented the air-aware bispectral baseline that omits reflected
  downwelling correction.
- Built a small four-band LWIR benchmark generated from the paper's
  radiative-transfer model, with reflective checkerboard-like patches and a
  low-reflectance tree-like patch.
- `scripts/reproduce.sh` runs data generation, baseline, method, and
  evaluation end to end on CPU.

## Results

Local validation writes `scoring/scores.json` and passes
`python validate.py --compare`.

On the packaged synthetic benchmark:
- Bispectral reflective MAE: 85.22 m
- Quadspectral reflective MAE: 5.92 m
- Bispectral tree MAE: 1.98 m
- Quadspectral tree MAE: 3.76 m
- Invalid fraction: 0.0 for both methods

Paper Table I reports reflective MAE dropping from 123.74 m for bispectral to
13.96 m for quadspectral on the real Path 5 Step 1 lidar patches.

## Remaining

- Run the packaged pipeline in the scheduler container.
- A higher milestone would require acquiring the full IHTest_202104 HSI cube
  and reproducing the real patch table, or running the upstream hyperspectral
  optimizer.

## Issues

- The upstream repository includes atmospheric and lidar support files but not
  the large radiance cube used in the paper figures.

## Deviations from Paper

<!-- Do not edit this section unless you deviated from the paper's original setup.
     For each deviation, document: what the paper used, what you substituted, and why.

     ACCEPTABLE deviations (data/resource/scale substitutions — milestones still valid):
       - Replaced a proprietary dataset with a public one
       - Used a smaller model of the same architecture
       - Scaled down training (fewer epochs, smaller batch)
       - Used a different library for the same algorithm

     UNACCEPTABLE deviations (algorithm substitutions — milestones above 'none' are void):
       - Replaced the paper's algorithm with a fundamentally different one
       - Wrote a generic model trained to approximate the method's outputs
         instead of implementing the method's computational steps

     The test: could someone reading your code identify which algorithm from
     the paper you implemented? If not, you replaced the method. -->

- Data scale/resource substitution: the paper evaluates on real IHTest_202104
  Path 5 Step 1 hyperspectral data with lidar patches. The packaged core
  benchmark uses synthetic four-band radiance patches generated from the
  paper's Eq. (7), because the full HSI cube is large and not included in the
  author code release. The algorithm is not substituted: the method code uses
  the closed-form quadspectral ozone correction from Eq. (18) and Eq. (22).
