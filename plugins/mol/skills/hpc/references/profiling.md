# CPU profiling checklist

## Tools

| Tool | Use |
|---|---|
| `perf stat` / `perf record` | Counters, hot functions |
| Compiler vec reports | Missed vectorization |
| `OMP_DISPLAY_ENV`, OMP tools | Thread placement |
| VTune / Score-P / TAU | Deep OpenMP/MPI |
| `cachegrind` / `perf` cache events | Locality |
| Roofline (manual or advisor) | Bound type |

## Record per experiment

- benchmark command
- problem size
- dtype
- CPU model + frequency governor notes if relevant
- `OMP_NUM_THREADS` / MPI ranks
- baseline time / optimized time
- correctness
- speedup
- bottleneck class (compute | memory | sync | mpi | imbalance)
- keep / revert

## Order of attack

1. Find the true hot region (not guess).
2. Fix algorithmic waste and excess allocations.
3. Improve locality / layout.
4. SIMD the proven inner loop.
5. OpenMP the outer independent dimension.
6. MPI / multi-node last for single-node-bound work.

## Anti-patterns

- Adding OpenMP to a memory-bound loop without fixing layout.
- Comparing Debug builds.
- Tuning thread counts on a noisy laptop as production truth.
