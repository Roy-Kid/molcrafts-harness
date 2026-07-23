# Profiling and performance engineering

## Tools

| Tool | Use |
|---|---|
| CUDA events | Kernel/region elapsed time (always available) |
| NVTX | Mark ranges for Nsight Systems timelines |
| Nsight Systems | End-to-end: copies, sync, concurrency, launch gaps |
| Nsight Compute | Single-kernel roofline, memory, stalls, occupancy |
| compute-sanitizer | memcheck, racecheck, initcheck, synccheck |

## Baseline package (record every experiment)

- benchmark name / command
- problem size(s)
- data type(s)
- GPU model + driver/CUDA version when available
- baseline time
- optimized time
- correctness result (pass/fail + metric)
- speedup
- profiler evidence (metric or short quote)
- bottleneck class (memory | compute | latency | launch | transfer | atomic | imbalance)
- decision: **keep** or **revert**

Use `templates/experiment-log.md`.

## What to inspect

- Memory bandwidth achieved vs peak
- Arithmetic intensity / roofline position
- Occupancy **and** why (registers, smem) — high occupancy is not always better
- Register count and local-memory spills
- Coalescing / excessive sectors
- Cache hit rates
- Branch divergence / warp efficiency
- Atomic contention
- Kernel launch overhead and unnecessary `cudaDeviceSynchronize`
- Host–device transfers inside hot loops
- Load balance across SMs and warps

## Experiment discipline (NVIDIA-style loop)

Adapted from NVIDIA `tilegym-improve-cutile-kernel-perf`:

1. Establish correctness + performance baselines **without** code changes.
2. Change **one** primary factor per iteration.
3. Correctness must pass or the change is reverted immediately.
4. Re-benchmark under the same problem sizes and flags.
5. Keep only improvements that clear noise (prefer ≥2–5% with stable measurement).
6. Log every iteration.

## Anti-patterns

- Tuning shared-memory tile sizes before confirming the kernel is memory-bound.
- Chasing 100% occupancy while increasing spills.
- Optimizing a kernel that is 2% of wall time (profile the **timeline** first).
- Comparing Debug to Release or different problem sizes as if comparable.
- Claiming speedup from a single noisy run without warmup/repeats.

## Suggested order of attack

1. Nsight Systems: remove transfers, syncs, launch gaps.
2. Sanity: algorithm class and library choice.
3. Nsight Compute on the hottest kernel: memory vs compute.
4. Mapping / layout / reduction structure.
5. Micro-knobs (launch bounds, unroll, vector loads) last.
