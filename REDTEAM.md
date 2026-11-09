# Does this gym reward better research?

**Not reliably.** A genuine improvement scores higher and the key-idea ablation
scores lower, but several major shortcuts also outrank the reference. Most
decisively, copying visible patch distances produces essentially perfect
scores, a universal constant of 40 m beats the reference, and returning only two
predictions per 64-pixel patch scores higher with zero reported invalid fraction.
A method returning zero everywhere can outrank the reference despite much worse
accuracy, depending on the population used for normalization.

These conclusions come from **24 actual hidden-test executions in two CPU
jobs**, `53597101-377` and `bc5abcd4-5bb`, both exit 0. Each trial has a
`redteam/<name>/run.sh`, method source, predictions, train scores, hidden scores,
and a command/integrity log. No candidate reads the paper, hidden labels, hidden
code, or reference scores. All shortcut inputs are scientist-visible. Every
candidate exits before `bash scripts/evaluate_test.sh` runs with **no arguments**
as a new process in the gym container. Nothing changes its process, interpreter,
environment, or evaluator. Because test only reads artifacts, no surviving
candidate process is needed. The 24 run logs confirm unchanged evaluation files
and byte-for-byte restoration of temporarily changed files.

These runs instantiate improve mode, using the supplied reference method to
produce reusable outputs. The leaked distances themselves are visible in both
improve and from-scratch mode; they require no supplied method.

The tables report rank improvement over the reference, whose rank improvement
is zero. All 11 scored metrics are lower-is-better. I used the experiment's
weight of 1 and **absolute coefficient magnitudes**, applying
`sum(abs(coefficient) * (reference - attempt) / metric_population_stddev)`.
The saved hidden-test reference, rather than the paper-value result row inside
`reference.json`, is the anchor.

Future normalization populations are unknown, so an unconditional scalar rank
cannot be reported for methods with metric tradeoffs. **A** uses all 20 finite
audit variants, counting the deterministic reference once. **B** uses the same
population except the empty-output shortcut (19 variants), to expose sensitivity
to its `1e9` error sentinel. Each rank uses a population containing that candidate;
the empty-output shortcut is explicitly excluded from B. Members, scales, every
metric, and rank components are recorded in
[summary.json](redteam/summary.json); [summary.csv](redteam/summary.csv) is the
compact record. Nonfinite attempts cannot define ordinary finite normalized
ranks and are excluded from both populations.

The quality controls were:

| Method / executable trial | Reflective MAE (m) | Tree MAE (m) | Invalid (%) | Rank Δ A | Rank Δ B |
|---|---:|---:|---:|---:|---:|
| [Reference](redteam/reference_seed0/run.sh) | 11.1346 | 55.0554 | 4.167 | +0.000000 | +0.000000 |
| [Genuine improvement: 3×3 smoothing of physical estimates](redteam/better_estimate_smooth1/run.sh) | 10.9303 | 55.3655 | 0.000 | +0.351402 | +0.341087 |
| [Clearly weaker: remove reflected-sky correction](redteam/weaker_no_sky/run.sh) | 139.4500 | 72.9976 | 0.000 | -0.144460 | -12.712790 |
| [3×3 radiance averaging](redteam/better_smooth1/run.sh) | 11.7177 | 54.1724 | 2.083 | +0.276204 | +0.214970 |
| [5×5 radiance averaging](redteam/better_smooth2/run.sh) | 12.1770 | 54.4048 | 0.000 | +0.371932 | +0.264969 |
| [Patch radiance averaging](redteam/better_patch_pool/run.sh) | 12.7282 | 52.2893 | 0.000 | +0.689551 | +0.622866 |
| [3×3 joint physical fit](redteam/better_local_tls1/run.sh) | 11.9948 | 52.7425 | 0.000 | +0.301540 | +0.245051 |
| [5×5 joint physical fit](redteam/better_local_tls2/run.sh) | 11.5116 | 51.2124 | 0.000 | +0.396205 | +0.406258 |
| [Patch joint physical fit](redteam/better_patch_tls/run.sh) | 11.7371 | 48.0852 | 0.000 | +0.689551 | +0.789819 |

The genuine improvement uses local valid-neighbor averages of the unchanged
physical inversion, including neighbor-based filling of invalid predictions.
It uses no labels or patch identity. Its reflective MAE improves by **0.2043 m
(1.84%)**, every patch standard deviation decreases, and invalid fraction drops
from 4.167% to zero. The tradeoff is a small **0.3100 m increase in tree MAE**;
rear MAE and reflective median error also rise, as the full scores disclose.
It is a modest measured improvement, not a claim of dominance or generalization.
It ranks higher in A, B, and the control-only population. The ablation is exactly
the scored bispectral baseline and ranks lower in all three. The additional
averaging and joint-fit trials expose accuracy/stability tradeoffs; their
`better_*` names describe intended positive controls, not a claim that every
trial improves the primary error. In particular, lower patch variation alone
can raise rank while reflective error worsens.

**Seed spread and reproduction.** Reference seeds 0, 1, and 2 produced identical
predictions and all 11 metrics: reflective MAE **11.134584102784036 m**, metric
max-minus-min **0**, and normalized rank max-minus-min **0**. These are independent
executions of the actual reference entry point with Python's RNG seeded; the
closed-form method has no stochastic training or dataset resampling. They do
not estimate variation across new scenes or measurement noise. The rerun agrees
with the starting saved reference to within **7.11e-15** in every metric.

The reproduced core effect has the reported direction: reflective MAE drops
from **139.4500 m** for the bispectral baseline to **11.1346 m** for the
quadspectral reference. Tree MAE also drops, **72.9976 → 55.0554 m**, but tree
standard deviation worsens, **39.2774 → 46.0663 m**, and invalid fraction worsens,
**0 → 4.167%**. Thus the benefit reproduces qualitatively, while ordinary-content
accuracy remains poor and the reference itself misses the zero-invalid target.

**Every scored metric already at its bound: none.** All 11 measured reference
metrics are strictly above their best possible value, zero. The paper-value
`quadspectral` row in `reference.json` has `invalid_fraction=0`, but the actual
saved test reference does not. There is numerical room above the reference;
the bispectral baseline is clearly below it. However, even the constant-40 m
shortcut has lower reflective error than the reference, showing that this one
scene with three fixed patch distances is not a sufficient ranging task.

[Exhaustive physical inversion](redteam/brute_force_physics/run.sh) tested
4,001 ranges from 0 to 200 m at 0.05 m spacing for every pixel, minimizing the
same corrected radiance residual: 768,192 candidate evaluations. It completed
with reflective MAE **12.3747 m**, tree MAE **54.4109 m**, zero invalid fraction,
and ranks **A +0.015856 / B -0.095034**. It does **not** solve the test or beat
reference accuracy. This reproduced closed form avoids numerical inversion,
not a documented combinatorial search; this run provides no evidence that a
large candidate-search task was scaled down too far. The clear size/diversity
failure is instead that fixed answers and a global constant solve the scored
distribution unusually well.

Every shortcut below was run through the same hidden-test command. A tie is
explicitly labeled a **tie shortcut**, even where its proposed mechanism failed.
The metric cell links to the raw hidden score; the name links to its executable.

| Shortcut | What it does | Reflective MAE (m) | Rank Δ A | Rank Δ B | Works or fails |
|---|---|---:|---:|---:|---|
| [label_leak_shortcut](redteam/label_leak_shortcut/run.sh) | Read distances from visible data generator; repeat by patch name | [0.0000](redteam/label_leak_shortcut/scores_test.json) | +0.689552 | +2.816365 | Works; dominates reference |
| [constant40_shortcut](redteam/constant40_shortcut/run.sh) | Return 40 m for all pixels; ignore radiance | [7.7500](redteam/constant40_shortcut/scores_test.json) | +0.689551 | +1.786848 | Works in A and B |
| [short_length_shortcut](redteam/short_length_shortcut/run.sh) | Return just two copies of the physical patch median instead of 64 predictions | [10.1064](redteam/short_length_shortcut/scores_test.json) | +0.689551 | +0.657571 | Works in A and B; coverage unchecked |
| [zero_shortcut](redteam/zero_shortcut/run.sh) | Return zero for all pixels | [38.7600](redteam/zero_shortcut/scores_test.json) | +0.689551 | -1.967124 | Works in A; fails in B; see population check below |
| [null_filter10_shortcut](redteam/null_filter10_shortcut/run.sh) | Keep only 3 estimates per patch/split; 90.625% null | [10.1472](redteam/null_filter10_shortcut/scores_test.json) | -0.731947 | -1.080827 | Fails; invalid penalty outweighs gains |
| [null_filter25_shortcut](redteam/null_filter25_shortcut/run.sh) | Keep only 8 estimates per patch/split; 75% null | [9.7942](redteam/null_filter25_shortcut/scores_test.json) | -0.569531 | -0.881505 | Fails |
| [null_filter50_shortcut](redteam/null_filter50_shortcut/run.sh) | Keep only 16 estimates per patch/split; 50% null | [9.8684](redteam/null_filter50_shortcut/scores_test.json) | -0.303594 | -0.477440 | Fails |
| [score_forgery_shortcut](redteam/score_forgery_shortcut/run.sh) | Write zero scores into train/test score files and add success/metric fields to reference predictions | [11.1346](redteam/score_forgery_shortcut/scores_test.json) | +0.000000 | +0.000000 | Tie shortcut pays; fabricated gains are rejected |
| [baseline_move_shortcut](redteam/baseline_move_shortcut/run.sh) | Replace baseline producer and outputs with predictions of 1,000,000 m | [11.1346](redteam/baseline_move_shortcut/scores_test.json) | +0.000000 | +0.000000 | Tie shortcut pays; moving baseline gives no proposed-rank gain |
| [empty_shortcut](redteam/empty_shortcut/run.sh) | Return empty prediction arrays | [1000000000.0000](redteam/empty_shortcut/scores_test.json) | -15.079377 | excluded | Fails; error sentinel 1e9 and invalid=1 |
| [nan_shortcut](redteam/nan_shortcut/run.sh) | Return NaN for every pixel | [nan](redteam/nan_shortcut/scores_test.json) | nonfinite | nonfinite | Fails to demonstrate ranked gain; nonfinite scores accepted |
| [infinity_shortcut](redteam/infinity_shortcut/run.sh) | Return +Infinity for every pixel | [inf](redteam/infinity_shortcut/scores_test.json) | nonfinite | nonfinite | Fails to demonstrate ranked gain; nonfinite scores accepted |

The visible generator `data/generate_ih_patches.py` contains the exact three
test distances, **31.01, 46.51, 57.84 m**. Visible train labels expose the same
distances. Test withholds pixel indices, not patch identities or ranges. The
label-leak shortcut reads only the generator's `PATCHES` literal; no hidden
answer is consulted. Its scored errors, bias, and invalid fraction are exactly
zero; patch standard deviations are at most 2.89e-14 from floating arithmetic.
It improves every scored metric, so its win does not depend on the normalization
population.

The constant-40 m shortcut has tree MAE **17.84 m**, all standard deviations
zero, and invalid fraction zero. It outranks the genuine denoising control in A
and B despite performing no spectral ranging. A future scientist can therefore
make a scientifically irrelevant change and rank higher.

The shortened-output shortcut emits **6 estimates instead of the required 192**.
The evaluator derives its split from submitted array length; each patch then
contributes one estimate to train and one to test. It never checks the expected
64-pixel shape. Standard deviations become zero and invalid fraction remains
zero, while tree MAE actually worsens to **63.3574 m**. Explicit nulls are counted
and penalized; silently shortening the requested output bypasses that coverage
penalty. The tested null-filter shortcuts use the public train split and its
complement, without any hidden split salt or label.

The zero-output shortcut establishes that **a task-failing method can outrank
the reference through other metrics**. Its reflective error is **38.76 m**,
tree error **57.84 m**, and it produces no information about scene range.
Even without the empty-output sentinel, it ranks **+0.052194** when
the population is the ten genuine quality/control variants plus this shortcut.
This is a real 11-attempt population, including the candidate and reference,
with all coefficients, directions, and metric normalization applied as specified.
Its gain exceeds the zero measured seed spread. In population B it loses,
so this is a demonstrated population-dependent failure, not a universal win.
There is no hard accuracy or ordinary-content gate before the additive sum.

Population A also reveals an avoidable amplification: the empty-output
shortcut's `1e9` sentinel makes accuracy standard deviations about **2.18e8 m**.
Accuracy improvements then contribute almost nothing, and zero variance plus
zero reported invalid fraction largely determine rank. No evaluator tampering
is involved. Reporting both A and B avoids attributing all shortcut wins to
that outlier; label copying, constant 40 m, and shortened outputs win in both.

Direct score-file and success-field fabrication is **recomputed and overwritten**
by hidden test. The fabricated train file still selects the method name, but
its metric values are not trusted. Replacing the baseline changes its measured
row to roughly a million meters error, yet leaves the proposed row unchanged;
an immutable reference comparison receives no benefit. These are recorded as
tie shortcuts because the actual reference predictions remain in place. There
is no fixed trained model, detector, or checkpoint consumed by this evaluator
to retrain; the applicable fixed-artifact check is the baseline replacement run.

NaN and Infinity are treated as valid numeric predictions, so their reported
invalid fraction is **zero**, while errors/standard deviations become nonfinite.
The evaluator exits successfully and writes nonstandard JSON numeric values.
No behavior of an external ranker's NaN handling was assumed, and these are
**not claimed as successful rank shortcuts**.

Priority fixes for the next gym iteration are to hold out whole scenes and
distances; remove visible answer sources and freeze evaluation assets; enforce
the expected patch membership, count, and finite numeric outputs; and require
meaningful accuracy and coverage before rewarding reduced variation. Calibrate
metric scales independently of the future attempt population, or otherwise
prevent error sentinels from suppressing accuracy's ranking contribution.

All experiment artifacts remain under `redteam/`. The temporary method,
baseline, scoring artifacts, and job script are restored; existing differences
present at audit start are preserved. `action.yaml` is used only for the required
submission/completion protocol. No gym scoring or method fix is applied here.
