# Kernel design worksheet

Fill **before** writing or heavily rewriting a CUDA kernel. Incomplete sheets
mean stop at design review.

## Identity

- **Name / path:**
- **Scientific operation:**
- **Caller / phase** (build vs launch / SCF iter / MD step):

## Data

| | Description | Shape | Dtype | Residence |
|---|---|---|---|---|
| Inputs | | | | host / device |
| Outputs | | | | host / device |
| Temporaries | | | | |

## Parallel structure

- **Independent task dimension:**
- **Cooperative dimension:**
- **Reduction dimension:**
- **Data reuse locations** (reg / smem / L2 / none):

## SIMT ownership

| Level | Owns | Notes |
|---|---|---|
| thread | | |
| warp | | |
| block | | |
| grid | | |

Proposed launch: `blockDim = …`, `gridDim = …` (or persistent / graphs).

## Layout and access

- **Array layout** (SoA / tiled / CSR / …):
- **Coalescing plan:**
- **Shared memory plan** (bytes/block):
- **Atomics?** where / expected contention:

## Risks

- Warp divergence:
- Load imbalance:
- Occupancy limiters (regs / smem):
- Numeric risks (reduction order, mixed precision, fast-math):

## Library alternative

- Could cuBLAS / cuSPARSE / CUB / cuFFT / … do this? **yes/no + reason**

## Why not CPU-style mapping

- Direct `one-thread-per-<task>` rejected/accepted because:

## Correctness plan

- Reference:
- Tolerances (abs/rel/invariant):
- Tests / sanitizer:

## Performance plan

- Baseline command:
- Primary metric (ms, GB/s, ns/atom, …):
- Success criterion:
