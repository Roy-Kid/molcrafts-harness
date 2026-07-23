# CUDA library selection

**GPU-native ≠ rewrite every BLAS call by hand.** It means primary data and
iteration stay on device, using the best maintained implementation.

## Prefer libraries when the op matches

| Need | First choice |
|---|---|
| Dense GEMM / GEMV / batched small GEMM | cuBLAS, cuBLASLt |
| Dense factorizations, eigensolvers | cuSOLVER |
| Sparse SpMV / SpMM / formats | cuSPARSE |
| Device-wide reduce / scan / select / sort | CUB |
| Thrust-style algorithms on device | Thrust (often CUB underneath) |
| Tensor-core heavy GEMM/conv structure | CUTLASS (when shapes justify) |
| FFT / spectral methods | cuFFT |
| Alloc, streams, events, graphs | CUDA Runtime / Driver |

## When custom kernels are justified

- Fusion that libraries cannot express without huge temp traffic
- Irregular science patterns (screened shell work, neighbor force with
  Newton third-law, specialty quadratures)
- Layout constraints forced by the rest of the code that library APIs fight
- Proven profiler evidence that a library launch sequence is the bottleneck

## Decision procedure

1. Name the mathematical operation in standard terms (GEMM, SpMV, reduce, …).
2. If a CUDA-X primitive fits **without** harming numerics → use it.
3. If partial fit → library for the dense core + custom for the irregular rim.
4. Only then design a full custom kernel (`templates/kernel-design.md`).

## Anti-patterns

- Reimplementing GEMM “to learn CUDA” inside production science paths.
- Pulling results to host to call CPU BLAS inside the SCF/MD loop.
- Mixing many tiny library launches when one fused custom kernel (or CUDA
  Graph) would cut launch overhead — decide with Nsight Systems.

## Version and determinics

- Pin library behavior expectations in tests (especially reductions).
- Be aware some library paths are non-deterministic across versions/GPUs;
  lock criteria to scientific tolerances, not bit-identical GPU dumps,
  unless the project requires bit-reproducibility.
