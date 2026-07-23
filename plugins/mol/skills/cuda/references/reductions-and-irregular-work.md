# Reductions and irregular work

Scientific codes spend much of their time in **reductions** (energies,
residuals) and **irregular** tasks (screened integrals, neighbor lists,
sparse rows).

## Reductions

### Levels

1. **Thread-local** accumulate in registers.
2. **Warp** reduce with shuffles (`__shfl_down_sync`) — no shared needed.
3. **Block** reduce via shared memory + one warp finalize.
4. **Grid** reduce via atomics to device scalar, multi-block reduce, or
   CUB/`cub::DeviceReduce`.

Prefer **CUB / library reduce** for whole-device reductions unless the reduce
is fused into a larger kernel where fusion wins.

### Segmented reductions

Common in: per-atom energy, per-shell contributions, blocked sparse rows.

- One warp or block per segment when segment length is moderate.
- For highly variable lengths: load-balance with **sorted segment size** or
  **persistent threads** pulling from a work queue.

### Non-associativity

FP add is not associative. Document:

- Whether results may differ across block sizes / run-to-run.
- Whether the science requires deterministic accumulation order.
- Compare against a fixed-order CPU reference with tolerances that reflect
  reduction depth, not a single global `1e-6`.

## Scans

Prefix sums build offsets for compacted task lists and CSR row pointers.

- Use CUB `DeviceScan` / `BlockScan` unless fused logic requires custom scan.
- Two-pass: count → exclusive scan → scatter write.

## Neighbor and pair work

- Build neighbor lists with cell lists / Verlet; keep list construction and
  force evaluation as separate, profiled stages when either dominates.
- **Newton’s third law:** half-list vs full-list trades atomics vs extra
  compute; choose from measurements.
- Tile i-particles in shared memory; stream j-neighbors through registers.

## Irregular screened task lists

Electronic-structure and cutoff physics often discard most candidate tasks.

Recommended pipeline:

1. **Generate candidates** (shell pairs, cell pairs) with cheap bounds.
2. **Screen** into a compact list (predicate + scan + scatter).
3. **Launch over compacted list** so the grid is dense and balanced.
4. Optionally **bin by cost class** (angular momentum, estimated FLOPs) so
   warps stay uniform.

Avoid: one thread per raw quartet with early `return` on screen fail
(leaves warps mostly idle).

## Atomics

- Acceptable for sparse scatter (forces) when contention is low.
- Hot single-address atomics (one global energy from every thread) → use
  hierarchical reduction instead.
- Prefer privatized partials + final reduce when profiling shows atomic
  serialization.

## Load imbalance

Symptoms: low warp efficiency, high stall “not selected”, uneven SM time.

Mitigations: cost binning, work stealing / persistent kernel queue, split
heavy tasks across warps, separate kernels per class.
