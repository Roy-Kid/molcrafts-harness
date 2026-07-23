---
name: impl
description: One-spec TDD loop → verify → simplify → docs Mode A (public surface) → auto close. Chain/prefix → /mol:impl-all. Fully agent-driven; never asks the operator to close.
argument-hint: "<slug | spec-prefix | feature description>"
---

> **Codex:** Read `../CODEX.md` before executing this shared workflow. Claude Code follows the workflow directly.

# /mol:impl — Spec Tasks Orchestrator

Read CLAUDE.md → parse `mol_project:` (`$META`); else emit adoption hint and stop. Print `[mol] stage: <value>`.

`/mol:impl` orchestrates a **single** spec's Tasks checklist: pre-flight → iterate each task (RED → GREEN → tick) → verify → simplify → docs Mode A (public surface) → finalize (acceptance ledger + commit + auto evaluators + auto-close). `/mol:simplify`, `/mol:docs` Mode A (when applicable), and `/mol:close` run automatically every pass — never prompt the operator for them. All stage-policy decisions for hygiene/legacy delegate to `/mol:simplify`.

**Iron law (CLAUDE.md Design preferences):** if impl work discovers a pre-existing failure, Design anti-pattern, or broken invariant in the touched/dependent surface → **prioritize** fix (local) or **stop** and route to `/mol:fix` / `/mol:refactor` / supersede. Never ignore, baseline-away, or land the feature on top of known rot.

**Chain / batch:** if `$ARGUMENTS` matches a chain prefix with ≥2 specs (`<prefix>-NN-*` under `$META.specs_path`), **forward immediately to `/mol:impl-all <prefix>`** and exit. Prefer `/mol:impl-all` as the default user-facing implement command for multi-spec work.

Orchestration mode per `plugins/mol/rules/model-policy.md`: this loop plans, routes, gates, and verifies — it never authors production source. Tests come from `tester`, production code from `implementer`.

---

## 1. Pre-flight

### 1a. Scope & branch

If chain prefix detected (≥2 matching specs) → invoke `/mol:impl-all` and stop.

Classify against `$META.arch.style`: SMALL (<3 files, existing pattern) / MEDIUM (3–8 files, new pattern) / LARGE (new top-level concept).

LARGE on a monolithic spec → re-invoke `/mol:spec` to produce a chain, then `/mol:impl-all` on the chain — no user prompt.

When slug matches `<base>-<NN>-<phase>` or scope is LARGE: if on default branch, checkout `feat/<base>` (create if needed). No prompt. Silent otherwise.

State classification. SMALL skips to § 2.

### 1b. Spec gates

Read `{$META.specs_path}{slug}.md` + `{$META.specs_path}{slug}.acceptance.md`. Refuse if either missing.

**Status gate:**
- `draft` → refuse (re-run `/mol:spec`).
- `approved` → first run.
- `in-progress` → resume (run 1c).
- `code-complete` → skip to § 4.
- `done` → warn (should be deleted).

**Stage gate:** `maintenance` refuses unless spec has `kind: bugfix`.

**Acceptance gate:** parse `criteria:` from acceptance frontmatter. Each `type: code | runtime` criterion must map to ≥1 task. Surface the ledger. Already-`verified` criteria are not re-traced unless 1c finds the test path gone.

### 1c. Resume sync

For every unchecked task, cheap inspection (grep symbol, glob file, run `$META.build.test_single`). Show verdict per task:

```
[done — verified]      Implement Foo in src/foo.py        → tick
[no evidence]          Wire Bar into Service              → leave
```

Replace `- [ ]` with `- [x]` for verified tasks in one batch. Report: *"N of M tasks already done; resuming from X."* If all done → skip to § 3.

Set `status: in-progress`.

### 1d. Architecture check (MEDIUM/LARGE)

Verify placement against `$META.arch.rules_section`. LARGE → delegate to `architect`.

---

## 2. Core loop — iterate Tasks

For each unchecked task, in order:

### 2a. TDD (RED)

First **Write failing tests** task → delegate to `tester` agent (write-mode). Unit tests **only** under `tests/`, path mirroring `src/` (`src/foo/boo.py` → `tests/test_foo/test_boo.py`), types mirrored (`FooClass` → `TestFooClass`), **single-function** tests — no e2e under `tests/`. Categories: basics, edge cases, immutability, domain validation (if `$META.science.required`) with hard-coded goldens. Run `$META.build.test_single`; confirm red. **Tick immediately.**

### 2b. Implement (GREEN)

Task targets `regressions/` (public-API regression example) → test artifact only: delegate to `tester` (write-mode, § Regression examples). Must hard-code reference values (offline third-party capture if needed — **no** live third-party imports/subprocesses). Run standalone, tick on pass. `implementer` never writes it.

For each remaining task:
1. Delegate to `implementer` agent with: spec path, the task line, the RED test reference from 2a (command in `$META.build.test_single` form), the spec's Files section as scope, and the layer from 1d.
2. `verdict: green` → run `$META.build.test_single` yourself to confirm (never trust the self-report), then **tick that task's box** — ticking stays here; `implementer` never ticks.
3. `still-red` → re-delegate once with the failure output attached; still red after the retry → stop, re-invoke `/mol:spec` (supersede).
4. `blocked:` → surface the blocker verbatim and stop (missing RED test → run 2a for that symbol; spec ambiguity → `/mol:spec`).

Revert on regression is this skill's job (and `/mol:simplify`'s inside § 3); `implementer` never reverts.

Every line — production or test — satisfies `$META.build.check`. No escape-hatch types (`Any`, `any`, `interface{}`).

MEDIUM/LARGE: after impl tasks, re-delegate to `architect` for post-impl layer check.

---

## 3. Verify, simplify, docs

### 3a. Verify

Run in parallel: `$META.build.check` + `$META.build.test` (full suite) + the spec's `regressions/` example(s) standalone. A failing regression blocks finalize exactly like a failing unit test — the feature is not delivered until the regression reproduces its **hard-coded** reference values.

### 3b. Simplify

Invoke `/mol:simplify` on touched files. **Mandatory.** `/mol:simplify` decides: delete legacy (`experimental`) / shim (`stable`) / migration-note (`beta`) / leave (`maintenance`). Runs its own build/test gate; reverts on regression.

If revert → leave `in-progress`, surface trigger, attempt one `/mol:fix` cycle on the simplify regression; still bad → stop hard (resume via 1c on re-run).

If "Hygiene cleanup" task exists → tick it; else add one line recording simplify ran clean.

### 3c. Docs Mode A (public surface)

After simplify succeeds, decide whether public API documentation is owed:

**Public-surface heuristic** (any one → docs owed):

- scope was MEDIUM or LARGE, or
- touched production files add/change **exported** symbols — e.g. Python names in `__all__` or module-level public classes/functions (no leading `_`); Rust `pub` items in `lib.rs` / `mod` re-exports; TS/JS `export` at package entry; similar for other languages in `$META.language`.

When owed:

1. If `$META.doc.style` (or `doc:` block) is missing → one-line skip (`docs Mode A skipped — no mol_project.doc.style`) and continue to § 4.
2. Else **auto-invoke `/mol:docs` Mode A** on the touched public paths (Skill tool / read-and-execute `../docs/SKILL.md`). Never Mode B.
3. Docs applies docstring/comment fixes only; if it reports blockers that need code behavior changes → surface and continue finalize (do not block close on tutorial-grade polish).

When not owed → one-line skip (`docs Mode A skipped — no public surface in diff`).

Do **not** inline-delegate to `documenter` here — `/mol:docs` owns the audit+apply contract.

---

## 4. Finalize

Re-read spec + acceptance.

### 4a. Update acceptance ledger

For each `type: code | runtime` criterion, write back verdict (`verified` / `failed`) with `last_checked` date. Leave criteria of other types untouched.

### 4b. Decide status

All Tasks `[x]`, build green, every `code` / `runtime` criterion `verified` — any failing → leave `in-progress`, print remaining tasks + unmet criteria, stop.

All hold:
- Acceptance has only `code` / `runtime` criteria → **done** (§ 4c).
- Any other-typed criterion exists → **code-complete** (§ 4d).

### 4c. Done path

1. Mark `status: done`.
2. Invoke `/mol:commit` (gates on `/mol:ship commit`). Message: `feat(<scope>): <summary> (<slug>)`. BLOCK → leave `in-progress`, stop.
3. Delete spec, acceptance, INDEX entry.
4. Suggest `/mol:note` for non-obvious context.

### 4d. Code-complete path

1. Mark `status: code-complete`.
2. Invoke `/mol:commit` (same as done path). BLOCK → drop to `in-progress`, stop.
3. List the criteria left at `pending`, **grouped by evaluator owed** per the routing table in `plugins/mol/rules/evaluator-protocol.md` § *Type → owed evaluator*.
4. **Auto-evaluators then auto-close.** For each owed evaluator on pending non-`code`/`runtime` criteria, invoke it once (`/mol:perf`, `/mol:web`, …) when configured. Then invoke `/mol:close <slug>` (default mode) — no prompt. `/mol:close` re-checks, auto-attests remaining C criteria with `verified_by: agent-auto` when no evaluator can flip them, and deletes artifacts on success.
5. If close still fails (failed criteria / commit gate) → stop hard with the failure. **Never** ask the operator to close or pass `--manual`.
6. Never delete spec/acceptance/INDEX directly on this path — deletion is `/mol:close`'s job.

For chained specs, exit cleanly after commit + auto-close — don't start the next spec (that's `/mol:impl-all`'s job).

---

## 5. Summary

One-line F2 summary: scope, files changed, tests passing, resulting `status:` (`done` / `code-complete` with N pending / `in-progress` with N remaining), acceptance tally.
