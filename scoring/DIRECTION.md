# Research Direction

## Research Problem

Improve passive LWIR absorption-based range estimation in outdoor scenes where
reflected ambient thermal radiance can make reflective surfaces appear much
farther away than they are.

## Approach Scope

In-scope improvements should still operate on LWIR spectral radiance and
physical scene metadata. Acceptable directions include better radiative-transfer
modeling, improved use of spectral cues, more robust inversion, uncertainty
handling, or calibration strategies that preserve the same input/output task.

## Out of Bounds

Do not solve the task by supervised fitting to the evaluation patch distances,
using non-LWIR modalities, adding external scene priors that bypass the
radiance problem, or changing the benchmark labels/data to make the task easier.
