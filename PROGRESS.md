# Progress

## What Works

- Read the paper and cloned the public author code release into
  `method/upstream/`.
- Implemented the paper's Sec. IV quadspectral ozone-cue estimator in Python.
- Implemented the air-aware bispectral baseline that omits reflected
  downwelling correction.
- Built a small four-band LWIR benchmark from the public IHTest_202104 Path 5
  Step 1 LWIR HSI cube, using the crop, bands, and patch centers in the
  paper's released MATLAB figure script.
- `scripts/reproduce.sh` runs data generation, baseline, method, and
  evaluation end to end on CPU.
- Evaluation now reads ground-truth patch distances from
  `eval/quadspectral_core_labels.json`; prediction files contain patch names
  and estimates only.

## Results

Local validation writes `scoring/scores.json` and passes
`python validate.py --compare`. A final CPU scheduler validation is being
submitted to verify the current pipeline state in-container.

On the packaged real IHTest patch benchmark:
- Bispectral reflective MAE: 139.00 m
- Quadspectral reflective MAE: 11.83 m
- Bispectral tree MAE: 77.62 m
- Quadspectral tree MAE: 59.71 m
- Invalid fraction: 0.0 for bispectral and 0.042 for quadspectral

Paper Table I reports reflective MAE dropping from 123.74 m for bispectral to
13.96 m for quadspectral on the real Path 5 Step 1 lidar patches.

## Remaining

- Reduce the gap to the paper's quadspectral residual by reproducing the
  authors' processed `DC2P5S1.mat` calibration exactly or by adding their
  hyperspectral optimizer.
- Additional claims remain: full hyperspectral correction, total-variation
  regularization, and image-level depth maps.
- The current milestone is `core_claim`: the paper's actual closed-form
  quadspectral method runs on public real IHTest radiance patches and reduces
  reflective-patch range error substantially relative to the bispectral
  baseline.

## Issues

- The upstream repository includes atmospheric and lidar support files but not
  the large `DC2P5S1.mat` radiance cube used in the paper figures. The public
  AWS IH dataset provides raw ENVI BSQ collects; this gym extracts the paper
  patch measurements from `LWHSI1_collect1`.
- Job `ef89eced-1b5` ran the reproduction and validation successfully, but
  exited with code 2 because the template tail of `scripts/run.sh` still tried
  to execute a nonexistent `method/train.py`. Removed the stale template lines.
- Retry job `2d92bd6f-811` exited with code 0 in the scheduler container and
  passed all scoring and repository-structure validation checks.
- CPU validation job `f031ddb2-f53` exited with code 0 in the scheduler
  container, but it used an earlier quadspectral calibration state. The current
  local pipeline has since been rerun and passes validation with the scores
  recorded above.
- A review identified a label-leak risk: prediction files previously copied
  patch ground truth from the method input. This is fixed by splitting
  method-visible radiance inputs from eval-owned labels.
- A packaging review identified two robustness issues. `scripts/reproduce.sh`
  no longer calls the downloader inside compute jobs, and the evaluator now
  returns a large penalty instead of crashing when a submission produces no
  valid reflective estimates.
- The method and baseline scripts now validate the band-count, attenuation
  ordering, and non-singular water-vapor attenuation difference assumptions
  used by the paper's closed-form estimator.
- Raw `collect1` gives a bispectral baseline and quadspectral primary metric
  close to the paper's Table I values after using the paper-released
  downwelling-regression coefficient for the selected band pair.
  The paper's processed cube likely includes calibration/registration steps not
  present in the raw public BSQ file.

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

- Data representation substitution: the paper's public code loads a processed
  MATLAB cube named `DC2P5S1.mat`, which is not included in the release. The
  packaged benchmark downloads the public raw IHTest_202104 Path 5 Step 1
  ENVI BSQ LWIR cube from AWS and extracts the same three 8x8 patch locations
  and four quadspectral bands. The patch labels use the paper's reported lidar
  ground-truth distances from Table I. The algorithm is not substituted: the
  method code uses the closed-form quadspectral ozone correction from Eq. (18)
  and Eq. (22).
