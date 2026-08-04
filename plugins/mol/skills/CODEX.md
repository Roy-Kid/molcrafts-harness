# Codex runtime adapter

Apply only when Codex loads a skill from this plugin. Claude Code follows `SKILL.md` directly.

## Contract

- Source of truth: current `SKILL.md`, `../../agents/`, `../../rules/`. This file translates runtime only.
- Project harness: `CLAUDE.md` (`mol_project:`) plus any `AGENTS.md` Codex loads.
- User-facing `/mol:<name>` → sibling `../<name>/SKILL.md`.
- Invocation text with the skill → `$ARGUMENTS`.

## Invokers + free-form

Tiers A–E and invoker rules: `../../rules/design-principles.md` § 2.5–2.6.
`description` is the free-form index. One verb = one skill (no entry/body pair).

| Intent | Claude | Codex (`agents/openai.yaml`) |
|---|---|---|
| User-only | `disable-model-invocation: true` | `allow_implicit_invocation: false` |
| Model- or skill-reachable (default) | omit | omit or `allow_implicit_invocation: true` |

Sibling auto-invoke targets must be model-invoked. Read target `SKILL.md` (+ yaml) before in-thread execute.

## Paths

From the active skill directory:

- skill → `../<name>/SKILL.md`
- agent → `../../agents/<name>.md`
- rule → `../../rules/<name>.md`

Project paths (`CLAUDE.md`, `.claude/…`) stay relative to the user repo root.

## Tools

Map Claude tool names to Codex tools by intent. `AskUserQuestion` → normal blocking question. Sibling skill invoke → read and execute in-thread unless independence is required. Claude-only builtins (e.g. `/goal`) → skill's stated fallback.

## Agents

1. Read `../../agents/<name>.md`.
2. `tools` = capability boundary; body = role prompt.
3. Prefer Codex subagent when available; else sequential in-thread only if independence is not required.
4. Ownership: reviewer read-only; `tester` tests; `implementer` production; skill owns gates/ledgers.

Tier labels (not required IDs): `opus` strongest judgment; `sonnet` balanced; `haiku` cheap verify. If tier select unavailable, use session model and keep role/independence.
