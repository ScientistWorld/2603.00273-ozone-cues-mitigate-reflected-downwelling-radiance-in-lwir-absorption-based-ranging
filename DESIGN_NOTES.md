# Train/Test Evaluation Design Notes

## What I Checked

- Read `scripts/evaluate_train.sh` and `scripts/evaluate_test.sh` side by side.
- Read both slice evaluators under `eval/train/` and `eval/test/`.
- Checked that evaluators read method prediction artifacts from `outputs/*_predictions.json` instead of importing or re-running `method/`.
- Checked for train/test cross-imports and hardcoded method defaults.
- Checked active metrics in `scoring/reference.json` for paper-agreement scoring and missing metadata.
- Confirmed `scoring/scores_train.json` and `scoring/scores_test.json` are absent.
- Ran `bash -n` on both evaluation scripts and JSON parse checks on edited metadata/label files.

## What Changed

- Replaced the obvious even/odd pixel split with slice-specific salted half-sample masks. This keeps each slice at exactly half of each patch while making the held-out test positions a private test detail instead of the visible parity complement.
- Pointed train and test scripts at slice-local label files under `eval/train/` and `eval/test/`.
- Added descriptions to every active metric in `scoring/reference.json`; all metrics now include `higher_is_better`, `coefficient`, and `description`.
- Preserved method discovery from prediction files, so future method variants are scored without hardcoded method names.

## Remaining Runtime Concerns

- The benchmark is still small: three 8x8 patches from one scene. The salted split improves anti-shortcut behavior inside those patches, but a future design pass with additional held-out patches or scenes would be stronger.
- The visible train labels necessarily expose the three patch distances. A shortcut that writes the known distances for every named patch could score well on both slices because this first-pass gym does not have additional hidden patch identities. The held-out mask mainly catches shortcuts that tune only visible pixel positions or visible aggregation behavior.
- Test evaluation optionally uses `scoring/scores_train.json` to restrict the method list to train-scored methods. If that file is absent, it falls back to all prediction artifacts in `outputs/`, which is appropriate for final test-only runs but should be watched by the runner.
