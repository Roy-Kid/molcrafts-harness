---
name: hpc
description: "Design, implement, validate, and optimize CPU HPC scientific code with OpenMP, MPI, SIMD, cache-aware layouts, numerical references, and profiler-driven one-change experiments. Free-form: OpenMP / SIMD / MPI / vectorize / CPU HPC / cache optimize. Sibling of /mol:cuda (GPU). Not a QC theory skill."
argument-hint: "[path | module]"
---

> **Codex:** Read `../CODEX.md` before executing this shared workflow. Claude Code follows the workflow directly.

# /mol:hpc — CPU scientific high-performance computing

Design and optimize **CPU** scientific code: OpenMP, MPI, SIMD, and
cache-aware algorithms. Sibling **`/mol:cuda`** owns GPU-native SIMT work.
Acceptance evaluation of `scientific` / `performance` criteria is
**`/mol:perf`**.

Domain formulas stay in specs/notes; this skill owns **parallel CPU method**.

## Core principles

1. **Correctness first.** Parallel/SIMD paths match serial or reference within
   science-derived tolerance.
2. **Measure first.** Profile before parallelizing; re-measure after each change.
3. **One primary change per experiment.** Correctness → benchmark → keep/revert.
4. **Levels:** instruction (SIMD) → thread (OpenMP) → node (MPI).
5. Prefer validated libraries (BLAS, FFTW, vendor math) when they fit.

## Gate: parallel design before heavy edits

For non-trivial hot paths, answer before rewriting
(`templates/parallel-design.md`):

| Question | Must answer |
|---|---|
| Scientific operation | What is computed? |
| Hot loop dimensions | Parallel index? Reduction index? |
| Independence | Race-free without sync? |
| Reduction / atomics | How are partials combined? |
| Layout | SoA vs AoS, alignment, false sharing |
| SIMD strategy | auto-vectorize vs explicit SIMD |
| Thread schedule | static / dynamic / guided — why |
| MPI ownership | decomposition, ghosts, collectives |
| Why not serial + compiler | What limits the current binary |

## Workload patterns

```text
elementwise | reduction | stencil | dense / sparse linear algebra
neighbor / pair loops | screened irregular tasks
batched small matrix | iterative solver | spectral (FFT)
```

See `references/parallel-patterns.md`.

## Procedure

### 1. Scope

Read `CLAUDE.md` → `mol_project:` and notes. Discover CPU backend paths from
the project layout. Identify hot paths (forces, neighbors, integrators,
integrals, grids, solvers).

### 2. Correctness baseline

Serial or trusted reference; invariants
(`references/numerical-correctness.md`). `OMP_NUM_THREADS=1` and multi-thread
both pass.

### 3. Performance baseline

Hot-region wall time; record threads, problem size, dtype, CPU, build flags.

### 4. Experiment loop

Same NVIDIA-derived discipline as `/mol:cuda`, CPU-flavored
(**CC-BY-4.0 AND Apache-2.0** provenance; no TileGym content):

```text
LOOP:
  1. Apply ONE primary change (schedule, SIMD, layout, MPI overlap, …).
  2. Correctness (serial + threaded) → FAIL ⇒ revert.
  3. Re-benchmark same problem size / flags.
  4. Log (`templates/experiment-log.md`).
  5. keep if clear stable gain; else revert / stop.
```

### 5. Review mode

Missing parallelism, races, reduction/false-sharing, SIMD blockers,
hot-loop allocations, MPI over-sync. Report
`[SEVERITY] file:line` (`parallelism | vectorization | memory | mpi | numeric`).

### 6. Implementation mode

Design answers → implement → validate → report speedup vs baseline thread counts.

## Project-local rules

Read project harness for concrete constraints (SIMD library versions,
forbidden global flags, path layout). Do not invent Atomiverse-only
rules as universal defaults — put project decisions in
`$META.notes_path` / CLAUDE.md.

## References (this skill directory)

| File | Role |
|---|---|
| `references/parallel-patterns.md` | OpenMP / MPI / SIMD map |
| `references/simd-and-layout.md` | Vectorization and SoA |
| `references/numerical-correctness.md` | References and tolerances |
| `references/profiling.md` | CPU profiling checklist |
| `templates/parallel-design.md` | Design worksheet |
| `templates/experiment-log.md` | keep/revert log |

## Guardrails

- Does not replace `/mol:cuda` for GPU kernels.
- Does not author HF/DFT theory.
- No optimization without a correctness path.
- Does not replace `/mol:perf` for acceptance-ledger evaluation.

## Provenance

Keep/revert experiment loop adapted from NVIDIA
`tilegym-improve-cutile-kernel-perf` (**CC-BY-4.0 AND Apache-2.0**),
rewritten for CPU scientific HPC.
