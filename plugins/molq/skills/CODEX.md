# Codex runtime adapter

Apply this file only when Codex loads a skill from this plugin. Claude Code follows the canonical `SKILL.md` directly.

- Treat the current `SKILL.md` as the canonical workflow.
- Preserve `/molq:<name>` in user-facing output → sibling `../<name>/SKILL.md`.
- `$ARGUMENTS` = invocation text with the skill.
- Map Claude tool names to Codex tools by intent.
- **molmcp tools** are the primary execution surface (`list_jobs`, `get_job`, `job_logs`, `list_destinations`, `list_queue`, `submit_job`, `cancel_job`). Discover exact qualified names from the connected MCP server if the short name fails.
- Mutations require `MOLMCP_MOLQ_SUBMIT=1` (or provider `allow_submit=True`).
- Cross-plugin: agent harness is `mol`; experiment data layout is `molexp`.
