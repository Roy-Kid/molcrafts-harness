# Memory and layout

## Hierarchy (fast → slow)

| Level | Typical use in science kernels |
|---|---|
| Registers | Hot scalars, small tiles, loop carries |
| Shared memory / smem | Block tiles, stencils halos, scratch reductions |
| L1/L2 cache | Re-read neighbor lists, density grids, matrix panels |
| Global (HBM/GDDR) | Primary arrays: coords, forces, matrices, grids |
| Host | I/O, setup, rare control — never per-iteration bulk |

## Layout defaults

- Prefer **SoA** for large particle/grid arrays that warps stream contiguously
  (`x[i]`, `y[i]`, `z[i]` rather than `pos[i].x`).
- Prefer **structure-of-arrays of small structs** only when every field is
  always touched together and size stays aligned.
- **Tile** matrices and grids to match shared-memory budgets and bank width.
- Pad leading dimensions to avoid 32-bank conflicts and improve coalescing
  (often multiples of 32 or 128 bytes).

## Coalescing

- Consecutive threads should touch consecutive addresses (or a short
  strided vector load pattern the hardware merges).
- Neighbor-list gathers are irregular: stage indices, sort/bin by cell, or
  use shared tiles of positions to cut repeat global loads.
- Avoid array-of-structs of 3 doubles if only one coordinate is needed in a
  pass.

## Shared memory

- Load a **tile**, `__syncthreads()`, compute, write back.
- For stencils: interior + halo; size tiles so halo overhead is amortized.
- Bank conflicts: consecutive threads → different banks; pad if stride is a
  multiple of 32 banks.

## Multi-buffer and residency

- **GPU-native** means intermediate frames/densities/Fock builds stay device-side
  across iterations.
- Overlap **H2D/D2H** with compute only for true boundary I/O; never stage the
  whole state through host each step.
- Prefer async copies + streams when pipeline stages are independent.

## Precision storage vs compute

- Store in the precision required by the science (often FP64 for energies).
- Mixed precision (FP32 accumulate, FP64 residual) only with a correctness
  case proving invariants still hold (`numerical-correctness.md`).

## Checklist before claiming “memory bound”

1. Achieved bandwidth vs peak (Nsight Compute).
2. Bytes loaded / useful FLOP (arithmetic intensity).
3. L2 hit rate and uncoalesced transactions.
4. Local memory spills (register pressure).
