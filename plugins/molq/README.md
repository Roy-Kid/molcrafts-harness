# molq plugin

Job-queue workflows for **[molq](https://github.com/MolCrafts/molq)** via **molmcp** tools — not the code harness (`mol`) and not experiment folders (`molexp`).

```
molmcp MolqProvider
  read:  list_jobs · get_job · job_logs · list_destinations · list_queue
  mutate (opt-in): submit_job · cancel_job
```

## Skills

| Skill | What |
|---|---|
| `/molq:jobs [list\|get\|logs\|destinations\|queue] …` | Read-only dashboard: store jobs, status, log tails, destinations, live queue |
| `/molq:submit <argv…> [resources…]` | Submit one job (needs `MOLMCP_MOLQ_SUBMIT=1`); does not wait |
| `/molq:cancel <job_id>` | Cancel one job (same opt-in) |

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
| `mol-plugin` | Marketplace scaffolding / release |
