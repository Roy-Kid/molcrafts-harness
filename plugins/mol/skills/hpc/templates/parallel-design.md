# Parallel design worksheet (CPU)

## Identity

- **Path / symbol:**
- **Scientific operation:**

## Loop structure

- **Parallel index:**
- **Reduction index:**
- **Inner sequential work:**

## Strategy

| Level | Plan |
|---|---|
| SIMD | auto-vec / xsimd / none |
| OpenMP | construct + schedule |
| MPI | decomposition + comm |

## Data

- Layout (SoA/…):
- Shared mutable state:
- False-sharing risks:
- Allocations moved out of hot path?:

## Correctness

- Reference:
- Tolerances:
- Thread/rank matrix to run:

## Performance

- Baseline command:
- Success metric:
