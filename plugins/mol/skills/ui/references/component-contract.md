# Component Contract

Two layers, per product, in the product's own repo.

```text
components/ui/          base primitives — vendored, project-owned
components/<domain>/    product components — the actual vocabulary
components/scientific/  shared-within-product scientific widgets
```

There is no third layer. There is no cross-product layer. See the skill's
guardrails for why.

---

## Base floor

Install these and nothing else at stage 1. Add a primitive only when a
product component being written actually needs it.

```text
button      input       textarea    select      checkbox
switch      tooltip     popover     dropdown-menu
dialog      sheet       tabs        command
separator   scroll-area resizable
```

Deliberately absent until justified: `card` (usually the problem, not the
solution), `accordion`, `carousel`, `avatar`, `breadcrumb` (a header is
cheaper), `form` (schema-driven fields supersede it), `toast` (one
notification channel per product — decide before installing), `chart`
(scientific charts follow scientific conventions, not a UI kit).

Every vendored primitive is **modified in place** to match the
constitution: control heights, radius tokens, border width, focus ring.
Do not re-derive those values at call sites and do not keep a pristine
copy "in case of upgrade" — the file belongs to the project now.

---

## Product surface

Feature code should read as domain language. This:

```tsx
<Button variant="outline" size="sm" onClick={…}>
  <Ruler className="h-4 w-4" /> Measure
</Button>
```

should become this:

```tsx
<ViewerToolButton tool="measure-distance" />
```

and this:

```tsx
<Badge variant={run.status === "failed" ? "destructive" : "secondary"}>
  {run.status}
</Badge>
```

should become this:

```tsx
<RunStatusBadge status={run.status} />
```

### The wrapper rule

**shadcn's API must not appear in feature code.** Concretely: outside
`components/ui/`, there should be no `variant=`, no `size=`, no
`className` doing visual work that a token or a product component should
own.

Why it matters here specifically: it is what lets MolVis restyle every
button for a dark viewport, and MolExp restyle every button for a dense
light IDE, without either team touching the other's code — and without
either being blocked by a shared package's release cycle.

`className` remains legitimate for **layout at the call site** (grid
placement, flex growth, width) — that is composition, not styling.

### Naming

- Product components are named for the **domain object or action**, not
  the widget: `TrajectoryTimeline`, not `FrameSlider`. `RunStatusBadge`,
  not `StatusChip`.
- The product prefix appears only when the same noun exists in both
  layers (`ViewerToolButton` vs the base `Button`).
- One component per file, named for the file. Files stay under ~200 lines;
  a component past that is two components.
- Props are domain types (`status: RunStatus`, `tool: ViewerTool`), never
  visual enums (`color: "red"`, `variant: "danger"`). Visual mapping lives
  inside the component — that is the entire point of the layer.

---

## States

Every component that fetches or computes renders all applicable states.
This is stage 5, and it is checked per component, not per page.

| State | Requirement |
|---|---|
| `loading` | Skeleton matching the real content's shape and height, or an inline indicator. Never a layout jump on resolve. |
| `empty` | One line of what would be here plus, when there is one, the action that creates it. Never a blank region. |
| `error` | What failed, in the user's terms, plus a retry when retry is meaningful. Never a blank region with a console error. |
| `disabled` | Explains itself — tooltip or adjacent text. A disabled control with no reason is a dead end. |
| `running` | `--status-running` plus determinate progress where progress is knowable; honest indeterminate where it is not. |
| `success` | Transient confirmation, or the result itself. Not a toast for something already visible on screen. |

A component that renders content only when `data && !loading && !error`
and `null` otherwise is missing three states, not one.

Empty states are also where a scientific tool earns trust: "No
trajectory loaded" plus an open action beats an illustration, and beats
silence.

---

## Testing the surface

- Product components are the right unit for component tests: they carry
  domain props and domain behavior.
- Fixed-viewport screenshot baselines belong on the **shell** (skeleton)
  and on the **five product components** per archetype — that is where
  drift in panel widths, control heights, and node layout actually shows
  up. Playwright's `toHaveScreenshot` comparison is built for this.
- Do not baseline the 3D canvas pixel-for-pixel; GPU differences make it
  flaky. Baseline the chrome around it and assert canvas behavior
  functionally.
