# Ozone Cues Mitigate Reflected Downwelling Radiance in LWIR Absorption-Based Ranging

<!-- scope-note -->
> [!NOTE]
> **Not a full reproduction of the paper.** This environment keeps the paper's core problem at a reduced scale so it is easy to run. It measures an AI scientist's idea and how well it is carried out, not the full research loop.

<!-- hardening-note -->
> [!NOTE]
> **Red-teamed and hardened.** A red team tried to score on this environment's hidden test without doing better research, and the environment was then fixed against the shortcuts that worked: see [`REDTEAM.md`](REDTEAM.md) and [`HARDENING.md`](HARDENING.md). The environment as it was before is kept as branch [`pre-hardening`](../../tree/pre-hardening).

| This paper | Scientist World, the framework this environment belongs to |
|:---:|:---:|
| <a href="https://arxiv.org/abs/2603.00273"><img alt="This paper on arXiv" src="https://img.shields.io/badge/arXiv-2603.00273-b31b1b?logo=arxiv&logoColor=white"></a> | <a href="https://arxiv.org/abs/2611.08478"><img alt="Scientist World on arXiv" src="https://img.shields.io/badge/arXiv-2611.08478-b31b1b?logo=arxiv&logoColor=white"></a> <a href="https://github.com/zlab-princeton/scientist_world"><img alt="Scientist World code" src="https://img.shields.io/badge/Code-Scientist_World-181717?logo=github&logoColor=white"></a> <a href="https://github.com/zlab-princeton/scientist_world_cli"><img alt="Command line code" src="https://img.shields.io/badge/Code-Command_line-181717?logo=github&logoColor=white"></a> |

| **Paper ID** | [2603.00273](https://arxiv.org/abs/2603.00273) |
|:---|:---|
| **Domain** | Computational imaging / thermal remote sensing |
| **TL;DR** | The paper uses ozone absorption structure in reflected sky radiance to correct passive LWIR range overestimates on reflective objects. |

## Summary

Passive LWIR absorption-based ranging estimates depth from spectral
attenuation, but reflective surfaces can mirror downwelling sky radiance and
produce large overestimates. The paper proposes a closed-form four-band
estimator and a richer hyperspectral optimizer that explicitly account for
reflected downwelling radiance. The packaged reproduction implements the
closed-form quadspectral estimator and compares it against the air-aware
bispectral baseline on public IHTest_202104 Path 5 Step 1 LWIR HSI patches.

## Problem

Estimate object range from passive long-wave infrared spectral radiance in
natural outdoor scenes. The input is measured LWIR radiance at known wavelengths
plus scene-level atmospheric metadata such as attenuation coefficients and air
temperature. The output is range in meters for each spatial sample or patch.

The difficult regime is a reflective surface under open sky. Reflected ambient
thermal radiation can carry absorption structure unrelated to the
object-to-sensor path, causing ordinary absorption-based ranging to infer a
distance that is much too large.

## The paper's method

The paper introduces ozone-cue mitigation for reflected downwelling radiance in
LWIR absorption-based ranging. It uses spectral structure that appears strongly
in sky radiance but is negligible in ground-level horizontal propagation to
estimate and remove the reflected-radiance bias that makes reflective objects
look farther away.

## Key results of the paper

- Paper Table I reports reflective checkerboard errors dropping from over 100 m
- This reproduction shows the same qualitative effect on a small real-data

## Run it

```bash
pip install sciworld
sw research 2603.00273 --mode innovate --agent claude-code
sw evaluate 2603.00273
```

## More

The full problem statement, method notes, evaluation protocol and reproduction log are in [DETAILS.md](DETAILS.md).

