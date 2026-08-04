---
name: release
description: Release end-to-end for any mol* repo — libraries and this marketplace. Delegates the version bump + pre-release gate to the project's mol_project.release hook skills when declared, else uses built-in first-party dep/registry/docs gates + crate/py/npm bump; then /mol:commit → push(origin) → pr(upstream) → green checks → merge → /mol:tag. Never direct-push to upstream. User-only.
disable-model-invocation: true
argument-hint: "<patch | minor | major> [<package-or-manifest path>]"
---

> **Codex:** Read `../CODEX.md` before executing this shared workflow. Claude Code follows the workflow directly.

# /mol:release — Release (libraries + marketplace)

Read `../../rules/git-publish.md` first — same remotes, pre-commit ≡ CI,
and PR-first chain as everyday push/pr.

One release skill for every `mol*` repo. The skeleton is always the same —
version bump → commit → **push fork** → **PR** → **green checks** → merge →
tag. Two steps are project-specific and are **delegated** to project-local
hook skills named in `mol_project.release` when present:

| `mol_project.release` key | Delegated step | When absent (fallback) |
|---|---|---|
| `bump_skill` | version bump across the repo's version surface | built-in crate/py/npm manifest bump |
| `gate_skill` | pre-release verification (PASS/BLOCK) | built-in dep/registry/docs/CI gates (§3) |

A library (molrs, molpy, …) needs no config and behaves exactly as before;
`molcrafts-harness` declares `bump_skill: release-bump` + `gate_skill: check`
and releases through the same chain. Prefer tag-triggered CI for
crates.io / PyPI / npm — do not publish inline unless the project has no tag
workflow.

**Never write CHANGELOG** — history is `git log`; GitHub Release auto-notes.

## Procedure

### 1. Args + release config

`<bump>` ∈ `patch|minor|major`. Optional path to package/manifest; empty → root/workspace published product.

Read `mol_project.release` from CLAUDE.md. Whether `bump_skill` / `gate_skill`
are declared selects delegation vs built-in at §3 and §4.

### 2. Tree

Dirty → `/mol:commit` auto. BLOCK → stop. Non-default branch OK.

### 3. Hard gates (any 🚨 → stop)

**`gate_skill` declared** → invoke it via the Skill tool (e.g. `Skill(check)`);
its verdict *is* the gate — PASS proceeds, BLOCK / FIX REQUIRED stops. The
project owns its gate, so skip 3a–3d. **Otherwise** run the built-in library
gates below.

**3a. First-party deps** — inventory sibling MolCrafts deps (ignore pure third-party / unpublished workspace members).

| Ecosystem | BLOCK if |
|---|---|
| Cargo | path-only (no `version`) |
| Python/npm runtime | still `file:` / `link:` / path editable on published surface |
| Pin vs local sibling | local version doesn't satisfy pin |
| Registry | pin version missing on crates.io/PyPI/npm (network fail = BLOCK) |

Emit publish order (deps → this). Cycle among separately published packages → BLOCK. Cargo path+version dual-pin OK.

**3b. Docs** — since last tag: public API/CLI/install commits must have matching `docs/` or README (no "TODO document"). Version badges/snippets updated with the bump in § 5. No CHANGELOG required.

**3c. Harness** — if sibling `molcrafts-harness` exists: dirty or untagged commits that this package's harness relies on → BLOCK until the harness is released (run `/mol:release` in the `molcrafts-harness` checkout). Missing checkout → 🟡 skip.

**3d. CI** — `/mol:ship push` (implies pre-commit ≡ CI). BLOCK → ≤3 fix cycles or stop.

### 4–5. Version + branch + commit + local tag

Compute the new version and rewrite the version surface:

- **`bump_skill` declared** → `Skill(<bump_skill>, <bump>)`. It reads the current
  version, rewrites + stages every version field in the repo, and returns
  `old` → `new`. Take `<new>` from its report.
- **built-in** → read the crate/py/npm manifest, bump semver to `<new>`, update
  those version fields + README version badges.

Then put the change on a release branch and tag it: `git switch -c release/v<new>`
(carries the staged version edits onto the branch; switch if it already exists)
→ `/mol:commit "release: v<new>"` → `git tag -a v<new> -m "release: v<new>"`.
Local tag `v<new>` must not already exist. **Never** CHANGELOG.

### 6. Publish chain (no direct upstream branch push)

1. `/mol:push` → **origin only** (fork; pre-commit full + ship)
2. `/mol:pr` title `release: v<new>` (base = upstream default)
3. **Wait for green PR checks** — `gh pr checks <n> --watch` (or poll until all required checks pass). Red or timeout → **BLOCK**; do not merge; report failures.
4. `gh pr merge <n> --merge` (prefer merge commit; **no `--admin` unless checks are already green and the only blocker is admin-only protection** — never to override red CI)
5. If tag not on `upstream/<default>` after squash: retag at that tip
6. `/mol:tag v<new>` (tag only → upstream)
7. Switch default, pull upstream, delete merged `release/v<new>` locally and on origin

### 7. Report

```
/mol:release: v<old> → v<new>
  package / deps / docs / harness / PR / checks / tag / publish path
```

## Guardrails

- Never force-overwrite remote tags; never skip gates; never wait for approval.
- **Never** `git push upstream <branch>` or push the release branch to the org default — always fork → PR → merge.
- **Never** merge a red PR (avoids red Actions email storms on the org repo).
- Delegated `bump_skill` / `gate_skill` own their scope: do not override a project's gate verdict, and do not re-bump or hand-edit version fields after its bump skill ran.
- Dependent after dependency on registry. Idempotent if version+tag already on upstream.
