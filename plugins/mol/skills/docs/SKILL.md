---
name: docs
description: Mode A docstring/API fix-up (auto after /mol:impl on public surface; free-form 补文档/missing docs). Mode B narrative tutorial (tier C — 写教程 only, never auto from impl). Load this skill; don't invent docs in bare chat.
argument-hint: "[path, spec slug, or feature name] [mode:A|B]"
---

> **Codex:** Read `../CODEX.md` before executing this shared workflow. Claude Code follows the workflow directly.

# /mol:docs — Documentation

Read CLAUDE.md → parse `mol_project:` (`$META`). Pick **one** mode.

## When

| Trigger | Mode |
|---|---|
| `/mol:impl` § 3c — public surface in diff | **A** (auto) |
| 补文档 / docstring / bare public API | **A** |
| 写教程 / tutorial | **B** (never from impl) |
| No public symbols + no ask | skip |

Missing `$META.doc.style` → skip once; do not invent a style.

## Mode A — audit + apply

Delegate `documenter` (audit). Style from `$META.doc.style` (`google` / `rustdoc` / `jsdoc-tiered` / `doxygen` — details in `agents/documenter.md`).

Check public symbols: required tier; units if `science.required`; matches impl; no dangling refs. Findings: `emoji file:line — msg` + `Fix:`.

**Apply** docstring/comment-only `Fix:` lines. Re-audit touched symbols. Chain scope = caller paths; zero public symbols → one-line no-op.

## Mode B — tutorial

Delegate `documenter` (tutorial). Collect: related spec, impl files, existing docs, real runnable example. Don't invent missing APIs/artifacts.

Rules: problem + intuition first; define symbols before use; concrete example; `$...$` / `$$...$$` math. Science topics → two-part structure (textbook derivation ≡ code) per `documenter.md`.

## Guardrails

- Never mix A/B. Mode B never auto from write chains.
- Mode A behavior-preserving only; renames → `/mol:refactor` or `/mol:debug`.
