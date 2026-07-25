---
name: simplify
description: Hygiene + stage-aware backward-compat on the current diff (behavior-preserving, test gate). Auto from /mol:impl; free-form 整理代码/tidy/cleanup. Load this skill — don't hand-edit cruft in bare chat.
argument-hint: "[path or list of files]"
---

> **Codex:** Read `../CODEX.md` before executing this shared workflow. Claude Code follows the workflow directly.

# /mol:simplify — Apply Hygiene Cleanup

Read CLAUDE.md → parse `mol_project:` (`$META`). Read `$META.stage` (default `experimental`). Print `[mol] stage: <value>`.

Write-mode counterpart to `janitor` (read-only). See `plugins/mol/rules/agent-design.md` § "Producer vs reviewer".

## Stage gate (per `plugins/mol/rules/stage-policy.md`)

- `maintenance` — only: dead-import removal, debug-residue deletion, stale-`TODO` deletion *iff* the marker references already-removed code. Naming-drift / magic-literal / constant-extraction → `[skipped — stage: maintenance]`.
- `stable` — refuse to delete anything still referenced by `@deprecated` / `# DEPRECATED` (deprecation must run one full major version first).
- `beta` / `experimental` — full scope contract.

## Scope contract

**Apply** (provably behavior-preserving):

- delete unused import / unreachable branch / unused local
- delete commented-out code
- delete debug `print` / `console.log` / `dbg!`
- inline a magic literal with a named constant **already defined in the file** (no new constants)
- rename a local symbol per captured naming rule (e.g. `natoms` → `n_atoms`) **only** when local to one file and grep confirms no external caller
- whitespace / import-order fixes the formatter missed
- run the language-canonical formatter in fix mode on touched files, and auto-fix lints, per the table in `plugins/mol/agents/janitor.md` § *Language-canonical toolchains* — in scope only when mechanical and behavior-preserving; the Step 5 test gate is the safety net
- delete stale `TODO` / `FIXME` whose reference is dead code

**Refuse** (surface as "manual"):

- copy-paste duplication extraction → `/mol:refactor`
- function-too-long splits → `/mol:refactor`
- public-API renames → `/mol:refactor` with `pm` agent pre-check
- any finding `→ defer to <agent>` from `janitor`
- any finding without a captured rule citation → user runs `/mol:note` first; future run picks it up

## Procedure

### 1. Determine scope

- `$ARGUMENTS` if given, else `git diff --name-only`.
- If the working tree has unrelated uncommitted changes → invoke `/mol:commit` first (no ask), then continue on the post-commit diff / specified paths.

### 2. Snapshot test gate

Run `$META.build.check` and `$META.build.test`. Record passing list + pre-existing failures.

- **Regression gate for this skill's edits:** revert if you introduce *new* failures vs the snapshot (not "suite must be fully green before simplify starts").
- **Iron law (no silent debt):** pre-existing failures are **not** "ignore and move on." List them in the report as **priority debt**. If a failure sits in the simplify scope (touched files / same module) and is stage-allowed hygiene or a clear bug → fix it in this run (or hand to `/mol:debug` and stop). Never add skips or weaken tests to quiet them. Out-of-scope pre-existing red → name path + route (`/mol:debug …`) in the summary; do not omit.

### 3. Delegate to `janitor`

Invoke `janitor` agent on Step 1 scope. Capture findings + rule-capture suggestions + deferred-to-other-agent items verbatim.

### 4. Triage findings

For each finding:

- matches **apply** list → candidate for batch apply
- matches **refuse** list → label `manual: route to /mol:refactor (or /mol:debug)`, skip
- if `janitor` left a `Fix:` line → propose that exact patch. Multi-line / file-level reorg → out of contract, skip.

Show triage table:

```
[apply]    src/foo.py:42  unused import os               → delete line
[apply]    src/foo.py:88  debug print() residue          → delete line
[apply]    src/bar.ts:17  literal "#fff"                 → replace with TOKENS.surface (already in scope)
[manual]   src/baz.py:12  function 142 lines             → /mol:refactor (split)
[manual]   src/baz.py:55  copy-paste of foo.py:120-140   → /mol:refactor (extract)
[skipped]  src/qux.py:9   naming drift (no captured rule)→ /mol:note first, then re-run
```

**Do not wait for approval.** Apply every `[apply]` row automatically. `[manual]` / `[skipped]` are reported only.

### 5. Apply, verify, revert on regression

1. Apply minimal patch per finding (one Edit each when possible).
2. After **whole batch**, run `$META.build.test`.
3. If any Step-2-green test is now red → **revert entire batch** (`git checkout -- <files>`), tell user which finding was the suspected trigger. (Bisect is user's call.)
4. If green: run `$META.build.check`, then **run the language-canonical trio explicitly** even when `build.check` skips one — commands per the table in `plugins/mol/agents/janitor.md` § *Language-canonical toolchains*. Non-zero from any = test regression: revert batch, surface failing tool. At `maintenance` the trio is verify-only (no fix-mode formatter, no `--fix`).

Never partial-apply. Green-after-revert is the only acceptable failure mode.

### 6. Report

```
/mol:simplify: applied N hygiene fixes across K files
  - N_unused imports / debug residue / commented code
  - N_naming drift fixes (captured rules)
  - N_token-or-constant substitutions

Manual handoffs (M):
  - <finding> → /mol:refactor / /mol:debug
Suggested rule captures (S):
  - <suggestion> → /mol:note
```

Surface rule-capture suggestions as optional `/mol:note` follow-ups — do not block or wait.

End with a one-line summary: files touched, fixes applied, manual handoffs queued, tests still green.

## Guardrails

- **Behavior-preserving only.** Runtime/API/test-outcome changes → `/mol:debug` or `/mol:refactor`.
- **Whole-batch atomicity.** Regression reverts entire batch — no half-cleaned tree.
- **No new abstractions.** Only delete or rename. No new helpers / constants / modules.
- **No CLAUDE.md / `.claude/notes/` writes.** Rule capture is `/mol:note`'s job.

## Idempotency

Second run on same scope finds zero `[apply]` candidates; reports zero changes or re-surfaces the first run's manual / rule-capture handoffs.

## When to invoke

- **Mandatory from `/mol:impl`** — § 3 invokes this on the impl diff before docs/finalize. Single point where per-stage backward-compat is enforced. Fully automatic — no operator de-select.
- **Free-form (tier A)** — 整理代码 / 清理一下 / 去掉 debug / 收 diff / tidy / hygiene / cleanup / dead code / strip debug prints on the current uncommitted diff or named paths.
- **After `/mol:review`** — when the hygiene axis flagged apply-able findings.
- **Not for** structural splits, public API renames, or duplication extraction → those are `/mol:refactor`.
