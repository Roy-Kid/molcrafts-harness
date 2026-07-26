# molq plugin

Job-queue workflows for **[molq](https://github.com/MolCrafts/molq)** via **molmcp** tools — not the code harness (`mol`) and not experiment folders (`molexp`).

```
molmcp MolqProvider
  read:  list_jobs · get_job · job_logs · list_destinations · list_queue
  mutate (opt-in): submit_job · cancel_job
```

## Skills

| Skill | What | Free-form |
|---|---|---|
| `/molq:jobs …` | Read-only: list/get/logs/destinations/queue | 查作业 / squeue / 看日志 / job status — **agent may self-trigger** when it needs queue truth |
| `/molq:submit …` | Submit one job (`MOLMCP_MOLQ_SUBMIT=1`); no wait | 提交到服务器 / 丢到集群 / sbatch — **slash optional** when intent is clear |
| `/molq:cancel <job_id>` | Cancel one job (same opt-in) | 取消作业 / scancel |

Agents may also call molmcp tools **directly** (`list_queue`, `submit_job`, …) without typing a slash — skills define the procedure and safety gates.

## Install

```
/plugin install molq@molcrafts
```

Runtime:

```bash
pip install molcrafts-molq   # and molmcp with molq provider enabled
export MOLMCP_MOLQ_SUBMIT=1 # only when agents may submit/cancel
```

## Relation to other plugins

| Plugin | Domain |
|---|---|
| `mol` | Code project harness (spec / impl / review / git) |
| `molexp` | Experiment **data** workspace layout |
| `molq` | **Job queue** lifecycle (this plugin) |
