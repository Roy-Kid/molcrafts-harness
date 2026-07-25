---
name: ui
description: "MolCrafts frontend design system — audit a product's UI against the shared visual language, then apply one ladder stage per run (skeleton → tokens → components → de-card → states → motion). Free-form: 前端设计 / UI 改造 / 太像模板了 / de-shadcn / design tokens. Writes tokens, layout shells, product components, and .claude/notes/ui-guidelines.md; refuses shared cross-product UI packages. Not for a single broken component — that's /mol:debug."
argument-hint: "[audit | skeleton | tokens | components | de-card | states | motion] [<path>]"
---

> **Codex:** Read `../CODEX.md` before executing this shared workflow. Claude Code follows the workflow directly.

# /mol:ui — MolCrafts Frontend Design System

Give a MolCrafts frontend a UI that is unmistakably **this product** and
recognizably **MolCrafts** — without gluing the products together.

The governing decision this skill exists to enforce:

> MolVis and MolExp each own an independent UI. They share **design
> principles and brand constraints**, never component code, never a
> Tailwind preset, never an `@molcrafts/ui` package.

shadcn is not an npm component library — its components are *copied into*
the project and owned by it ([shadcn docs](https://ui.shadcn.com/docs)).
Two local component sets is the intended shape, not duplication to be
factored out. Consistency comes from the constitution in
`references/visual-language.md`; difference comes from layout, density,
palette, and product components.

Siblings: the **`web-design`** agent reviews frontend code read-only.
**`/mol:debug`** patches a single broken component. This skill is the only
one that *designs* — it writes tokens, layout shells, and product
components.

## Core principles

1. **Reduce containers, strengthen hierarchy.** Reduce decoration,
   strengthen data. Reduce page switching, strengthen direct manipulation.
2. **The work surface is the product.** Canvas (MolVis) or workflow graph
   (MolExp) holds 70–85% of the viewport. Chrome is low-presence.
3. **Controls appear around the object.** Contextual panels beat a
   permanent wall of disabled controls.
4. **Color carries one meaning at a time.** Status colors mean status.
   The product accent never signals run state.
5. **One ladder stage per run.** Beautifying buttons before fixing the
   page skeleton wastes the work.

## The ladder

Order is load-bearing — later stages are rework if earlier ones are wrong.

| # | Stage | Owns | Done when |
|---|---|---|---|
| 1 | `skeleton` | Page frame: sidebar / work surface / inspector / bottom panel; region sizes and resize behavior | Every route renders inside one declared shell; no ad-hoc page layouts |
| 2 | `tokens` | Type scale, spacing, radius, border, shadow, motion, status ramp, product accent | Zero literal colors/sizes outside the token layer |
| 3 | `components` | The five product components for this archetype | Feature code calls product components, not raw `<Button variant=…>` |
| 4 | `de-card` | Delete surplus `Card`/wrappers/headers — the fastest cure for template smell | `Card` count ≤ count of genuinely standalone objects |
| 5 | `states` | loading / empty / error / disabled / running / success, consistently rendered | Every fetching or computing component renders all applicable states |
| 6 | `motion` | Transitions, focus, hover, micro-detail | Motion only explains spatial or state change, 120–180 ms |

## Procedure

### 1. Resolve the surface and the archetype

Read `CLAUDE.md` → `mol_project:`. Locate the frontend root: the nearest
directory holding `components.json`, or a `package.json` depending on
`react` / `vue` / `svelte`, or the Tailwind entry CSS. In a workspace repo
(e.g. `molvis/` → `core` + `page` + `vsc-ext`) pick **one** workspace —
the one owning the UI entry. Never apply a stage across two workspaces in
one run.

Classify the archetype (drives everything downstream):

| Archetype | Signals | Profile |
|---|---|---|
| `viewer` | 3D / canvas deps (`@babylonjs/*`, `three`, `regl`, `wgpu`), render loop, camera state | Immersive instrument — MolVis |
| `workbench` | graph/table/log deps (`@xyflow/*`, `reactflow`, `@tanstack/react-table`, `xterm`), run + artifact models | Scientific IDE — MolExp |
| `site` | static docs / marketing generator | Out of scope — stop and say so |

Signals conflict or are absent → ask exactly one question naming the two
candidates. Do not guess.

### 2. Load the constitution

Read, in this order:

1. `references/visual-language.md` — shared, non-negotiable.
2. `references/product-archetypes.md` § matching archetype — layout,
   token set, density, product component list.
3. `{$META.notes_path}ui-guidelines.md` if present — the project's own
   record.

Project-local rules may only differ from the constitution inside the
**Permitted variance** table (`visual-language.md` § 8). A project-local
rule contradicting anything outside that table is a **violation to
report**, not an override to honor.

### 3. Audit and locate the ladder position

Run the mechanical conformance scan from
`references/de-templating.md` § *Detection* (literal colors, radius class
census, `Card` density, control heights, shadow on resident panels, raw
shadcn leakage into feature code). These are counts, not opinions.

In the same message, delegate the judgment axis to the **`web-design`**
agent over the frontend root — token drift, information density,
missing empty/error/loading states, a11y, responsiveness.

The boundary: the scan measures **shape**, and its numbers exist to pick
the ladder stage. The agent judges **quality** and owns severity for
token drift, a11y, density, and states. Where both look at the same
thing (literal colors are the usual overlap), the agent's finding is
authoritative and the scan contributes only the progress count — report
it once, not twice.

Merge into the conformance table (§ Output format). The ladder position
is the **lowest failing stage**. `audit` argument → stop here; this step
is read-only.

### 4. Apply exactly one stage

Default stage = the ladder position from Step 3. An explicit stage
argument overrides it; if that stage sits above an unmet lower stage, say
so in one line, then honor the argument.

Apply the stage in full across the frontend root — a half-migrated token
layer is worse than none. Per-stage contracts:

- **skeleton** — build the archetype's shell from
  `references/product-archetypes.md`. Regions are `Panel` + `Separator` +
  a resize primitive, not floating cards. Toolbars 40–48 px. Routes
  render *into* the shell.
- **tokens** — write one token layer in the project's Tailwind entry CSS
  via `@theme` / CSS custom properties (Tailwind v4 keeps theme variables
  in CSS — no shared JS config, [docs](https://tailwindcss.com/docs/theme)).
  Copy the archetype's token block, then replace literals across the
  frontend root. Both light and dark values for whichever themes the
  product ships.
- **components** — author the five product components for the archetype
  (`references/component-contract.md` § *Product surface*). Each wraps
  base primitives so shadcn's API stops leaking into feature code.
- **de-card** — apply `references/de-templating.md` § *Container
  removal*. Delete wrappers; keep semantics and a11y attributes.
- **states** — one state-rendering pattern per project, applied to every
  fetching/computing component. Status vocabulary and colors come from
  the constitution, not from local invention.
- **motion** — `references/visual-language.md` § 6. Remove decorative
  motion; honor `prefers-reduced-motion`.

Never install the whole shadcn registry. The base floor is
`references/component-contract.md` § *Base floor*; add a primitive only
when a component being written needs it.

### 5. Verify

Run the project's typecheck and lint from `mol_project.build`. Both must
be clean before the run reports success; a failing gate is reported with
its output, not summarized away.

A gate that was green before the stage and is red after it is this run's
regression. Fix forward inside the stage. If the stage cannot be made
green, **revert the whole stage** — not a subset — and report what
blocked it. A half-applied stage is worse than an unstarted one. A gate
that was already red before the stage is pre-existing debt: report it
explicitly and route it (`/mol:debug`), never silently absorb it into this
run's diff.

Then, if a browser-automation MCP is reachable (Playwright MCP,
claude-in-chrome, …), take a screenshot pass over the touched routes at a
fixed viewport and attach the images to the report. Boot the dev server
from `mol_project.dev.command` when it is declared, parse the URL from
its ready banner, and kill it when the pass ends. No such MCP, or no
declared dev command → say the visual pass was skipped and move on; it is
advisory and never blocks the stage. Never shell out to `npx playwright`.

The pass is for *this run's* evidence only — it verifies nothing about a
spec and writes to no acceptance ledger. Fixed-viewport screenshot
**baselines** are the durable regression net for this work (panel widths,
control heights, and node layout drift silently otherwise, and
[Playwright visual comparisons](https://playwright.dev/docs/test-snapshots)
are built for it). Recommend them once; adding them is a spec, not a side
effect of this run.

The optional screenshot pass reads `mol_project.dev` from CLAUDE.md. All
three keys are required for it to run; any missing → skip the pass rather
than guess a command.

```yaml
mol_project:
  dev:
    command: <shell command that boots the dev server>
    ready_pattern: <log substring meaning "now listening">
    url_pattern: <regex, one capture group, extracting the URL from that line>
    ready_timeout: 90   # optional, seconds
```

The banner is the only source of truth for the URL — dev servers fall
back to a different port when the configured one is busy.

### 6. Record and hand off

Refresh `{$META.notes_path}ui-guidelines.md` from
`templates/ui-guidelines.md`, writing **only** inside the managed markers:

```markdown
<!-- mol:ui:begin -->
…generated content…
<!-- mol:ui:end -->
```

Re-runs rewrite that block in place; anything a human wrote outside the
markers is preserved untouched. The file records what *this product*
decided (archetype, tokens, component inventory, ladder position) — it
never restates the constitution.

A decision that changes a project convention beyond UI (naming, file
placement, review expectations) is routed to **`/mol:note`**, not written
here.

## References (this skill directory)

| File | Role |
|---|---|
| `references/visual-language.md` | The MolCrafts constitution — type, spacing, radius, borders, shadow, icons, motion, status semantics, forbidden designs, permitted variance |
| `references/product-archetypes.md` | `viewer` and `workbench` profiles — layout, token block, density, product components |
| `references/de-templating.md` | Template-smell catalog with grep-level detection and the container-removal procedure |
| `references/component-contract.md` | Base floor, product surface, wrapper discipline, naming |
| `templates/ui-guidelines.md` | Managed-section template for `.claude/notes/ui-guidelines.md` |

## Output format

```markdown
## /mol:ui — <frontend root> (<archetype>)

### Conformance

| Check | Measured | Target | Verdict |
|---|---|---|---|
| Literal colors outside token layer | 34 | 0 | 🔴 |
| `rounded-2xl`/`3xl` occurrences | 12 | 0 | 🟡 |
| `<Card>` per standalone object | 41 / 6 | ≤ 1.0 | 🔴 |
| Components missing ≥1 state | 9 | 0 | 🔴 |

### Ladder position

Stage 2 `tokens` — stage 1 `skeleton` passes.

### Applied — stage 2 `tokens`

- wrote `src/styles/tokens.css` (…)
- replaced 34 literals across 11 files
- …

### Verification

typecheck ✅ · lint ✅ · visual pass ⏭ (no Playwright MCP)
```

End with the F2 one-line summary: what changed, what passed, what the
next stage is.

## Guardrails

- **No shared UI package — hard refusal.** `packages/ui`,
  `packages/design-system`, `@molcrafts/ui`, a shared Tailwind preset, or
  importing components across product repos. If asked, refuse in one
  sentence with the reason (MolVis optimizing its viewport must not be
  able to break MolExp's forms) and offer the constitution +
  per-product design systems instead. This is the rule the skill exists
  to hold.
- **One repo, one workspace, one stage per run.** Never edits a sibling
  product in the same invocation.
- **Constitution is read-only from the project side.** Deviations are
  legal only inside the Permitted variance table.
- **Never trade accessibility for density.** Focus indicators, labels,
  touch targets, and reduced-motion support survive every stage. Density
  comes from removing decoration, not from removing affordances.
- **No mass component installs.** Base floor plus what the current stage
  needs.
- **Writes UI code, tokens, and one notes file.** Never touches specs,
  acceptance ledgers, `docs/`, backend source, or CI config.
- **Managed markers only.** Human prose in `ui-guidelines.md` outside the
  markers is never rewritten (I3).
