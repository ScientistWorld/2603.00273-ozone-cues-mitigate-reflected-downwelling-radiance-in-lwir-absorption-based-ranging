# Evaluation

## Prediction Format

Write one file per method, `outputs/<method_name>_predictions.json`:

```json
{"method": "<method_name>",
 "patches": {"<patch_id>": [64 range estimates in meters, row-major, or null], ...}}
```

Include every patch id of the `train`, `test` and `real` splits. Each list
must have exactly 64 entries; an entry is a finite, non-negative number or
`null` (no estimate). The method key in the score files is the file-name
stem. Nothing else in the file is read.

## Metrics (all in meters, lower is better)

Per-pixel absolute errors are clipped at 100 m; a `null` costs 100 m.

| Metric | Coefficient | Meaning |
|---|---:|---|
| `reflective_mae_m` (primary) | 1.0 | mean per-pixel error over reflective targets |
| `reflective_patch_abs_error_m` | 0.5 | mean over reflective targets of the error of the patch's median estimate (systematic error after averaging noise) |
| `ordinary_mae_m` | 0.5 | mean per-pixel error over low-reflectance targets |

## Validity Gates

A run is scored as failed (all three metrics set to 100 m) if:

- the prediction file is malformed: a required patch is missing, a list does
  not have 64 entries, or an entry is non-numeric, NaN/Infinity or negative;
- on either target class (reflective, ordinary) its per-pixel MAE is not
  lower than the MAE of the best constant range guess for that class;
- (held-out test only) on the two reflective patches of the real scene its
  per-pixel MAE is above 35 m.

Failure reasons and unscored diagnostics (patch standard deviations, null
fractions, real-scene errors, the ungated metric values) are written under
`_diagnostics` in the score files.

## Scripts

- `bash scripts/evaluate_train.sh` -> `scoring/scores_train.json` (labelled
  train targets; same metrics and gates except the real-scene gate).
- `bash scripts/evaluate.sh` -> `scoring/scores.json` (same as train).
- `bash scripts/evaluate_test.sh` -> `scoring/scores_test.json` (hidden test:
  held-out targets plus the real-scene check). Not available to methods.

Each script scores every `outputs/*_predictions.json`; none of them runs or
imports method code.

## Reference Comparison

The provided baseline ignores reflected sky radiance and fails the
reflective-target gate (its ungated reflective MAE is about 78 m on test).
The reference method reaches about 21 m reflective MAE on the held-out test.
Ranking is relative to the reference's held-out test scores.
