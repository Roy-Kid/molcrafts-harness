---
description: Batch-implement a chain of specs from start to finish. Given a spec prefix, discovers all matching specs in `.claude/specs/` sorted by numeric suffix, then hands the chain to Claude Code's `/goal` built-in so iteration persists across turns until every spec reaches a terminal status. Each spec gets `/mol:impl` + `/mol:commit`; all gating, TDD, simplify, and verdict logic lives in `/mol:impl`. Never stops to ask questions.
argument-hint: "<spec-prefix>"
---

# /mol:impl-all — Batch Spec Chain Driver

Drive a spec chain (`<base>-01-<phase>`, `<base>-02-<phase>`, …) to completion by handing the iteration to Claude Code's `/goal` built-in. The skill itself only discovers the chain, validates it, and constructs the completion condition; `/goal` handles cross-turn persistence, live progress (elapsed / turns / tokens), and termination. All gating, testing, simplifying, and status advancement remains `/mol:impl`'s job.

```
/mol:impl-all morse-bond
→ finds morse-bond-01-potential, morse-bond-02-gradient, morse-bond-03-optimization
→ /goal "for each spec in chain, run /mol:impl then /mol:commit; stop when all are terminal"
→ /goal keeps Claude working across turns until completion condition is met
→ skill prints final verdict table
```

**Never asks questions.** Fully autonomous — the `/goal` substrate keeps the work going across turns; the skill itself never loops in-place.

---

## Procedure

### 1. Discover the chain

Read `CLAUDE.md` → parse `mol_project:` (`$META`); else emit adoption hint and stop.

Scan `$META.specs_path` (default `.claude/specs/`) for files matching `<prefix>-<NN>-<phase>.md` where `<NN>` is a two-digit number. Include a bare `<prefix>.md` at position 00 if present. Sort ascending by `<NN>`.

At least 1 spec must exist. If none: *"no specs matching '<prefix>' found"* and stop.

Print the chain:

```
[mol:impl-all] chain: morse-bond (3 specs)
  01-potential      status: approved
  02-gradient       status: approved
  03-optimization   status: approved
```

Any spec with `status: draft` → refuse and stop (*"approve draft specs first: <list>"*). Any spec already at `done` or `code-complete` is included in the chain table but skipped during the `/goal` step (the completion condition treats it as already-terminal).

### 2. Hand off to `/goal`

Issue a single `/goal` invocation whose **completion condition** is the chain reaching terminal status across all specs. Construct it from the discovered chain — do not hard-code spec names. Template:

```
/goal Drive spec chain <prefix> to completion.

Plan:
  For each spec in this order, run `/mol:impl <slug>` and then `/mol:commit`:
    - <slug-01>
    - <slug-02>
    - <slug-03>
    …

Per-spec rules:
  - `/mol:impl` owns every gate (stage gate, science gate, scope classification,
    TDD, simplify, acceptance criteria, status advancement). Do not duplicate.
  - After `/mol:impl` exits, advance based on the spec's terminal state:
      • done            → `/mol:commit -m "feat(<base>): implement <phase> (<NN>/<total>)"`,
                          then move to the next spec
      • code-complete   → `/mol:commit` with whatever message `/mol:impl` parked it under,
                          then move to the next spec
      • approved / in-progress (no advance) → STOP the goal; do not skip to the next spec

Completion condition (any of):
  - Every spec in the chain is at status `done` or `code-complete`, AND the final
    verdict table has been printed (see step 3 of /mol:impl-all).
  - A spec failed to advance — stop, do not progress further.

Constraints:
  - Never ask the operator a question.
  - Never edit specs directly; only `/mol:impl` may advance status.
  - Never reorder the chain.
```

`/goal` keeps Claude working across turns until the completion condition is met. Its overlay panel shows elapsed time, turns, and token usage — the skill does not re-implement progress reporting.

### 3. Final verdict (printed as part of satisfying `/goal`)

Once every spec is terminal (or the chain has stopped), print the verdict table. This emission is part of `/goal`'s completion condition — without it, `/goal` keeps running.

Show one row per spec with its terminal status. For every spec at `code-complete`, attribute the parking reason to a specific evaluator so the operator knows what to run next (or whether `/mol:close --manual` is appropriate).

```
═══ [mol:impl-all] chain verdict ═══

  morse-bond-01-potential      done
  morse-bond-02-gradient       done
  morse-bond-03-optimization   code-complete   owes: /mol:bench  (2 perf criteria)

  2 done, 1 parked, 0 failed
```

After the table, if any spec parked, print the chain-level **closing recipe** once (don't repeat per spec):

```
PARKED specs require runtime-evaluator verification before they
self-delete. To finish closing the chain:

  - Run each owed evaluator on its spec (e.g. `/mol:bench
    morse-bond-03-optimization`); evaluators flip their criteria to
    status: verified.
  - Re-run `/mol:impl <slug>` per spec — when every criterion is
    verified, the spec advances to done and is deleted.

Manual close (when no evaluator is available, e.g. mol_project.bench.repo
is unset):

  /mol:close <slug> --manual

  for each parked spec. Operator asserts the pass_when conditions
  are met; the audit trail lands in the commit message.
```

Skip the recipe entirely if no spec parked (chain reached `done` end-to-end).

End-of-skill one-line summary: `/mol:impl-all: <N> done, <M> parked, <K> failed; chain <prefix>` (or `BLOCKED: <reason>` if step 1 / step 2 refused).

---

## Guardrails

- **Never ask questions.** Autonomous batch mode — `/goal` drives across turns; the skill reports at end.
- **Don't duplicate `/mol:impl`.** All gates, TDD, simplify, acceptance, and status logic belongs to `/mol:impl`. This skill only discovers, hands off to `/goal`, and reports.
- **Don't write the loop into the skill body.** `/goal` is the loop substrate. The skill issues *one* `/goal` invocation and exits its own procedure; iteration lives at the runtime layer.
- **Stop on stall.** The `/goal` completion condition treats "spec did not advance" as a stop — later specs may depend on it.
- **Commit every spec.** Each spec gets its own checkpoint (per the per-spec rules embedded in the `/goal` body) so the chain is reviewable mid-flight.
- **Print the verdict.** The final verdict table is part of `/goal`'s completion condition; without it the goal keeps running.
