---
name: cuda
description: "Design, implement, validate, and optimize GPU-native CUDA C++ scientific kernels with explicit SIMT mapping, numerical references, CUDA-X libraries, and profiler-driven one-change experiments. Free-form: CUDA kernel / GPU-native / SIMT / optimize CUDA / ERI GPU / neighbor CUDA. Sibling of /mol:hpc (CPU). Not ML/PyTorch/cuTile; not a QC theory skill."
argument-hint: "[path | kernel | module]"
---

> **Codex:** Read `../CODEX.md` before executing this shared workflow. Claude Code follows the workflow directly.

# /mol:cuda — GPU-native scientific CUDA C++

Design and optimize **scientific** CUDA C++ kernels. Not ML, Transformer,
PyTorch, cuTile, Triton, or a single quantum-chemistry algorithm.

HF/DFT, MD, FEM, FDTD, and CFD are **application domains**. This skill owns
**GPU method**: SIMT mapping, memory layout, reductions, irregular work,
library choice, numerical reference, and profiler-driven iteration.

Sibling: **`/mol:hpc`** (CPU OpenMP / MPI / SIMD). Domain math (SCF,
integrals, XC, invariants) lives in project notes/specs — not here.
External acceptance evaluation of `scientific` / `performance` criteria is
**`/mol:perf`**, not this skill.

## Core principles

1. CUDA is **SIMT**. A kernel is not a CPU loop with `threadIdx` sprinkled in.
2. **Correctness first.** Performance never excuses wrong science.
3. **Profiler-driven.** Measure before and after; do not optimize by intuition.
4. **One primary change per experiment.** Re-verify correctness, re-benchmark, then keep or revert.
5. **GPU-native** means data and compute stay on device — not “refuse CUDA-X libraries.”

## Gate: SIMT design before code

Do **not** generate a non-trivial kernel until these are answered (worksheet:
`templates/kernel-design.md` next to this skill):

| Question | Must answer |
|---|---|
| Scientific operation | What quantity is computed? |
| Inputs / outputs | Buffers, shapes, dtypes, units |
| Independent task dimension | What can run with no communication? |
| Cooperative dimension | What needs shared memory / warp sync? |
| Reduction dimension | What aggregates across threads/warps/blocks? |
| Data reuse | Registers, shared, L2, texture |
| thread / warp / block / grid roles | Explicit ownership |
| Layout | SoA vs AoS, tiling, padding, alignment |
| Divergence / atomics / load imbalance | Present? Mitigated how? |
| Why not CPU-style mapping | Reject one-thread-per-task unless justified |

If unanswered → stop at design; do not emit `.cu`.

## Workload classification

Classify as one or more patterns (`references/simt-design.md`):

```text
elementwise | map | reduction | segmented reduction | scan
stencil | dense matrix | sparse matrix | batched small matrix
quadrature | pair interaction | neighbor interaction
irregular screened tasks | graph-like traversal
iterative solver | spectral transform
```

## Procedure

### 1. Scope and classify

Read `CLAUDE.md` → `mol_project:` and architecture notes. Identify CUDA
paths from the project (common: `src/cuda/`, `include/**/cuda/`). Classify
workload; fill kernel-design template.

### 2. Correctness baseline

CPU or high-precision reference; abs/rel + scientific invariants
(`references/numerical-correctness.md`). Note dtype and Debug/Release /
fast-math.

### 3. Performance baseline

CUDA events (+ NVTX when multi-kernel). Record problem size, dtype, GPU, time.

### 4. Library check

Prefer cuBLAS / cuBLASLt / cuSOLVER / cuSPARSE / CUB / Thrust / CUTLASS /
cuFFT when they fit (`references/library-selection.md`).

### 5. Experiment loop

Methodology adapted from NVIDIA `tilegym-improve-cutile-kernel-perf`
(CC-BY-4.0 AND Apache-2.0); TileGym/cuTile specifics removed:

```text
LOOP:
  1. Apply ONE primary optimization (or design change).
  2. Re-run correctness → FAIL ⇒ revert immediately.
  3. Re-benchmark vs current baseline.
  4. Log (`templates/experiment-log.md` or project sandbox).
  5. Decision:
       ≥5% faster + correct  → keep, new baseline
       2–5%                  → keep, lower priority next
       <2% or no gain        → keep optional; consider stop
       regression / fail     → revert
  UNTIL goals met, plateaus, or user stops
```

Occupancy is not the goal. Profiler evidence over intuition
(`references/profiling.md`).

### 6. Review mode

Scan for CPU-style mapping, host sync in hot paths, D2H/malloc in launch,
uncoalesced access, atomic hotspots, launch overhead. Report
`[SEVERITY] file:line` with category (mapping | memory | sync | numeric | library).

### 7. Implementation mode

Design answers → implement → reference tests → experiment loop → report
mapping, numeric agreement, speedup, profiler evidence.

## Project-local rules

Do **not** hardcode one repo’s paths. Read:

- `CLAUDE.md` / `AGENTS.md` for backend residency and lifecycle
- `$META.notes_path` for decided CUDA conventions
- project benchmarks/tests for how to measure

Domain math (ERI formulas, XC, SCF) stays in specs/notes or a domain skill.

## References (this skill directory)

| File | Role |
|---|---|
| `references/simt-design.md` | Patterns → thread/warp/block/grid |
| `references/memory-and-layout.md` | SoA, coalescing, shared, tiles |
| `references/reductions-and-irregular-work.md` | Reductions, scans, screened lists |
| `references/numerical-correctness.md` | References, tolerances, determinism |
| `references/library-selection.md` | CUDA-X vs custom kernels |
| `references/profiling.md` | Events, NVTX, Nsight, sanitizer |
| `templates/kernel-design.md` | Mandatory design worksheet |
| `templates/experiment-log.md` | keep/revert log |

## Guardrails

- No TileGym / cuTile / PyTorch / Transformer assumptions.
- Not HF/DFT-only; those are example workloads.
- No non-trivial kernel without SIMT design answers.
- No “optimize first, check later.”
- Mixed precision only with evidence.
- Does not replace `/mol:perf` for acceptance-ledger evaluation.

## Provenance

Experiment loop adapted from NVIDIA Agent Skill
`tilegym-improve-cutile-kernel-perf` (**CC-BY-4.0 AND Apache-2.0**).
TileGym paths, cuTile knobs, and AI-kernel playbooks removed and rewritten
for general scientific CUDA C++.
