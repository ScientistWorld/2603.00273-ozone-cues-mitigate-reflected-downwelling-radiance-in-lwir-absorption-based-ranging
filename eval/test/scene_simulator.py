"""Held-out LWIR target simulator (hidden; lives only in eval/test/).

Generates 8x8 radiance patches from the radiative-transfer measurement model
of the paper (object emission + diffusely reflected ambient radiance,
attenuated by Beer's law, plus path emission) using the released Path 5
Step 1 attenuation spectrum and zenith-resolved downwelling sky radiance.
Nuisance factors (emissivity spectra, temperature contrast, sky view,
ground temperature, sensor noise) are randomised per target.
"""

from __future__ import annotations

import math
import random

H, C, KB = 6.63e-34, 3.0e8, 1.38e-23
PATCH = 8
NOISE_STD = 1.0  # microflick, the instrument's typical noise level


def planck(lambda_um: float, t_k: float) -> float:
    lm = lambda_um * 1e-6
    return 1e-4 * (2.0 * H * C * C / lm**5) / (math.exp(H * C / (lm * KB * t_k)) - 1.0)


def _shape(rng: random.Random, amplitude: float):
    bumps = [(rng.uniform(7.8, 10.2), rng.uniform(0.4, 1.2), rng.uniform(-1.0, 1.0)) for _ in range(2)]

    def f(lam: float) -> float:
        return amplitude * sum(a * math.exp(-0.5 * ((lam - c) / w) ** 2) for c, w, a in bumps)

    return f


def _zenith_weights(zenith: list[float], centre: float, spread: float) -> list[float]:
    w = [math.exp(-0.5 * ((z - centre) / spread) ** 2) for z in zenith]
    total = sum(w)
    return [x / total for x in w]


def simulate_patch(rng: random.Random, target_class: str, atm: dict):
    lam = atm["wavelengths_um"]
    att = atm["attenuation_db_per_m"]
    dw = atm["downwelling_microflick"]
    zen = atm["downwelling_zenith_deg"]
    t_air = float(atm["t_air_k"])
    n_b = len(lam)

    d0 = rng.uniform(15.0, 200.0)
    grad_r, grad_c = rng.uniform(-0.03, 0.03), rng.uniform(-0.03, 0.03)
    delta_t = (-1.0 if rng.random() < 0.75 else 1.0) * rng.uniform(1.5, 8.0)
    t0 = t_air + delta_t
    if target_class == "reflective":
        eps_a = rng.uniform(0.3, 0.85)
        eps_b = min(0.95, eps_a + rng.uniform(0.05, 0.25))
        materials = [(eps_a, _shape(rng, rng.uniform(0.0, 0.03))), (eps_b, _shape(rng, rng.uniform(0.0, 0.03)))]
        sky_fraction = rng.uniform(0.3, 0.55)
        weights = _zenith_weights(zen, rng.uniform(55.0, 89.0), rng.uniform(4.0, 20.0))
    elif target_class == "ordinary":
        eps = rng.uniform(0.95, 0.99)
        shape = _shape(rng, rng.uniform(0.0, 0.008))
        materials = [(eps, shape), (eps, shape)]
        sky_fraction = rng.uniform(0.4, 1.0)
        weights = _zenith_weights(zen, rng.uniform(0.0, 89.0), rng.uniform(5.0, 30.0))
    else:
        raise ValueError(target_class)
    t_ground = t_air + rng.uniform(-3.0, 3.0)

    b_air = [planck(l, t_air) for l in lam]
    ambient = [
        sky_fraction * sum(w * dw[k][q] for q, w in enumerate(weights))
        + (1.0 - sky_fraction) * 0.97 * planck(lam[k], t_ground)
        for k in range(n_b)
    ]
    eps_spec = [[base + f(l) for l in lam] for base, f in materials]

    pixels, distances = [], []
    for i in range(PATCH):
        for j in range(PATCH):
            d = d0 * (1.0 + grad_r * (i - 3.5) / PATCH + grad_c * (j - 3.5) / PATCH)
            t = t0 + rng.gauss(0.0, 0.2)
            jitter = rng.gauss(0.0, 0.002)
            spec = eps_spec[((i // 4) + (j // 4)) % 2]
            row = []
            for k in range(n_b):
                e = min(0.999, max(0.02, spec[k] + jitter))
                tau = 10.0 ** (-att[k] * d / 10.0)
                leaving = e * planck(lam[k], t) + (1.0 - e) * ambient[k]
                row.append(tau * (leaving - b_air[k]) + b_air[k] + rng.gauss(0.0, NOISE_STD))
            pixels.append(row)
            distances.append(round(d, 4))
    info = {
        "delta_t_k": round(delta_t, 3),
        "sky_fraction": round(sky_fraction, 3),
        "emissivity": [round(m[0], 3) for m in materials],
    }
    return pixels, distances, info
