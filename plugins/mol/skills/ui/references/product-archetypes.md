# Product Archetypes

Two shapes of MolCrafts frontend. Pick one in Step 1 of the skill; it
decides layout, tokens, density, and the five product components.

Both inherit `visual-language.md` unchanged. What differs is only what
§ 8 *Permitted variance* allows.

| | `viewer` (MolVis) | `workbench` (MolExp) |
|---|---|---|
| Default theme | dark | light (dark offered) |
| Accent | teal-cyan, hue 195 | violet, hue 295 |
| Core region | 3D canvas | workflow graph |
| Density | controls hidden until context | high, persistently visible |
| Primary verbs | observe, select, measure | edit, configure, run |
| Panels | contextual, low-presence | fixed, resizable |
| Bottom region | frame/status bar | logs · problems · runs · artifacts |

---

## A. `viewer` — immersive scientific instrument

MolVis is not a web page. It is an instrument for looking at a structure.

### Layout

```text
┌──────────────────────────────────────────────────────────────┐
│ File / structure name    Selection    Render    Export       │ 44px
├────────┬───────────────────────────────────────┬─────────────┤
│        │                                       │             │
│ Tools  │                                       │  Inspector  │
│        │          Molecular Canvas             │  Selection  │
│ 40px   │                                       │  Properties │
│        │                                       │  Appearance │
├────────┴───────────────────────────────────────┴─────────────┤
│ Frame 142 / 1000  ▶ ──────────────  300 K   128,402 atoms    │ 28px
└──────────────────────────────────────────────────────────────┘
```

Rules:

- **Canvas holds 70–85% of the viewport.** No project cards, welcome
  copy, or tutorial rail on the primary route. Opening a structure lands
  directly in the viewer.
- Left tool rail is icon-only, 40px, single column, tooltips mandatory.
- Right inspector is **contextual**. Nothing selected → no selection
  panel at all, not a panel of disabled fields. An empty inspector shows
  one muted line telling the user what to select.
- Status bar is mono, tabular, and never wraps.
- Panels may float over the canvas with a translucent surface, but data
  values never sit on blur — legibility beats effect.

### Contextual inspector — the pattern

```text
Selection
Oxygen · Atom 142

Position
X   12.382 Å
Y   -2.112 Å
Z    4.820 Å

Residue
PEO · 18

Actions
[ Center ]  [ Hide ]  [ Measure ]
```

Section label at `--text-label`, muted. Values mono, right-aligned,
units in the muted foreground. Separator between groups — no nested
boxes. Actions are a single row of 28px buttons.

### Tokens

```css
@theme {
  --color-canvas:            oklch(0.145 0.008 255);
  --color-panel:             oklch(0.185 0.009 255);
  --color-panel-raised:      oklch(0.215 0.010 255);
  --color-border:            oklch(1 0 0 / 8%);
  --color-foreground:        oklch(0.94 0.010 255);
  --color-muted-foreground:  oklch(0.68 0.015 255);
  --color-accent:            oklch(0.74 0.130 195);
  --color-accent-foreground: oklch(0.14 0.010 195);
}
```

Never `#000`. Pure black kills depth cues in a 3D scene and makes dark
molecular geometry unreadable against the background.

Element colors, property colormaps, and charge scales are **scientific
data**, not theme — they live in their own module and are never remapped
to the accent.

### Product components

The real UI assets. Generic shadcn primitives are their internals, not
the app's vocabulary.

```text
ViewerToolbar           RepresentationSelector   AtomSelectionBadge
TrajectoryTimeline      MeasurementOverlay       ColorScaleLegend
PeriodicBoxControl      LayerTree                StructureInspector
FrameStatusBar          RenderQualityPopover
```

Stage 3 builds five first: **ViewerToolbar · StructureInspector ·
TrajectoryTimeline · AtomSelectionBadge · ColorScaleLegend**.

### Viewer-specific hazards

- Canvas resize must not thrash the render loop — panel resize is
  debounced and the canvas is the last thing to relayout.
- Overlay UI must not intercept pointer events meant for the scene;
  everything decorative is `pointer-events: none`.
- Keyboard focus must be able to *leave* the canvas. A canvas that traps
  Tab is an accessibility blocker, not a design choice.
- Frame counters and timers update mono/tabular text; never let digit
  width shift on every frame.

---

## B. `workbench` — workflow editor + experiment record + light IDE

MolExp is closer to an IDE than to a SaaS dashboard. Model it on the
tools scientists already keep open all day, not on an admin template.

### Layout

```text
┌───────────────────────────────────────────────────────────────┐
│ Project / Experiment / Workflow          Validate    Run ▶    │ 44px
├────────────┬─────────────────────────────────┬────────────────┤
│ Projects   │                                 │ Node Inspector │
│ Experiments│        Workflow Canvas          │ Parameters     │
│ Runs       │                                 │ Inputs/Outputs │
│ Assets     │                                 │ Validation     │
├────────────┴─────────────────────────────────┴────────────────┤
│ Logs | Problems | Runs | Artifacts                            │
└───────────────────────────────────────────────────────────────┘
```

Rules:

- Left navigator is a tree, 28px rows, 13px text, resizable.
- **The bottom panel is essential**, not an afterthought. Logs, problems,
  runs, and artifacts are tabs in one collapsible, height-draggable
  region — never separate routes. Users fix problems while looking at
  the graph.
- Breadcrumb (project / experiment / workflow) is the header's left side;
  primary actions its right side. Nothing else in the header.
- Panels are fixed and resizable; sizes persist per user.

### Tokens

```css
@theme {
  --color-background:        oklch(0.985 0.003 255);
  --color-surface:           oklch(1 0 0);
  --color-surface-subtle:    oklch(0.965 0.006 255);
  --color-border:            oklch(0.890 0.012 255);
  --color-foreground:        oklch(0.200 0.015 255);
  --color-muted-foreground:  oklch(0.480 0.018 255);
  --color-accent:            oklch(0.550 0.190 295);
  --color-accent-foreground: oklch(0.985 0.003 295);
}
```

Light by default: parameters, tables, DAGs, logs, and config are read for
hours. Ship dark as a real theme if wanted — but never use dark to hide a
hierarchy problem. If the light build looks flat, the layering is wrong,
not the palette.

`--color-muted-foreground` at L 0.48 sits near the 4.5:1 line against
`--color-background`. Measure it with a contrast checker before shipping
and darken it if it fails; do not assume.

### Workflow node — not a card

```text
┌──────────────────────────┐
│ ● Molecular Dynamics  ⋮  │
│ LAMMPS                   │
├──────────────────────────┤
│ structure   ◉        ◉ trajectory
│ parameters  ◉        ◉ log
└──────────────────────────┘
```

A node must express: type · run status · input/output ports · validation
errors · cached · executing.

A node must not have: a large icon, a paragraph of description, layered
shadows, a gradient border, or a unique color per type.

Type is carried by a small lucide glyph plus a very light type stripe.
Status is a separate indicator using the § 5 status ramp. **Never let the
type color and the status color occupy the same pixel** — that is the
single most common way a DAG becomes unreadable at 40 nodes.

Node sizing: 8px radius, 1px border, 220–280px wide, 12px internal
padding, ports on a 4px grid so edges land predictably.

### Inspector — grouped, not nested

```text
Parameters

Simulation
──────────────────
Temperature       300 K
Pressure          1 bar
Time step         1 fs

Execution
──────────────────
Backend           Dardel
MPI ranks         128
GPU               Enabled
```

Sections + separators + collapsible groups. No card inside a card. Label
left at `--text-label` muted; value right, mono when numeric, unit in
muted foreground. Validation errors attach to the field, not to a banner
at the top of the panel.

### Product components

```text
WorkflowNode      NodeInspector      NodePortHandle
ParameterField    ParameterGroup     ValidationList
RunStatusBadge    RunTimeline        BottomPanel
LogViewer         ArtifactTable      MetricTable
```

Stage 3 builds five first: **WorkflowNode · NodeInspector ·
ParameterField · RunStatusBadge · BottomPanel**.

### Workbench-specific hazards

- Status vocabulary is exactly the § 5 list. Do not invent `pending`,
  `error`, `success`, `stopped` aliases — one word per state, everywhere,
  including the API-facing types.
- `ParameterField` is schema-driven. A hand-written form per node type
  guarantees drift; derive the control from the parameter schema.
- Log rendering is virtualized. A 200k-line log in a naive list is a
  freeze, not a perf nit.
- Long-running work needs determinate progress where it exists and
  honest indeterminate state where it doesn't — never a fake progress bar.
