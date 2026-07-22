---
name: submit
description: Submit one molq job via molmcp (argv list, scheduler local/slurm/pbs/lsf). Requires MOLMCP_MOLQ_SUBMIT=1. Free-form: 提交作业/submit job/sbatch via molq. Does not wait — poll with /molq:jobs. Controlled mutation.
argument-hint: "<argv…> [--scheduler=local|slurm|pbs|lsf] [--cluster=] [--profile=] [--cpus=] [--mem=] [--time=] [--partition=] [--gpus=] [--name=] [--workdir=]"
---

> **Codex:** Read `../CODEX.md` before executing this shared workflow. Claude Code follows the workflow directly.

# /molq:submit — Submit One Job

Controlled mutation through molmcp `submit_job`. **Does not block-wait** — use `/molq:jobs get|logs` to poll.

## Preconditions

1. molmcp molq provider available; `molcrafts-molq` installed.
2. **Opt-in mutate:** env `MOLMCP_MOLQ_SUBMIT=1` (or provider `allow_submit=True`). Tool error "disabled" → tell user to set the env; do **not** invent a side-channel CLI submit unless they explicitly ask for `molq` CLI outside MCP.
3. User intent is clear (command + where to run). Ambiguous cluster/scheduler → call `list_destinations` first (via `/molq:jobs destinations` or MCP) and recommend one.

## Procedure

### 1. Build argv

- **argv = list of strings**, never a shell string (`"python train.py --x 1"` is wrong; `["python", "train.py", "--x", "1"]` is right).
- Reject empty argv, `..` in workdir, null bytes.

### 2. Resolve destination

| Field | Default |
|---|---|
| `scheduler` | `local` |
| `cluster` | `cli_<scheduler>` if omitted |
| `profile` | none (optional named molq profile) |

Remote HPC: prefer a known profile or SSH Host from `list_destinations`. Local never resolves the label as SSH.

### 3. Resources (optional)

Map user flags → tool args: `cpus`, `mem` (e.g. `8G`), `time` (e.g. `4h`), `partition`, `gpus`, `gpu_type`, `name`, `workdir`, `account`.

### 4. Submit

Call MCP `submit_job` with the fields above. Capture `job_id`, `cluster`, `scheduler`, `state`.

Do **not** spin-wait in a tight loop. Tell the user how to poll:

```
/molq:jobs get <job_id>
/molq:jobs logs <job_id>
```

### 5. Report

```
/molq:submit: job_id=<id> cluster=<c> scheduler=<s> state=<st>
  cmd: <joined argv>
```

## Guardrails

- Opt-in only — no silent submit when tool is disabled.
- No shell interpretation of argv.
- No force-cancel from this skill.
- Prefer MCP over raw `sbatch` when molq tools are available.
