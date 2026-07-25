---
name: debug
description: "The bug loop — reproduce → diagnose → minimal-diff patch → verify, in one skill. Free-form: 修这个 / 为啥挂 / failing test / stack trace / segfault. `--diagnose-only` stops at the root-cause report and edits nothing (先诊断 / don't patch yet). Writes code; proceeds at every `mol_project.stage`. Not for new features — that's /mol:spec → /mol:impl."
argument-hint: "<bug description, error message, or failing test> [--diagnose-only]"
---

> **Codex:** Read `../CODEX.md` before executing this shared workflow. Claude Code follows the workflow directly.

# /mol:debug — The Bug Loop

Read CLAUDE.md → parse `mol_project:` (`$META`). Read `$META.stage`
(default `experimental`). Print `[mol] stage: <value>`.

One minimal loop for bugs: reproduce, diagnose, patch the smallest
surface, verify. It is deliberately *not* a degenerate `/mol:impl` — no
spec gate, no acceptance ledger, no design phase. A bug is a defect
against behavior that was already agreed; a feature is not.

`--diagnose-only` stops after the root-cause report and **edits
nothing** — for when you want to see the diagnosis before committing to
a patch, or hand the report to someone else.

`/mol:debug` is the **only** writing skill that proceeds at every stage —
bugs are always in scope. Stage tightens scope discipline at Step 3 per
`plugins/mol/rules/stage-policy.md`:

- `maintenance` — patch may not touch lines unrelated to the
  reproduction; no new abstractions; no rename of any symbol (even
  local) outside the immediate fix surface.
- `stable` — additive only by default; modifying an existing public
  signature requires a deprecation shim or explicit user approval.
- `beta` / `experimental` — standard scope discipline (smallest change
  that resolves the issue).

## Procedure

### 1. Reproduce

Run `$META.build.check` + `$META.build.test` (or the single-test form
when the failure is one specific test). Confirm the reported symptom.

Other failures discovered while reproducing are **not** ignored (iron
law): list them; fix them in this run if they share a root cause or
surface, otherwise report them as priority follow-ups with routes. Never
a silent baseline.

Cannot reproduce → say so, report what you ran and what you saw, and stop
before Step 3. Do not patch a symptom you have not observed.

### 2. Diagnose

If the conversation or `$ARGUMENTS` already contains a debugger report (a
block with **Root cause** / **Fix recommendation** / **Preventive
measure**), consume it directly — do **not** re-delegate.

Otherwise delegate to the `debugger` agent with the symptom from
`$ARGUMENTS`. It classifies (build / test / runtime), gathers evidence,
and returns:

- **Classification.**
- **Root cause** — one paragraph, `file:line` precise.
- **Fix recommendation** — what to change, not the change.
- **Preventive measure** — test category + assertion shape that catches
  a regression.
- (when evidence is inconclusive) **Open questions** — the specific
  evidence to gather before a fix is justified.

Render the agent's report verbatim; do not re-summarize it. Use it as the
plan for Step 3 — do **not** re-derive the diagnosis.

**Open questions present** → surface them and stop. **`--diagnose-only`**
→ stop here; go to § Output format.

### 3. Patch

Delegate the patch to the `implementer` agent: the debugger report as the
plan, the Step 1 reproduction (or the regression test below) as the RED
test, the smallest fix surface as the scope — bounded by the stage
discipline above.

- Touches architecture boundaries → read `$META.arch.rules_section` in
  CLAUDE.md first and pass it as the layer constraint.
- Root cause suggests a missing test → delegate to `tester` for a
  **unit** test under `tests/` (mirrored layout, single-function)
  **before** the patch (RED), then `implementer` (GREEN). No e2e under
  `tests/`; public-API lock-in goes to `regressions/` with hard-coded
  goldens only.
- **Type safety.** No escape-hatch top types (`any` / `Any` /
  `interface{}` / `dyn Any`); no dropping existing annotations.
  `implementer` enforces this; the Step 4 gate verifies. Exception:
  deserialization at a system boundary, narrowed immediately.

### 4. Verify

Full `$META.build.test` (no regressions) + `$META.build.check`
(format / lint). Both green before reporting success.

Still red after the patch → report the failure output; do not declare
the bug fixed and do not weaken the test to make it pass.

## Output format

Render the debugger report, then — unless `--diagnose-only` — what
changed and the gate results.

End with the F2 one-line summary:

- patched: *"root cause: `<one line>` — `<n>` files changed, `<test>`
  added, suite green."*
- `--diagnose-only`: *"diagnosis only, nothing edited — re-run
  `/mol:debug <bug>` without `--diagnose-only` to apply; it consumes the
  report above without re-running diagnosis."*

## Guardrails

- **`--diagnose-only` never edits.** Enforced here in the procedure, not
  just in the description: the run ends at Step 2.
- **Minimal diff.** The patch resolves the reproduction and nothing else.
  Refactoring that the fix reveals is routed to `/mol:refactor`, not
  smuggled in.
- **Never weaken a test to go green.** A failing assertion is fixed at
  the source or reported, never relaxed, skipped, or baselined.
- **Bugs only.** A request that turns out to need new behavior stops
  here and routes to `/mol:spec`.
