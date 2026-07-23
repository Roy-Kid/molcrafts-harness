# CPU parallel patterns

## OpenMP

| Pattern | Typical approach |
|---|---|
| Uniform O(N) map | `#pragma omp parallel for schedule(static)` |
| Variable cost loops (neighbors) | `schedule(dynamic, chunk)` or taskloops |
| Reductions | `reduction(+:…)` or thread-local buffers + merge |
| Nested regions | Rare; prefer flattened loops |
| NUMA | First-touch init in the parallel region that consumes data |

### Force / energy accumulation

- Prefer thread-local force arrays or colored pair loops over heavy atomics.
- For Newton 3rd-law pair loops, privatize and reduce to avoid false sharing.
- Critical sections do not belong in inner MD/SCF loops.

## MPI

| Concern | Approach |
|---|---|
| Spatial MD | Domain decomposition + ghost halo exchange |
| Force reverse | Reverse comm for 3rd-law across ranks |
| Global scalars | `MPI_Allreduce` for E, T, P |
| Overlap | `Isend`/`Irecv` + compute on interior |
| Load balance | Rebalance when particles migrate |

Keep CPU backend free of CUDA types; MPI ranks own CPU memory.

## SIMD

See `simd-and-layout.md`. Order of preference:

1. Contiguous SoA + compiler auto-vectorization (`-O3 -march=native`)
2. Explicit portable SIMD (e.g. xsimd) on proven hot primitives
3. `#pragma omp simd` when the compiler misses a safe loop
4. Intrinsics only when measured necessary

## Pattern map

| Science pattern | Threading | SIMD focus |
|---|---|---|
| elementwise | parallel for | contiguous loads |
| reduction | parallel reduction | horizontal reduce at end |
| stencil | tiled parallel for | inner contiguous axis |
| neighbor/pair | dynamic or spatial decomp | pack j-tiles |
| screened tasks | compact list then parallel | bin by cost class |
| small batched GEMM | parallel over batch | vendor BLAS per batch |
| sparse row | parallel over rows | row length dependent |
| iterative solver | parallel SpMV + vector ops | BLAS-1/2 |

## Anti-patterns

- Parallelizing the outer loop that only runs for 4 shells while the inner
  does all the work (profile first).
- Sharing a non-reduced accumulator across threads.
- MPI per-atom messages instead of aggregated halo buffers.
- Expecting AoS `struct {x,y,z,type}` loops to vectorize well.
