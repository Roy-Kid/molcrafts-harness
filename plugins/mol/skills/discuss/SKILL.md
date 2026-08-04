---
name: discuss
description: "Structured design discussion with Convergence pulse; converge → auto /mol:grill, or discard. Free-form: 该不该做/几种方案/should we/trade-offs — load this skill, not bare chat. Not for clear specs (/mol:spec), formed plans (/mol:grill), or decided rules (/mol:note). Read-only."
argument-hint: "<topic or question>"
---

> **Codex:** Read `../CODEX.md` before executing this shared workflow. Claude Code follows the workflow directly.

# /mol:discuss — Design Discussion

Read CLAUDE.md → parse `mol_project:` (`$META`).

Trade-offs *before* a spec. Exits: **converge** → `/mol:grill` (plan) or **discard** (no trace). Not `/mol:spec` (clear requirement), `/mol:grill` (plan already formed), `/mol:note` (decided rules).

## Procedure

### 1. Frame

One-sentence restatement (user's language). List code/specs/notes read. Vague → one clarifying question, stop.

### 2. Drive toward convergence

Each turn end with:

```
Convergence pulse
- Agreed: <settled>
- Open: <still open>
- My read: converging | diverging | stuck
```

Converge signals: user accepts; Open empty; two turns with no new Open.
Diverge: Open grows; reframes; incompatible alternatives without reduction.
Hard cap: **8 turns** → force Step 3 or 4.

### 3. Converge → `/mol:grill` (plan)

When converging and Open empty (or user defers opens out-of-scope):

1. One-paragraph requirement + short Context (alternatives + why this won) + paths from Step 1
2. *"converged — entering `/mol:grill`…"*
3. Auto-invoke `/mol:grill` plan mode (Skill tool / `../grill/SKILL.md`). Do not invoke `/mol:spec` (tier C).
4. Grill handoff: sharpened plan → user may 落盘 / 写 spec.

### 4. Discard

Diverging/stuck two turns, user changes mind, or 8-turn cap without convergence:

- one-sentence reason; write nothing; do not grill
- stable rule emerged → suggest `/mol:note` only

## Output

Frame + surface; per-turn pulse; converge → requirement + Context + grill; discard → reason.

```
/mol:discuss <topic>: converged → /mol:grill → (user) /mol:spec <requirement>
/mol:discuss <topic>: discarded (<reason>)
```

## Guardrails

- Read-only. Spec = `/mol:spec`. No silent `/mol:note`.
- Converge → auto `/mol:grill`; never auto `/mol:spec`.
- 8-turn cap.
