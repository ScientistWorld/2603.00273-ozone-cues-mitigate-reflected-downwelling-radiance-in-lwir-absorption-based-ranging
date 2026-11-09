#!/bin/bash
# Hardening audit: rebuild every variant/shortcut and score it with the
# unchanged hidden-test evaluator; then rank, paired comparisons, robustness.
set -e
cd /home/user
H=redteam/hardening
rm -rf $H/outputs && mkdir -p $H/outputs
python $H/make_attempts.py --out $H/outputs | tee $H/make_attempts.log
python eval/test/evaluate.py --outputs-dir $H/outputs --output $H/scores_test_all.json
python eval/train/evaluate.py --outputs-dir $H/outputs --output $H/scores_train_all.json
python $H/rank.py | tee $H/rank.log
python $H/paired.py --attempts better_aircentred_cue_patch_median better_patch_median better_local_median3x3 \
  better_aircentred_cue weaker_sky_slope_0p8 weaker_half_sky_slope weaker_no_sky_correction \
  shortcut_train_affine_calibration shortcut_train_ridge_regression | tee $H/paired.log
python $H/alt_sets.py | tee $H/alt_sets.log
# Baseline-move check: replace the baseline's predictions by 1e6 m and rescore;
# the reference row must not move.
mkdir -p $H/baseline_move
cp $H/outputs/reference_quadspectral_predictions.json $H/baseline_move/
python - <<'PY'
import json
p = "redteam/hardening/outputs/weaker_no_sky_correction_predictions.json"
d = json.load(open(p))
d["patches"] = {k: [1e6] * len(v) for k, v in d["patches"].items()}
json.dump(d, open("redteam/hardening/baseline_move/bispectral_predictions.json", "w"))
PY
python eval/test/evaluate.py --outputs-dir $H/baseline_move --output $H/baseline_move/scores_test.json
python - <<'PY'
import json
a = json.load(open("redteam/hardening/scores_test_all.json"))["experiments"]["lwir_reflective_patch_ranges"]["results"]["reference_quadspectral"]
b = json.load(open("redteam/hardening/baseline_move/scores_test.json"))["experiments"]["lwir_reflective_patch_ranges"]["results"]["reference_quadspectral"]
print("baseline-move: reference row unchanged =", a == b)
PY
# Determinism: regenerate the simulated sets in the container and compare hashes.
python - <<'PY'
import hashlib, subprocess, tempfile, shutil, pathlib
root = pathlib.Path("/home/user")
tmp = pathlib.Path(tempfile.mkdtemp())
shutil.copy(root / "data/lwir_scenes/atmosphere.json", tmp / "atmosphere.json")
subprocess.run(["python", "eval/test/build_scenes.py", "--force", "--data-dir", str(tmp),
                "--train-labels", str(tmp / "train_labels.json"), "--test-labels", str(tmp / "test_labels.json")], check=True)
h = lambda p: hashlib.sha256(pathlib.Path(p).read_bytes()).hexdigest()[:16]
for a, b in (("data/lwir_scenes/train_radiance.f32", tmp / "train_radiance.f32"),
             ("data/lwir_scenes/test_radiance.f32", tmp / "test_radiance.f32"),
             ("eval/train/train_labels.json", tmp / "train_labels.json"),
             ("eval/test/test_labels.json", tmp / "test_labels.json")):
    print("regenerated", a, "identical =", h(root / a) == h(b))
shutil.rmtree(tmp)
PY
