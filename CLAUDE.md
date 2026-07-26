---
mol_project:
  name: molcrafts-harness
  language: mixed
  build:
    check: "python3 scripts/validate_repository.py --root . && python3 tests/test_model_policy.py && python3 tests/test_project_blueprint_mechanism.py && python3 tests/test_git_publish.py"
    test: "python3 tests/test_model_policy.py && python3 tests/test_project_blueprint_mechanism.py && python3 tests/test_git_publish.py"
    test_single: "python3 {path}"
  arch:
    style: monorepo
    rules_section: "## Architecture"
  doc:
    style: google
  science:
    required: false
  stage: stable
  release:
    bump_skill: release-bump
    gate_skill: check
  ci:
    config: .github/workflows/validate-plugins.yml
    local: "pre-commit run --all-files"
  notes_path: .claude/notes/notes.md
  specs_path: .claude/specs/
---

# CLAUDE.md — molcrafts-harness

The MolCrafts Claude-Code-first **plugin marketplace**. It ships the `mol`,
`molexp`, and `molq` plugins (workflow skills + agents), and is *itself*
maintained as a `mol*` project — released by `/mol:release` like any other.

## What this repo is

- `plugins/<name>/` — the **published** plugins (`mol`, `molexp`, `molq`).
  Each has `.claude-plugin/plugin.json` (Claude) + `.codex-plugin/plugin.json`
  (Codex) + `skills/` + (for `mol`) `agents/` + `rules/`. Both marketplace
  manifests must agree; the validator enforces it.
- `.claude-plugin/marketplace.json` — Claude marketplace registry (authoritative).
- `.agents/plugins/marketplace.json` — native Codex registry (mirrors it; no
  version field).
- `scripts/` — deterministic, **LLM-free** tooling runnable in CI:
  `validate_repository.py` (structure gate) and `bump_version.py` (release bump).
- `tests/` — stdlib structural guards (model policy, blueprint mechanism, git
  publish). CI and pre-commit run these verbatim.
- `.claude/skills/` — **project-local** maintenance skills for this repo
  (`check`, `new-skill`, `release-bump`); not published plugins.
- `.claude/notes/` — passive project knowledge.

## Where things live (four-zone layering)

Per [`plugins/mol/rules/design-principles.md`](plugins/mol/rules/design-principles.md)
§ 1: public docs in READMEs; passive context in `.claude/notes/`; active specs
in `.claude/specs/`; this router in `CLAUDE.md`. Do not mix them.

## Architecture

The plugin/skill/agent layering, orthogonality, and knowledge-locality rules
are defined once in
[`plugins/mol/rules/design-principles.md`](plugins/mol/rules/design-principles.md)
and [`plugins/mol/rules/agent-design.md`](plugins/mol/rules/agent-design.md).
The `check` skill (§ semantic contracts) validates compliance. Skills are user
verbs; agents are single-axis roles reached only through skills.

## Must never change casually

- **Dual-manifest parity.** Every plugin's Claude + Codex manifest agree on
  name, version, and source. `scripts/validate_repository.py` gates it.
- **Git publish invariants.** `origin` = fork (branch push only); `upstream` =
  canonical (PR → green checks → merge only). Pre-commit ≡ CI. Never merge red.
  See [`plugins/mol/rules/git-publish.md`](plugins/mol/rules/git-publish.md).
- **One workflow file per skill.** `skills/CODEX.md` translates runtime only;
  never a second copy of a workflow body.

## Default workflow

1. Edit a plugin / skill / agent / manifest.
2. Run `/check` (structure + semantic + content janitor + install smoke), or
   `python3 scripts/validate_repository.py --root .` for the fast gate alone.
3. Commit — pre-commit re-runs the validator + structural tests (CI parity).
4. Release with `/mol:release <patch|minor|major>` — it delegates the version
   bump to `release-bump` and the gate to `check` (declared in
   `mol_project.release`), then runs the standard fork → PR → green → merge →
   tag chain.

Validation runs at commit (pre-commit), in CI, and in the release gate. There
is intentionally **no post-edit auto-validation hook** — it blocks structural
refactors of the marketplace itself; run `/check` on demand instead.

## Adding a skill

`/new-skill <plugin>:<name>` scaffolds a complete SKILL.md into a published
plugin, updates its README, and runs `/check`.
