---
name: grill
description: "One-question-at-a-time plan/spec interview (recommended answers, Grill pulse). Free-form 盘问/grill when a plan exists; auto from discuss (plan) and spec (spec-audit). No plan → /mol:discuss. Never auto /mol:spec or /mol:impl. Read-only."
argument-hint: "[mode:plan|spec-audit] <plan, requirement, or slug>"
---

> **Codex:** Read `../CODEX.md` before executing this shared workflow. Claude Code follows the workflow directly.

# /mol:grill — Plan / Spec Interrogation

Read CLAUDE.md → parse `mol_project:` (`$META`).

Relentless interview: one focused question per turn, each with a recommended answer, until the decision tree is empty. Not `/mol:discuss` (whether/what) and not `/mol:spec` (writes the artifact). Chain: discuss → **grill (plan)** → user ignites spec → **grill (spec-audit)** → impl.

## Mode

| Mode | When | Input |
|---|---|---|
| **plan** (default) | discuss converge, free-form grill | plan / requirement (+ optional Context) |
| **spec-audit** | `/mol:spec` after persist | slug + paths of written spec / acceptance |

Explicit `mode:` wins. Infer `spec-audit` only when caller is post-persist `/mol:spec` or args name an existing slug under `$META.specs_path`.

## Procedure

### 1. Frame

**plan.** Restate in one sentence (user's language). List code/spec/notes surface read. No plan (open topic / "should we…?") → `/mol:discuss`; do not invent a plan.

**spec-audit.** Restate `spec under audit: <slug>`. Read Design (incl. Reuse), Files, Tasks, Out of scope, Testing, acceptance. Missing file → stop; do not invent.

### 2. Decision tree

Enumerate open decisions dependency-first. Hold internally — do not dump as a wall of questions. **plan:** implied by free-form plan. **spec-audit:** gaps in the written artifact only; do not re-litigate clear decisions unless they conflict with code.

### 3. Interrogate — one question per turn

Each turn:

- Exactly one focused question.
- Always recommend an answer + one-line rationale grounded in `$META` / code.
- If the codebase answers it, resolve yourself and move on.
- Wait for the user; fold the answer in (may close or open nodes).

End every turn:

```
Grill pulse
- Resolved: <settled decisions + chosen answer>
- Open: <still unresolved>
- Next: <single upcoming question>
```

If Open grows two turns with no net reduction → under-formed: offer `/mol:discuss` (plan) or re-spec (spec-audit).

### 4. Converge

Open empty (or explicitly deferred out-of-scope):

**plan → hand off to `/mol:spec`**

- Sharpened plan (user's language) a fresh `/mol:spec` can consume
- Decisions log: `question → answer → why`
- Paths from Step 1

Tell user: say 落盘 / 写 spec / `spec this` (or `/mol:spec …`). Do **not** invoke `/mol:spec` or `/mol:impl` (tier C).

```
audit_result: n/a (plan mode)
```

**spec-audit → return result (caller writes)**

- Decisions log
- `audit_result: clean` — written artifact matches resolved decisions
- `audit_result: supersede_needed` — short supersede payload (Design / Tasks / Files / acceptance deltas for `/mol:spec` + `spec-writer`)

Never write specs or source. On `clean`: ready for `/mol:impl <slug>`.

### 5. Redirect

Premise dissolves (wrong feature / reopens whether-what):

- **plan:** one sentence → `/mol:discuss`
- **spec-audit:** one sentence → suggest `/mol:discuss`; leave files on disk

## Output

- Frame + surface read
- Per turn: question + recommendation + pulse
- Converge plan: sharpened plan + Decisions + handoff
- Converge audit: Decisions + `audit_result`
- Redirect: one-line reason

F2:

```
/mol:grill plan: sharpened (<N>) → /mol:spec <plan>
/mol:grill spec-audit <slug>: clean (<N>) → /mol:impl <slug>
/mol:grill spec-audit <slug>: supersede_needed (<N>) → caller supersedes
/mol:grill: redirected → /mol:discuss (<reason>)
```

## Guardrails

- Read-only on source and specs. Persistence = `/mol:spec`; rules = `/mol:note`.
- One question per turn; always recommend; self-answer from code first.
- No plan / no spec surface → redirect (Step 1).
- Never auto-invoke `/mol:spec` or `/mol:impl`.
