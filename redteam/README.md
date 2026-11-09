# LWIR scoring audit

Each trial directory contains `run.sh` and `method.py`. The latter is a link to
the shared, self-contained candidate implementation (or the actual reference
implementation). `run.sh` chooses its fixed variant, installs it as method
code, generates predictions, runs the visible evaluation, and runs
`bash scripts/evaluate_test.sh` with no arguments in a new process. The
candidate has exited before test starts. No test code, Python environment, or
process is modified. The evaluator never executes candidate code at test time.

`harness.py` supplies only visible data and outputs computed by the original
method. Every shortcut's input use is in `candidate.py`; it never reads hidden
labels, hidden code, the paper, or reference scores. The original baseline
source, prediction files, and scoring files are restored byte for byte in a
`finally` block. Every run retains its predictions, train scores, test scores,
command log, elapsed time, and restoration/integrity results in its own folder.

Run all trials as a CPU job with `bash redteam/run_all.sh`. These methods are
small and use only the standard library. `summarize.py` is audit-only analysis:
it applies the specified normalized additive ranking, lists both normalization
populations, and compares each candidate with the rerun reference. No candidate
imports it. The unknown population of future attempts prevents reporting one
population-independent scalar rank for candidates with metric tradeoffs.

The `better_*` variants apply label-free spatial averaging before the unchanged
quadspectral physical inversion, smooth physical estimates, or fit a common
physical range using errors-in-variables regression. `weaker_no_sky` removes the correction.
`brute_force_physics` enumerates 4,001 physical ranges per pixel. All deliberate
shortcut identifiers include `shortcut`, including failed probes and ties.

Two CPU jobs completed 24 hidden-test trials. `summary.json` and `summary.csv`
preserve all raw metric vectors and normalized rank components. Populations A
and B respectively include all finite variants and exclude the empty-output
outlier; duplicate deterministic reference seeds are counted once. Control-only
scale projections are explicitly named as projections, and each shortcut also
has a genuine control-plus-candidate population recorded for comparison.
`write_report.py` builds `REDTEAM.md` from the retained results without running
experiments. These conclusions are scoring audits, not fixes to gym code.

Runs instantiate improve mode. The visible generator and train labels expose
the same patch distances in from-scratch mode. Original scheduler logs are
retained in `job_logs/`; per-trial logs and scores are in the trial folders.
