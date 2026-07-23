# SIMT design for scientific workloads

CUDA executes in a **SIMT** model: warps of threads run the same instruction
stream. Designing a kernel means assigning work to **thread**, **warp**,
**block**, and **grid** levels explicitly.

## Mapping checklist

For every non-trivial kernel:

1. **Task dimension** — independent units of work (one atom, one cell, one
   shell quartet batch, one matrix tile, one quadrature point set).
2. **Cooperative dimension** — work that shares data or produces a partial
   result (tile of a stencil, warp reduction over neighbors, block-wide GEMM
   fragment).
3. **Reduction dimension** — where values combine (energy, force components,
   histogram bins, residual norms).
4. **Grid dimension** — how many independent tasks run concurrently.

Reject “one thread = one heavy task with huge per-thread state” unless
registers/shared memory and occupancy analysis justify it.

## Pattern → typical mapping

| Pattern | Thread | Warp | Block | Grid |
|---|---|---|---|---|
| elementwise / map | 1 element (or small vector) | vectorized load/store | tile of elements | cover N |
| reduction | partial sum | warp shuffle reduce | shared + block reduce | segment or whole array |
| segmented reduction | item in segment | segment partials | multi-segment tile | segments |
| scan | inclusive/exclusive item | warp scan | block scan + upsweep | multi-block scan |
| stencil | 1 (or few) output cells | halo reuse in warp | tile + halo in shared | domain tiles |
| dense matrix | 1 result element or MMA lane | tensor/warp tile | CTA tile | tiles of C |
| sparse matrix | 1 row / 1 nonzero group | row-warps | row panel | rows/panels |
| batched small matrix | lane in tiny GEMM | one matrix / warp | batch tile | batches |
| quadrature | 1 point or point-group | points sharing geometry | shell/cell block | shells/cells |
| pair interaction | 1 pair or 1 i-particle | neighbor chunk | cell or i-block | particles/cells |
| neighbor interaction | 1 i or 1 (i,j-tile) | neighbor tile | cell pair | cells |
| irregular screened tasks | 1 task from compacted list | task batch | block of tasks | compacted grid |
| iterative solver | vector element / row | SpMV warp | vector chunk | iterations host-driven |
| spectral transform | FFT element / pencil | shared FFT | batch FFT | batches / pencils |

## Granularity rules of thumb

- **Too fine:** one thread does almost nothing → launch/overhead bound.
- **Too coarse:** one thread holds a whole quartet/atom neighborhood with
  deep branching → divergence, register pressure, idle lanes.
- Prefer **warp-cooperative** for variable-length neighbor or primitive loops.
- Prefer **block tiles** when data reuse exceeds register file.
- Use a **compacted task list** when screening drops most candidates
  (see `reductions-and-irregular-work.md`).

## Divergence and balance

- Branch on **warp-uniform** predicates when possible (sort/bin by type).
- For mixed angular momentum / cutoffs, **specialize kernels** or batch by
  class instead of one mega-kernel with deep `if`.
- Measure load imbalance: max/mean thread time; fix with persistent threads,
  work queues, or re-binning — not only with larger blocks.

## Anti-patterns

- Direct port of OpenMP `for` with `threadIdx.x = i` and heavy per-i work.
- Host-side loops launching one tiny kernel per task.
- Atomically updating a single global total from every thread every step.
- Ignoring alignment and assuming AoS particle structs will coalesce.
