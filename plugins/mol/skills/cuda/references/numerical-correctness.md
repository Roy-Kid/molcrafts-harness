# Numerical correctness for scientific CUDA

## Rules

1. **Keep a reference.** CPU double-precision, higher-precision library, or
   analytic result. GPU-only “looks plausible” is not a baseline.
2. **Tolerance is physical**, not a fixed ML-style `rtol=1e-3`.
3. **Never accept a speedup that breaks the reference** without an explicit,
   user-approved change of scientific method.
4. **Record non-determinism.** Atomic reductions and multi-block reduces can
   change bit patterns run-to-run; document when that is allowed.

## What to compare

| Check | Why |
|---|---|
| Absolute error | Small quantities near zero |
| Relative error | Large dynamic range |
| Problem-specific invariants | Energy drift, charge, hermiticity, symmetry, forces ≈ −∂E |
| Multiple block sizes | Catches reduction-order and shared-memory bugs |
| Debug vs Release | Catches UB and uninitialized memory |
| With/without fast-math | Documents whether `--use_fast_math` is safe |
| Dtype variants | FP32/FP64/mixed must be proven per quantity |

## Setting tolerances

Derive from:

- Machine epsilon × condition estimate × reduction depth
- Known library accuracy (e.g. math function ULP)
- Scientific acceptance (e.g. force components to `1e-7` Ha/Bohr for a given
  method) stated in the **spec or paper**, not invented ad hoc

If the project already defines helpers (`assert_arrays_close`, GoogleTest
matchers, regression fixtures), **use them**.

## Mixed precision

Allowed only when:

1. Reference comparison still passes for **all** required observables.
2. Iterative methods still converge to the same criterion.
3. Accumulation of sensitive scalars (total energy) uses sufficient precision.

Document which buffers are narrow and which accumulators stay wide.

## Fast math and FTZ

`--use_fast_math`, FTZ/DAZ, and approximate transcendentals can change
integrals and long MD drifts. Treat as an **optimization experiment** with
correctness re-check, not a default compile flag for science kernels.

## Test matrix (minimum)

For a new or heavily changed kernel:

- [ ] Reference match on a tiny deterministic case
- [ ] Larger case within agreed abs/rel bounds
- [ ] ≥2 launch geometries (block sizes)
- [ ] Release build
- [ ] Invariant check if applicable
- [ ] `compute-sanitizer` clean on the test (memcheck / racecheck as relevant)
