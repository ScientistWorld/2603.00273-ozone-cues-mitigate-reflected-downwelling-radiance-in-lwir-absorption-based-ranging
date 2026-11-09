# Hardening report (iteration 11)

## Verdict

**Better results now score higher and the major shortcuts no longer pay.**
On the new hidden test, all four genuine improvements rank above the
reference by 4–16 paired standard errors. Every graded weaker variant ranks
below it. Every shortcut the red team found either fails the run or only
ties the reference. One borderline item remains open by rule only (fitting a
calibration or regressor to the train labels; see "Shortcuts left open").

All numbers below come from the unchanged hidden-test evaluator
(`eval/test/evaluate.py`), run by `redteam/hardening/run_audit.sh`.
Artifacts are in `redteam/hardening/` (`rank.log`, `summary.{json,csv}`,
`paired.log`, `alt_sets.json`, `scores_{train,test}_all.json`).

**How ranks are computed.** Rank Δ = Σ |coef| × (reference − attempt) /
population std. Every scored metric is lower-is-better. Population A is all
23 audited attempts. Population B is the attempts that did not fail, plus the
candidate. Old ranks are taken from `REDTEAM.md`, so they come from the old
test and a different population.

## What was wrong and what changed

The old hidden test scored three real 8×8 patches (front checkerboard, rear
checkerboard, tree) from one scene. Train and test were two halves of the
pixels of those same three patches. Their ranges (31.01, 46.51, 57.84 m) were
published in the paper and also sat in visible files. The real scene cannot
be fixed by making it denser. I scored both closed-form estimators against
the authors' lidar map on 131 lidar-homogeneous 8×8 patches of the paper's
crop. A constant 34.6 m guess has 8.9 m MAE there. The quadspectral reference
has 26.7 m mean (14.1 m median) and the bispectral baseline has 36.7 m. On
real raw data, these estimators cannot be ranked against trivial guesses.

**Changes:**

1. **New scored test: held-out simulated targets** (`eval/test/scene_simulator.py`,
   `eval/test/build_scenes.py`).
   - The targets come from the paper's measurement model: Eq. 7 with the
     Eq. 23 reflected term plus a ground-sourced term. It uses the authors'
     released Path 5 Step 1 attenuation (SpectralCalc/HITRAN2020) and their
     10-angle downwelling dictionary, at 96 instrument bands with 1 µflick
     noise (the paper's sensor noise).
   - Every target has a random range (15–200 m), a temperature contrast of
     1.5–8 K (mostly colder than air, as near sunset), a smooth non-gray
     emissivity spectrum, a sky view, a zenith-angle mix and a ground
     temperature.
   - Reflective targets are two-material checkerboards (ε 0.3–0.95). Ordinary
     targets have ε 0.95–0.99.
   - Test has 288 targets (192 reflective, 96 ordinary) with opaque ids. Train
     has 144 targets from the same distribution, with visible labels.
   - The generator and a 192-bit secret key live only in `eval/test/`. Only
     the radiance is visible (`data/lwir_scenes/`). Test labels exist only in
     `eval/test/test_labels.json`.
   - Rebuilding in the job container reproduces the committed files byte for
     byte.
2. **Real scene kept as a check, not a score.** The three real patches use
   neutral ids. Their labels are only in `eval/test/real_labels.json`. On
   the two checkerboards, the per-pixel reflective MAE must be ≤ 35 m (the
   reference has 17.9 m; ignoring reflected sky gives about 130 m). I removed
   the visible answer sources: distances in `data/generate_ih_patches.py`,
   `eval/lwir_patch_labels.json`, both slice label files, and the authors'
   registered `lidar.mat` under `method/upstream/data/`.
3. **Evaluator recomputes everything from raw estimates and fails bad runs.**
   - It requires all 64 estimates for every test and real patch. Each must be
     null or a finite, non-negative number. Otherwise the run fails, which
     covers short arrays, empty arrays, NaN, ±Inf, negative values and
     strings.
   - Per-pixel errors are clipped at 100 m, and a null costs 100 m. Abstaining
     is never cheaper than estimating, and there is no 1e9 sentinel.
   - If a target class does no better than the best constant guess for that
     class (computed by `eval/`), or the real gate fails, the run fails. A
     failed run gets 100 m on every scored metric, which is the worst value
     and is bounded.
   - Method keys are file stems. No method name is hard-coded, and nothing
     else in the prediction file is read.
4. **Metrics and coefficients.**
   - Scored metrics: `reflective_mae_m` (1.0, primary, the paper's claim),
     `reflective_patch_abs_error_m` (0.5, the Table I patch-level error) and
     `ordinary_mae_m` (0.5, the do-not-break-ordinary-content constraint).
   - Removed from scoring:
     - Patch standard deviations rewarded constant or zero output.
     - `invalid_fraction` is now folded into the MAE through the 100 m null
       cost.
     - Median, p90 and bias were redundant.
   - These quantities remain in `_diagnostics`, outside `results`.
5. **Reference consistency.** The method and baseline now read the
   attenuation of the chosen bands from the authors' `attenuation.mat`, as
   their MATLAB code does: bands 23/25 give 8.69e‑3 and 7.50e‑4 dB/m. The old
   gym used the paper text's 8.0e‑3 and 2.98e‑4, which belong to another band
   pair. The sky slope s = 0.7977 is now computed from the dictionary (Eq. 21)
   instead of hard-coded. The algorithm is unchanged: Eqs. 18 and 22 with the
   authors' Table I bands.
6. **Docs and scripts.**
   - Docs: `briefing/` and the `scoring/` documents describe the new task.
   - `reference.json` keeps the paper's Table I numbers unchanged under
     `_paper_table1`. Its `results` hold this gym's measured hidden-test
     values.
   - `scripts/evaluate_test.sh` takes no arguments and scores every
     `outputs/*_predictions.json`.
   - `download.sh` fetches the cube and the authors' assets from public URLs.
   - The container adds numpy and scipy for future methods. The gym itself is
     standard-library only.

## Does better score higher? (variants, before → after)

| Variant | Before: reflective MAE / rank A / B | After: reflective / patch / ordinary MAE (m) | After rank A / B | Paired Δ reflective vs ref (± SE) |
|---|---|---|---:|---:|
| Reference quadspectral | 11.13 / 0 / 0 | 21.34 / 14.77 / 19.91 | 0 / 0 | – |
| 3×3 median of estimates (red team's "genuine improvement") | 10.93 / +0.351 / +0.341 | 14.66 / 11.46 / 14.56 | +0.271 / +1.716 | −6.68 ± 0.55 |
| Patch median of estimates | (patch radiance pool) 12.73 / +0.690 / +0.623 | 11.55 / 11.53 / 14.43 | +0.349 / +2.156 | −9.79 ± 0.97 |
| Air-centred ozone cue (Planck-slope fix) | – | 19.75 / 10.67 / 15.60 | +0.140 / +0.956 | −1.59 ± 0.36 |
| Air-centred cue + patch median | – | 7.86 / 7.82 / 4.07 | +0.611 / +4.001 | −13.48 ± 1.04 |
| Weaker: sky slope × 0.8 | – | 34.85 / 33.41 / 20.05 | −0.559 / −3.213 | +13.51 ± 0.65 |
| Weaker: sky slope × 0.5 | – | failed (constant-guess and real gates) | −3.942 / −6.295 | +34.38 ± 1.26 |
| Weaker: no sky correction (bispectral, the paper's baseline) | 139.45 / −0.144 / −12.71 | failed (ungated 78.20 / 80.64 / 22.21) | −3.942 / −6.295 | +56.86 ± 1.70 |

- **Before:** the old test could not separate a genuine improvement from a
  shortcut. Constant 40 m, label copying and shortened outputs all reached
  the same top rank (+0.690 in population A) as patch pooling.
- **After:** the ordering is monotone in quality.
- **Stability across test sets:** `alt_sets.json` rebuilds the held-out set
  with three other keys. The reference gets 21.0, 21.3 and 22.8 m, and the
  ordering of all seven variants is identical in every set.
- **Noise:** the method is deterministic. Test sampling is the only noise
  source, and the paired standard errors above measure it.

## Shortcuts: fix and score before → after

| Shortcut | Before (rank A / B) | Fix | After |
|---|---|---|---|
| Label leak (copy visible patch distances) | +0.690 / +2.816 | Test targets are new and hidden; no distances in visible files | Not applicable. The analogue, copying the published real-scene ranges, only ties: rank 0 / 0 (the real scene is a gate, not a score) |
| Constant 40 m | +0.690 / +1.787 | Ranges 15–200 m plus constant-guess gate | Failed: −3.942 / −6.295 |
| Constant at the train median | – | Same | Failed: −3.942 / −6.295 |
| Zero everywhere | +0.690 / −1.967 | Constant-guess gate; std no longer scored | Failed: −3.942 / −6.295 |
| Short length (2 of 64 estimates) | +0.690 / +0.658 | Exact 64-entry check | Failed: −3.942 / −6.295 |
| Null filter (keep 25%) | −0.570 / −0.882 | Null costs 100 m | Failed: −3.942 / −6.295 |
| Empty arrays | −15.08 / excluded (1e9 sentinel) | Structural fail, bounded 100 m | Failed: −3.942 / −6.295 |
| NaN / +Inf | non-finite scores accepted | Structural fail | Failed: −3.942 / −6.295 |
| Negative ranges | – | Structural fail | Failed: −3.942 / −6.295 |
| Score forgery (fake metric/success fields) | tie 0 / 0 | Only estimates are read | Tie: 0 / 0 |
| Baseline move (baseline set to 1e6 m) | tie 0 / 0 | Nothing is compared against the baseline file | Reference row unchanged (checked in `run_audit.sh`) |
| kNN copy of train labels | – | Real gate (35 m) + rule | Failed by the real gate (real 40.8 m; ungated test 47.6 m, train 30.3 m): −3.942 / −6.295 |
| Ridge regression on train labels | – | Real gate + rule | Failed by the real gate (real 38.8 m; ungated test 25.94 m vs reference 21.34 m): −3.942 / −6.295 |

## Shortcuts left open

- **Supervised calibration on the train labels.** An affine correction
  fitted to train patch medians (slope 0.962, intercept −4.35 m) scores 19.40
  / 11.21 / 17.55 m and ranks +0.119 / +0.767. It passes the real gate (22.5
  m). Train and test share a distribution, and any label-fitted model learns
  that shared distribution, so no structural fix exists. It is forbidden in
  `scoring/CONSTRAINTS.md` and left for the shortcut grader. Every
  physics-based improvement I tried beats it, except the air-centred cue
  alone (+0.140), which only edges it.
- **Learned regressors trained on the train labels.** The two I tried fail
  the real gate. A stronger learned model could pass it and beat the
  reference on the simulated targets. This is covered by the same rule.
- **The published real-scene ranges.** These are public in the paper. Copying
  them can only pass the gate; it ties the reference and never gains.
- **Visible test radiance.** Test-time optimisation on the test inputs is
  allowed, because the inputs carry no labels. A method that fits the
  physical model harder is the paper's own hyperspectral direction, not a
  loophole.

## Reference score before → after

- **Before:** 11.13 m reflective MAE on the old test (half the pixels of two
  real checkerboards; tree MAE 55.06 m; 4.2% invalid).
- **After (held-out test):**
  - `reflective_mae_m` = 21.34
  - `reflective_patch_abs_error_m` = 14.77
  - `ordinary_mae_m` = 19.91
  - Real-scene check: 17.91 m (gate 35 m).
- **After (train):** 21.60 / 15.82 / 17.15 m. An honest method scores alike
  on train and test.
- The old and new numbers come from different tests and are not comparable.
- The paper's effect reproduces in the paper's direction:

  | Target set | Bispectral (no sky correction) | Quadspectral |
  |---|---:|---:|
  | Held-out simulated reflective targets | 78.2 m (ungated; fails the gate) | 21.3 m |
  | Real checkerboards (raw public cube) | ~130 m | 18 m |

## Headroom check

- **Bounds:** the reference sits at the bound (0 m) of no scored metric. The
  best simple variant (air-centred cue + patch median) reaches 7.86 / 7.82 /
  4.07 m. That is a large gain, but it is far from 0. The remaining error
  comes from per-target emissivity, temperature and sky-angle effects. A
  joint multi-band model fit (the paper's hyperspectral method, which the 96
  bands and the downwelling dictionary make possible) or better handling of
  pixels with no solution should go further.
- **What I added:** the held-out simulated targets are the experiment built
  from where the paper's quadspectral method falls short. It has to cope with
  noise at low temperature contrast, the approximations in its closed form,
  one sky slope for all orientations, and no solution on some pixels. The
  paper itself reports that the hyperspectral method beats it for these
  reasons.
- **Baseline:** the bispectral baseline is clearly below the reference. It
  fails the gate, with an ungated reflective error of 78 m against 21 m for
  the reference.
- **Brute force:** an exhaustive 1-D range search on the closed-form residual
  equals the closed form. The red team ran it on the old test and it did not
  beat the reference. A full per-pixel model inversion is the paper's own
  better method, not a shortcut the test must defeat. Wall-clock time is not
  scored.

## Weights

There is one experiment with weight 1.0. Coefficients:

- `reflective_mae_m` = 1.0. This is the paper's claim.
- `reflective_patch_abs_error_m` = 0.5. This is what Table I reports per
  patch.
- `ordinary_mae_m` = 0.5. This is the paper's constraint. It is not set
  higher because catastrophic damage to ordinary targets is already a gate
  failure.

## What I could not fix

- **The scored test is simulated.** The only real scene with ground truth has
  two reflective targets and publicly known ranges. Densely, the real scene is
  dominated by estimator noise: a constant guess beats every method on 131
  lidar patches. So real data serves only as a transfer gate (35 m on two
  checkerboards) and as diagnostics. A simulator-specific method that also
  happens to pass the real gate would be rewarded. Only the constraints rule
  guards against that for label-fitted methods.
- **The real tree patch is poorly ranged by every estimator on the raw
  public cube.** The reference gets 53.7 m, against the paper's 11.4 m on the
  authors' processed cube, which is not released. This patch is reported
  under `_diagnostics` and is not used.

## Verification

- **Job.** CPU job `37ffc6db-e58` ran `scripts/run.sh` in the gym container
  (Python 3.11) and exited with code 0. It:
  - reran the baseline and reference from the final code;
  - scored the train and test slices;
  - ran the full audit (`redteam/hardening/run_audit.sh`);
  - rebuilt the three alternate test sets;
  - regenerated the simulated data, which matched the committed train/test
    radiance and label files byte for byte;
  - repeated the baseline-move check, which left the reference row
    unchanged;
  - passed `validate.py --compare --post-reproducer`.

  Every number in this report matches that run.
- **Rescoring after the job.** The evaluators now average with `math.fsum`,
  so scores are bit-identical across Python versions. Before the change,
  Python 3.11 and 3.12 summed differently and the scores differed by about
  1e-14. The saved outputs were rescored; no method was rerun. The values are
  unchanged at every reported precision.
- **What `run.sh` does now.** `scripts/run.sh` reproduces the reference end
  to end: baseline, method, train and test scoring, and validation. The audit
  is run separately with `bash redteam/hardening/run_audit.sh`.
