# Skill / Agent Design Principles

The `mol` plugin is built around **harness engineering**: agents work
better when the repository gives them a small, well-shaped harness —
principled boundaries, predictable layers, and just enough scaffolding to
make safe defaults the obvious move. The aim is not to script every
agent action but to make the *next* agent that walks in succeed without
having to re-derive the rules.

These principles are enforced by `/mol:bootstrap`. Run it against
any project that has been bootstrapped with the mol harness to check
compliance. (The `molcrafts-harness/` marketplace repo maintains itself
as a `mol*` project — its project-local `/check` skill runs the self-audit.)

## 0. Harness Engineering

The harness should *constrain*, not *prescribe*.

- Give the agent **principles** (what's safe, what's risky, why).
- Give the agent **layers** (what kind of artifact lives where).
- Give the agent **judgment criteria** (when to write tests first, when
  to delegate, when to stop and ask).
- Do **not** force a fixed matrix of files, agents, or steps onto every
  project. The shape of the harness should follow the shape of the
  repository it lives in.

A skill or agent that prescribes ten exact steps is brittle. A skill
that names three principles and trusts the agent to apply them is
durable. Prefer the second.

### 0.1 Project iron law — no silent debt

Bootstrapped projects ship this in CLAUDE.md under Design preferences.
It is a **product** iron law for every MolCrafts repo, not optional
style:

- Discovering an anti-pattern, pre-existing failure, or broken
  invariant in the working surface → **prioritize fix or hard-stop
  with a route** (`/mol:debug` / `/mol:refactor` / supersede). Never
  ignore, baseline-away, or paper over with skips / weaker tests.
- "Stay in scope" and "minimal diff" do **not** license knowingly
  leaving rot you have already seen. Unmentioned discoveries are a
  process failure.

Skills that snapshot "pre-existing red" for *their own* regression
gates (e.g. `/mol:simplify`) must still **surface** those failures as
priority debt and must not treat silence as success.

### 0.2 Project iron law — high cohesion, low coupling

Also shipped under CLAUDE.md `## Design preferences (default)`, next
to the OOP defaults. **Every module** (file / type / package) in a
MolCrafts product is constrained:

- **High cohesion** — one clear responsibility per module; split when
  a unit accumulates more than one coherent job.
- **Low coupling** — depend only on narrow, explicit seams
  (constructor args, method params, small protocols/traits). No
  reach-through into other modules' internals; no ambient god
  context required to exercise the unit.

**Unit-test consequence (the operational definition of this law):**
a module is green when **its own** mirrored unit tests under `tests/`
pass via `$META.build.test_single`. Fakes/stubs cover outbound deps.
You do **not** need full-suite (`$META.build.test`) or cross-module
regression to prove the unit. Full suite and `regressions/` are CI /
public-API nets — not the unit-test loop during design or impl.

If unit tests only pass when the whole product graph boots, the
design is too coupled → stop and split / inject / `/mol:refactor`.
Do not compensate with more integration tests.

Enforced by: bootstrap managed section + `architect` (coupling /
isolation anti-patterns) + `tester` (unit scope = one module) +
`implementer` / `spec-writer` (Design preferences).

## 1. Four-Zone Layering

Every well-shaped repository separates four kinds of content. Mixing them
poisons future agents because they cannot tell what they are reading.

```
┌──────────────┐  public-facing documentation: tutorials, API docs,
│   docs/      │  user guides, onboarding. Written for human readers
│              │  who do not work on the agent harness.
└──────────────┘
┌──────────────────────────────────────────────────────────────────────┐
│  .claude/  (everything Claude Code & mol read at the project level)  │
│                                                                      │
│   .claude/notes/    passive internal context (mol): notes,           │
│                     architecture.md, decisions, contracts, handoffs, │
│                     rubrics, debt, open questions. Outlives features.│
│                                                                      │
│   .claude/specs/    active runtime artifacts (mol): alive, ticked    │
│                     off as /mol:impl progresses, deleted on done.    │
│                                                                      │
│   .claude/agents/   Claude Code: agent definitions (loaded at run)   │
│   .claude/skills/   Claude Code: skill definitions                   │
│   .claude/hooks/    Claude Code: hooks                               │
│   .claude/settings.json   Claude Code: settings                      │
└──────────────────────────────────────────────────────────────────────┘
┌──────────────┐  thin entry router: what is this repo, where do things
│  CLAUDE.md   │  live, what must never be changed casually. Routes;
│              │  never embeds.
└──────────────┘
```

`.claude/` follows Claude Code's project-level convention: everything
Claude Code or the mol harness reads lives under it. Inside, content
splits **active vs passive**:

- `.claude/notes/` — passive: outlives features, never auto-deleted.
  Note this is *not* `.claude/agents/` — that is Claude Code's folder
  for agent *definitions* (one file per agent, each defining a role).
  `.claude/notes/` is the agent's *project knowledge* (what the agent
  reads to understand this repo).
- `.claude/specs/` — active: intentionally ephemeral, deleted on done.
- `.claude/agents/`, `.claude/skills/`, `.claude/hooks/`,
  `.claude/settings.json` — Claude Code's own runtime configuration.

The four zones are still four because the conceptual split (public /
passive-internal / active-runtime / router) is what matters; nesting
the latter two under `.claude/` is just the spec-compliant filesystem
layout.

### Layering rules (L)

- **L1.** Public user docs live under `docs/`. Passive internal
  context (notes, decisions, contracts, handoffs, rubrics, debt log,
  open questions, project blueprint) lives under `.claude/notes/`.
  Active runtime artifacts (specs) live under `.claude/specs/`.
  Claude Code's own configuration (agents, skills, hooks, settings)
  lives directly under `.claude/`. `CLAUDE.md` is the router. Each
  category reads, writes, and references only its own kind.

- **L2.** Do not pollute `docs/` with agent contracts, handoffs,
  rubrics, specs, working memory, temporary plans, or private
  reasoning. Do not put public-user prose under `.claude/`. Do not
  put long-lived knowledge in `.claude/specs/` or directly under
  `.claude/` outside `.claude/notes/` — passive context goes in
  `.claude/notes/`, active runtime goes in `.claude/specs/`,
  Claude Code config goes in its conventional subfolders. Mixing
  passive content into `.claude/specs/` (or vice versa) breaks
  the active/passive contract that `/mol:impl`'s deletion behavior
  depends on.

- **L3.** `CLAUDE.md` is a short router (≤ ~150 lines is a good
  budget). It answers: *what is this repo?*, *where do things live?*,
  *what must never change casually?*, *what is the default workflow?*
  It links to files; it does not embed them. A CLAUDE.md that grows
  past two screens is a smell — promote sections to `.claude/notes/`
  and link.

- **L4.** Specs are alive. `/mol:spec` writes them under
  `.claude/specs/` with a checkbox-tracked Tasks section. `/mol:impl`
  ticks each box as work completes and deletes the spec file (plus
  its INDEX entry) on completion. A spec is never archived to
  `docs/` or `.claude/notes/`; once `done`, it is removed because
  the information that mattered is now in code, tests, and (when
  non-obvious) `.claude/notes/notes.md`.

## 2. Two-Layer Model

```
user / free-form / sibling skill
        │
        ▼
   /skill  (one verb — thin orchestration)
        │
        ▼
   agent × N  (single expertise axis; never user-invocable)
        │
        ▼
   tools
```

**One verb = one skill + 0..N agents.**

| Layer | Owns | Does not own |
|---|---|---|
| **Skill** | procedure: order, gates, multi-turn, handoffs, when to delegate | expert catalogs, long domain checks |
| **Agent** | one expertise axis: findings or artifacts in that axis | workflow, calling other agents, full-suite gates |

- Skill stays thin relative to agents (orchestration, not encyclopedia).
- Skill → agent is the default nest. Skill → skill only for a **different
  verb** (e.g. `/mol:impl` → `/mol:simplify`). **Never** two skills for
  the same verb (no entry/body pair).
- Agent never calls agents (O2). Skill is the only orchestrator.

Modes (advisor vs orchestration) and agent model tiers:
`plugins/mol/rules/model-policy.md`.

### 2.5 Invokers (who may fire a skill)

Default: **model-invoked** (user, free-form, or sibling).

| | Claude | Codex (`agents/openai.yaml`) |
|---|---|---|
| **Model-invoked** (default) | omit flag | omit or `allow_implicit_invocation: true` |
| **User-only** | `disable-model-invocation: true` | `allow_implicit_invocation: false` |

- Sibling auto-invoke target **must** be model-invoked.
- User-only only when no sibling and no free-form may fire it (e.g.
  `/mol:release`). No second skill for the same verb.
- Frontmatter `description` is the free-form index (zh/en triggers +
  when not to fire). Do not add a skill file just for indexing.

Plan chain:

```
/mol:discuss ──converge──▶ /mol:grill (plan)
                              │
                              ▼ (user: 落盘 / 写 spec — not silent)
                          /mol:spec ──persist──▶ /mol:grill (spec-audit)
                                                    │ holes → supersede
                                                    │ clean → /mol:impl-all
                                                              │
                                                              ▼
                                                    simplify → docs Mode A → close
```

### 2.6 Free-form tiers (A–E)

Natural language loads model-invoked skills. Tiers limit silent irreversible work.

| Tier | Free-form | Examples |
|---|---|---|
| **A** | Yes — match intent | `discuss`, `grill` (has plan), `simplify`, `docs` Mode A, `note` |
| **B** | Yes, scoped scene | `debug`, `review`, `map`, `test`, `litrev`, `ci-sync` |
| **C** | Oral ignition, no silent fire | `spec`, `commit`, `push`, `pr`, `refactor`, `bootstrap`, `docs` Mode B |
| **D** | Via siblings / chain | `close`, `ship`, `tag`, `impl` after spec, `perf` when owed |
| **E** | User-only | `release` |

Rules: A/B put triggers in `description`. C needs affirmative intent
("落盘", "提交吧"). Never silent-auto `spec` from discuss/grill.
`docs` Mode A = A; Mode B = C.

### Autonomy boundary

**Interactive (may wait):** `/mol:discuss`, `/mol:grill`, and
`/mol:spec` post-persist grill turns. Spec ignition is human (tier C).

**Fully agent-driven:** impl, close, simplify, docs Mode A, commit,
push, pr, tag, release, perf, ship, debug/refactor apply once kicked,
mechanical bootstrap repairs. Closing a spec is never the operator's
job — `/mol:close` auto-runs evaluators and agent-auto-attests.

One publish chain for every `mol*` repo, following
`plugins/mol/rules/git-publish.md` (pre-commit ≡ CI; **origin = fork**
branch push only; **upstream = canonical** via PR → green checks →
merge; never direct-push branches to upstream):

- **`/mol:release`** → gates (or a repo's `mol_project.release` `gate_skill`)
  → version bump (or `bump_skill`) → commit → push(origin) → pr → green
  checks → merge → tag. This covers both ecosystem libraries and the
  `molcrafts-harness` marketplace — the marketplace declares
  `bump_skill: release-bump` + `gate_skill: check`. Dependencies on the
  official registry **before** dependents; tag-triggered CI publishes to
  crates.io / PyPI / npm when configured.

## 3. Why This Split

1. **Reusability.** Multiple skills delegate to the same agent (the
   `architect` agent is used by `/mol:impl`, `/mol:refactor`, and
   `/mol:review` — directly or via `--axis=arch`). One source of
   architecture rules, read by many skills.
2. **Parallelism.** Review-style skills fan out to multiple agents in
   one message; agents have isolated context windows so the
   orchestrator stays small.
3. **Safety.** Read-only agents (`architect`, `optimizer`, `scientist`,
   `compute-scientist`, `undergrad`, `pm`, `ci-guard`, `ffi-guard`,
   `reviewer`)
   cannot accidentally edit code; write-capable agents (`tester`,
   `documenter`) have edit rights only inside their declared scope.

## 4. Knowledge Hierarchy

```
/mol:note  (sync — not append)
        │  reconcile · delete fossils · single canonical home
        ▼
.claude/notes/notes.md     staging / evolving rules (topic-keyed)
.claude/notes/<topic>.md   long stable rules
.claude/notes/architecture.md   blueprint (owned by /mol:map; note may
                                strike false claims only)
        │
        ▼ promotion when stable (and delete the staging copy)
   CLAUDE.md  ◀──────── thin router — read by every agent
        │
        ▼
   skills/agents read from it; never duplicate it

.claude/specs/    active, checkbox-tracked plans; written by /mol:spec,
                  ticked + deleted by /mol:impl. Not knowledge —
                  ephemeral work-in-flight.
```

**Harness knowledge is current truth, not a changelog.** `/mol:note`
must **rewrite or delete** superseded and stale entries across
CLAUDE.md and `.claude/notes/**` so agents are not polluted by
contradictory fossils. Git history is the archive; agent-facing files
keep one live rule per topic. Appending a second note that conflicts
with an older one is a design bug.

Every agent's first line is *"Read CLAUDE.md and the project's notes
file before running any checks."* Project-specific facts live in
CLAUDE.md (with the `mol_project:` frontmatter for machine-readable
keys) or in the notes tree. Agent prompts hold only **unique
knowledge** the agent needs that does not belong in CLAUDE.md
(tolerances, anti-pattern catalogs, grep heuristics, floating-point
conventions).

## 5. Design Rules

### Layering (L)

See Section 1.

### Orthogonality (O)

- **O1.** Each agent owns exactly one expertise axis. If two agents
  would both answer the same question, merge or split until each has a
  unique axis.

  *Worked example — `architect` vs `librarian` boundary.* Both
  agents read the same shared artifact (`.claude/notes/architecture.md`,
  the project blueprint maintained by `/mol:map`), but they answer
  different questions and are wired into different scheduling
  points:

  - `architect` answers *"is the code currently in **compliance**
    with the layering rules?"* — this is the review/refactor-time
    validator. Output: emoji-prefixed findings.
  - `librarian` answers *"given a planned new capability, where
    does it go (**placement**) and is it already there (reuse)?"* —
    this is the spec-time consultant. Output: a fixed
    four-section advisory report.

  Sharing the artifact does not violate O1 because the verbs are
  disjoint (validate vs. consult); the unique-axis rule is about
  *the question answered*, not *the data read*.
- **O2.** Agents do not call other agents. The skill is the only
  orchestrator. *Exception:* a write-capable agent may produce code
  that a read-only agent later validates — but the validation call is
  made by the parent skill, not by the writer.
- **O3.** A skill names its delegates explicitly. There is no implicit
  routing.
- **O4.** A skill does not contain expert knowledge. If a check is
  non-trivial enough to need worked examples or reference data, it
  belongs in an agent.
- **O5.** One verb = one skill. Never an entry/body skill pair for the
  same procedure. Skill → skill only when the callee is a different
  user verb.

### Knowledge locality (K)

- **K1.** CLAUDE.md is the single thin source of truth for stable
  rules. Every agent reads it first.
- **K2.** The project's notes file holds evolving decisions; `/mol:note`
  enforces conflict detection and promotes stable entries into
  CLAUDE.md (then deletes from the notes file).
- **K3.** Agent prompts contain only *unique knowledge* not in CLAUDE.md
  (heuristics, grep patterns, tolerances, anti-patterns). They never
  duplicate architecture rules.
- **K4.** Skill prompts contain only *workflow* (steps, when to
  delegate, output format). They never restate domain rules.

### Capability hygiene (C)

- **C1.** Read-only agents declare only Read/Grep/Glob/Bash. Granting
  Write/Edit must be justified by the agent's role (e.g. `tester`
  writes tests; `documenter` writes docs).
- **C2.** A skill that writes (specs, code, docs, tests, notes) must
  say so in its `description` frontmatter so the user knows what will
  change.
- **C3.** A skill's diagnose-only mode (`/mol:debug --diagnose-only`)
  states explicitly that
  they never edit. Enforced in the skill's procedure, not just in the
  description.

### Workflow shape (W)

- **W1.** Plan → Build → Verify → Document → Memory is the canonical
  loop. The `mol` plugin covers each phase.
- **W2.** RED before GREEN: `/mol:impl` must call the `tester` agent
  to write failing tests before any implementation is attempted.
- **W3.** Reviews fan out in parallel. `/mol:review` issues all
  delegate calls in one message.
- **W4.** Architecture validation happens at four points: scope
  assessment (planning), **spec-time librarian consult**
  (`/mol:spec` Step 4.5 — placement and reuse advice against the
  project blueprint at `.claude/notes/architecture.md`), after
  implementation, and after refactor. The spec-time consult is the
  fourth scheduling point and was added to plug the planning-phase
  visibility gap that produced duplicate modules and wrong-layer
  placement in large projects.
- **W5.** Bug fixing is a separate, minimal loop (`/mol:debug`:
  reproduce → diagnose → patch → verify), not a degenerate case of
  `/mol:impl`. It carries no spec gate and no acceptance ledger,
  because a bug is a defect against already-agreed behavior.

### Output format (F)

- **F1.** Review-style agents output severity-sorted lines prefixed
  with an emoji: 🚨 Critical, 🔴 High, 🟡 Medium, 🟢 Low.
  ```
  🚨 file:line — message
    Fix: ...
  ```
  Skills aggregating multiple agents render a 🚨 / 🔴 / 🟡 / 🟢 table
  and a verdict (APPROVE / REQUEST CHANGES / BLOCK).
- **F2.** Skills end with a one-line user-facing summary suitable for
  scanning: files changed, tests passing, remaining TODOs.

### Idempotency (I)

- **I1.** Bootstrapping skills must be safe to re-run. They detect
  existing files and offer merge / replace / keep per entry instead of
  duplicating or silently overwriting.
- **I2.** Memory skills (notes promotion) must detect duplicates and
  contradictions before writing.
- **I3.** Generators that write managed sections must use stable
  markers so re-runs update in place rather than appending.

## 6. Re-Examination Checklist

`/mol:bootstrap` walks this checklist against any `.claude/`
tree. Output one finding per row: `<emoji> file:line — message` (🚨 /
🔴 / 🟡 / 🟢).

### Layering (L)

- [ ] Are public docs under `docs/`? Is `docs/` free of agent
      contracts, handoffs, working memory, rubrics, or specs? (L1, L2)
- [ ] Are passive internal artifacts (notes, decisions, debt log,
      handoffs, rubrics, contracts) under `.claude/notes/`? (L1)
- [ ] Are specs under `.claude/specs/` with a checkbox-tracked Tasks
      section? Are completed specs deleted (not archived)? (L4)
- [ ] Is `.claude/` free of long-lived knowledge? (only skills,
      agents, hooks, settings, and active specs) (L2)
- [ ] Is CLAUDE.md a thin router, not a manual? Does it route to
      `docs/`, `.claude/notes/`, and `.claude/` rather than embedding their
      content? (L3)

### Layer presence

- [ ] Are skills (`.claude/skills/*/SKILL.md`) and agents
      (`.claude/agents/*.md`) both present, or is the project
      conflating the two?
- [ ] Does every user-visible verb live in a skill, not an agent?
- [ ] Is there a CLAUDE.md serving as the entry router?
- [ ] Does CLAUDE.md start with a `mol_project:` frontmatter block (if
      the project opts into the mol plugin contract)?

### Orthogonality

- [ ] List each agent and the question it answers. Are any two
      answering the same question? (O1)
- [ ] Do agents invoke other agents? (O2)
- [ ] Do skills name delegates explicitly? (O3)
- [ ] Does any skill embed expert knowledge that belongs in an agent?
      (O4)
- [ ] One skill file per verb — no entry/body dual skills? Skill →
      skill only for a different verb? (O5)

### Knowledge

- [ ] Do agents read CLAUDE.md first? (K1)
- [ ] Is there a `/mol:note`-equivalent skill enforcing conflict
      detection and promotion? (K2)
- [ ] Do agent prompts duplicate CLAUDE.md content? (K3)
- [ ] Do skill prompts restate domain rules instead of pointing to
      CLAUDE.md? (K4)

### Capability

- [ ] Are read-only agents declared with read-only tools? Any
      unjustified Write/Edit? (C1)
- [ ] Does each writing skill announce what it writes? (C2)
- [ ] Are diagnose-only modes enforced in the procedure, not just
      the description? (C3)

### Workflow

- [ ] Plan / Build / Verify / Document / Memory — is each phase
      covered? (W1)
- [ ] Does the implementation skill enforce RED before GREEN? (W2)
- [ ] Do review skills fan out in parallel? (W3)
- [ ] Are architecture checks scheduled at the three required points?
      (W4)
- [ ] Is bug fixing a minimal loop separate from the spec-gated
      feature path? (W5)

### Output

- [ ] Do review agents emit `<emoji> file:line` lines using 🚨 / 🔴 /
      🟡 / 🟢? (F1)
- [ ] Do skills end with a one-line user-facing summary? (F2)

### Idempotency

- [ ] Is the bootstrap skill safe to re-run? (I1)
- [ ] Does the notes skill detect duplicates and contradictions before
      writing? (I2)

### Per-project domain coverage

For a domain-heavy project, verify there is one agent per *axis of
risk* the project actually has. Every axis where the project can fail
silently must have its own agent, and every agent must map to a real
risk. No filler agents.

## 7. Anti-Patterns

These show up in repositories that were bootstrapped without harness
discipline. The audit flags each as 🟡 or higher.

- **Template sprawl.** A bootstrap dropped twelve skills and ten
  agents into a one-week-old repo, most of which never get invoked.
  Cure: start small, grow on demand.
- **Knowledge in `.claude/`.** Architecture rules, decisions, or
  domain notes embedded in a skill/agent body, or written into
  `.claude/` outside of `.claude/specs/`. Cure: promote to CLAUDE.md
  or `.claude/notes/` and leave a reference.
- **Specs in `.claude/notes/` or `docs/`.** Specs are alive — they belong in
  `.claude/specs/`. Putting them next to passive notes is a category
  error. Cure: move under `.claude/specs/` and add a Tasks checklist.
- **Specs without checkboxes.** A spec with no Tasks section can't be
  ticked, can't be tracked, and can't be auto-deleted. Cure: re-run
  `/mol:spec` to add a concrete checklist.
- **Done specs left around.** A spec marked `done` but still on disk
  is clutter. Cure: `/mol:impl` should have deleted it; if it
  didn't, delete manually and capture any non-obvious context with
  `/mol:note`.
- **Contracts in `docs/`.** Agent handoff contracts or review rubrics
  living next to user tutorials. Cure: move under `.claude/notes/`.
- **CLAUDE.md as manual.** A 600-line CLAUDE.md that nobody reads.
  Cure: split into `.claude/notes/architecture.md`, `.claude/notes/conventions.md`,
  etc. and link.
- **Fake precision.** A bootstrap that invented architecture rules
  with no evidence in the codebase. Cure: record as an open question
  in `.claude/notes/open-questions.md` instead.
- **Agent calling agent.** Implicit routing through agent bodies.
  Cure: hoist orchestration into a skill.
- **Entry/body dual skills.** Two skill files for one verb (thin
  user entry wrapping a body skill). Cure: one model-invoked skill;
  user-only only when the whole verb must never auto-fire.
- **One-shot skills with no idempotency.** Re-running them duplicates
  files or clobbers user content. Cure: detect and merge.
