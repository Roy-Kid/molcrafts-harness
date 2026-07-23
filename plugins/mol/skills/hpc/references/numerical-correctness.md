# Numerical correctness (CPU HPC)

## Rules

1. Parallel and SIMD results must match a **serial or reference** path within
   agreed tolerances.
2. Tolerances come from the **algorithm and quantity**, not a universal
   `1e-6`.
3. Thread count must not change scientific conclusions.
4. Document intentional non-associativity from parallel reductions.

## Required checks

| Check | Command / idea |
|---|---|
| Serial baseline | `OMP_NUM_THREADS=1` |
| Multi-thread | `OMP_NUM_THREADS=N` for N in {2,4,8,…} |
| MPI ranks | 1 rank vs multi-rank with same global problem |
| Debug vs Release | Catch UB |
| Reference library | e.g. libcint, BLAS, analytic |

## Invariants

When applicable: energy conservation windows, force = −∂E, density
normalization, hermiticity, symmetry of integrals.

## Reductions

Parallel FP reductions reorder sums. Compare with tolerances that scale with
problem size and condition; if bit-reproducibility is required, use
deterministic reduction trees and document the algorithm.
