# Problem Definition

What problem does this paper address? Write this so that someone with no knowledge of the paper can understand what needs to be solved and how success is measured.

Do NOT describe the paper's method or solution here — only the problem itself. Think about if a future scientist agent try to solve this problem from scratch without knowing what approach the paper took. If you leak the solution, you compromise the benchmark.

## Research Question

<!-- What problem or challenge does this paper tackle? What gap in existing work does it address? -->

## Why It Matters

<!-- Why is this problem important? What would a good solution enable? Make it short -->

## Success Criteria

<!-- What would a successful solution look like? What properties should it have? This is about the goal, not the paper's specific approach. Make it short -->
Estimate passive long-wave infrared range from spectral radiance measurements.
The input is radiance measured at LWIR wavelengths, known atmospheric
attenuation coefficients, and air temperature. The output is object range in
meters for each spatial sample or patch.

The difficult case is a reflective natural-scene object under open sky.
Reflected downwelling sky radiance carries atmospheric absorption structure and
can make ordinary absorption-based ranging overestimate distance. A valid
solution must estimate range from the radiance physics rather than from RGB
texture, lidar, or learned scene priors.
