# Frozen normalization coefficients — 2603.00273

These are the **locked** per-paper variance-normalization coefficients used to score submissions on this benchmark task. Once locked they are frozen, so any future submission is scored against a stable, reproducible normalizer (the published score no longer drifts as new models are added to the cohort).

Each `coeffs_<mode>_<phase>.json` carries `cells` (per-cell `coefficient`, `source`, `higher_is_better`), `paper_baseline`, and the cohort it was computed from.

- `normalization/coeffs_innovate_test.json` — mode=`innovate` phase=`test` locked with **4** cohort models at `2026-08-10T12:28:12.697640+00:00`
- `normalization/coeffs_innovate_train.json` — mode=`innovate` phase=`train` locked with **4** cohort models at `2026-08-10T12:28:12.697640+00:00`

This is a standalone snapshot branch; it intentionally does not contain the rest of the paper's code or run history.
