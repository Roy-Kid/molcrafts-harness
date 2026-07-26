# Notes — molcrafts-harness

Evolving decisions for this repo. `/mol:note` reconciles entries here;
stable rules get promoted into `CLAUDE.md` or `plugins/mol/rules/`.

## Release model (2026-07)

The harness repo is released as a `mol*` project by `/mol:release`, not by a
dedicated marketplace-release skill. `/mol:release` delegates the two
project-specific steps to project-local hook skills named in
`mol_project.release`:

- `bump_skill: release-bump` — rewrites every plugin + marketplace version
  field via `scripts/bump_version.py`.
- `gate_skill: check` — full structure + semantic + smoke gate.

When neither is declared (ordinary library repos), `/mol:release` falls back
to its built-in crate/py/npm manifest detection and dep/registry/docs gates.
This retired the former `mol-plugin` plugin and its `/mol-plugin:release`,
`/mol-plugin:check`, `/mol-plugin:new-skill`. Their assets moved to
`scripts/`, `tests/`, and `.claude/skills/` (project-local).

## No post-edit validation hook

The former `mol-plugin` shipped a PostToolUse hook that ran the validator on
every edit. It was dropped, not re-homed: it blocks structural refactors of
the marketplace itself. Validation is enforced by pre-commit, CI, and the
release `gate_skill` instead.
