# SIMD and data layout

## Layout

- **SoA** for particle and grid fields streamed in hot loops.
- Align allocations when using aligned loads (64 B cache line; 32/64 B SIMD).
- Avoid false sharing: pad thread-local accumulators to cache lines
  (`alignas(64)`).

## Vectorization hygiene

- Contiguous unit-stride access on the vectorized axis
- Minimal aliasing (`restrict` / clear index spaces)
- Branch-free inner loops (`select` / masks) when profitable
- Pull invariant computations out of the loop

Compiler reports:

- GCC: `-fopt-info-vec-missed`
- Clang: `-Rpass-missed=loop-vectorize`

## Explicit SIMD (when auto-vec fails)

Prefer project-declared SIMD libraries from `CLAUDE.md` / notes. Common
portable patterns:

- Explicit SIMD headers only in hot translation units.
- Avoid global compile defs that change expression-template storage and break
  views unless the project has validated them.
- `batch<T>` width is platform-dependent; write width-agnostic loops.
- Horizontal sum: store to array + scalar add if a free `hadd` is unavailable.
- Guard singular points before `sqrt`/`erf` with masked selects.

## Build flags

- Prefer **`-march=native`** (or a project-chosen microarch) on **host C++**
  only when the binary is not cross-built for heterogeneous login/compute.
- Never pass host march flags into device compilers unintentionally
  (use language generator expressions in CMake).

## When not to hand-vectorize

- The loop is not hot (timeline profile).
- Vendor BLAS/FFT already owns the work.
- Complexity would obscure a subtle numeric bug more than it gains.
