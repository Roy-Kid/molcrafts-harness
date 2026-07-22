---
name: cancel
description: Cancel one molq job by id via molmcp. Requires MOLMCP_MOLQ_SUBMIT=1. Free-form: 取消作业/cancel job/scancel. Controlled mutation — confirm job_id first when ambiguous.
argument-hint: "<job_id>"
---

> **Codex:** Read `../CODEX.md` before executing this shared workflow. Claude Code follows the workflow directly.

# /molq:cancel — Cancel One Job

Controlled mutation through molmcp `cancel_job`. Cluster/scheduler come from the job store record.

## Preconditions

1. molmcp molq tools available.
2. **`MOLMCP_MOLQ_SUBMIT=1`** (same opt-in as submit). Disabled → instruct user; do not shell `scancel` unless they explicitly want CLI outside MCP.
3. `job_id` required (molq UUID). Missing → `/molq:jobs list` and ask which id.

## Procedure

1. **Resolve id** — from `$ARGUMENTS`. If multiple ids, cancel one at a time (report each).
2. **Optional confirm** — when the user said "cancel the last job" without an id: `list_jobs` / `get_job`, show state + command, then cancel only after they confirm the id (or they already gave an explicit id this turn → proceed).
3. **Cancel** — MCP `cancel_job(job_id)`.
4. **Report** — `job_id`, `cluster`, post-cancel `state`.

```
/molq:cancel: job_id=<id> state=<st>
```

## Guardrails

- Same opt-in gate as submit.
- Never mass-cancel without explicit per-id (or explicit "all of these ids: …") request.
- Prefer MCP over raw scheduler cancel when tools work.
