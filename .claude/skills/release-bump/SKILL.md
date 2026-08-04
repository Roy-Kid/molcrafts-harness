---
name: release-bump
description: Project-local version-bump hook for molcrafts-harness. Bumps the marketplace version across every plugin + marketplace manifest and stages the change. Invoked by /mol:release as its mol_project.release.bump_skill; receives <patch|minor|major> and returns the old and new versions. Not a general skill — the marketplace-specific version surface lives here.
argument-hint: "<patch | minor | major>"
---

# /release-bump — Marketplace Version Bump

The version-carrying files of this repo are the marketplace's — not a single
crate/py/npm manifest — so `/mol:release` delegates the bump to this
project-local skill (named in `mol_project.release.bump_skill`). All the
marketplace-specific knowledge (which files carry the version) lives in the
deterministic helper `scripts/bump_version.py`, which this skill drives.

Callers: `/mol:release` (Step 4) passes `<patch|minor|major>`; this skill
rewrites + stages the version fields and reports `old` → `new` so the caller
can tag `v<new>` and write the release commit message. Also runnable by hand.

## Procedure

### 1. Validate the argument

`$ARGUMENTS` must be exactly one of `patch`, `minor`, `major`. Anything else
→ print usage and stop. No bump happens on a bad argument.

### 2. Confirm the tree agrees before bumping

Run the deterministic check:

```bash
python3 scripts/bump_version.py --check
```

It prints `current=<x.y.z>` when every version field agrees, or exits
non-zero listing the offenders. Disagreement → **stop** and report the
mismatched files; a split-version tree is a bug to fix by hand (or a prior
half-done bump), never something to paper over by bumping.

### 3. Bump and stage

```bash
python3 scripts/bump_version.py <part>
```

The script discovers every target dynamically — `.claude-plugin/marketplace.json`
(each `.plugins[].version`), `plugins/*/.claude-plugin/plugin.json`, and
`plugins/*/.codex-plugin/plugin.json` — verifies they agree, computes the new
semver, and rewrites only the `"version"` token (preserving formatting). It
prints each file touched and a final `old=<x> new=<y> fields=<n>` line.

Then stage exactly those files:

```bash
git add .claude-plugin/marketplace.json plugins/*/.claude-plugin/plugin.json plugins/*/.codex-plugin/plugin.json
```

Do not stage anything else — the caller owns the commit.

### 4. Report

Emit the old and new versions in a form the caller can consume, e.g.:

```
release-bump: 0.14.0 → 0.15.0 (9 version fields across 3 plugins + marketplace)
```

`old` and `new` are the contract `/mol:release` reads for the tag `v<new>`
and the `release: v<new>` commit message.

## Guardrails

- **Refuses to bump a mismatched tree** (Step 2). The whole point is a single
  agreed version; bumping over drift would hide it.
- **Version fields only.** Never edits skill/agent bodies, READMEs, or code —
  those are not version-carrying and are out of scope.
- **Stages, never commits or pushes.** The commit/push/tag chain belongs to
  `/mol:release`.
- **Deterministic core.** All rewriting is in `scripts/bump_version.py` (stdlib,
  testable); this skill only validates, drives it, and stages.
