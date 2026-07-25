# The MolCrafts Visual Language

The shared constitution. Every MolCrafts frontend obeys it; no product
forks it. It is deliberately short — it constrains brand and semantics,
and says nothing about layout, palette, or components, because those are
where products are supposed to differ.

Read this with `product-archetypes.md`. This file answers *"what makes
it MolCrafts?"*. That file answers *"what makes it this product?"*.

---

## 1. Typography

| Role | Family |
|---|---|
| UI, prose, labels | Geist, or Inter |
| Numbers, coordinates, units, identifiers, code, logs | JetBrains Mono |

The mono rule is not stylistic. Any value a scientist reads *as a
quantity* — coordinates, energies, temperatures, frame indices, atom
counts, run ids, file paths, durations — is mono with tabular figures
(`font-variant-numeric: tabular-nums`), so digits align across rows and
across frames of an animation.

Scale — one ramp, both products:

| Token | Size | Use |
|---|---|---|
| `--text-micro` | 11px | badges, axis ticks, port labels |
| `--text-label` | 12px | form labels, table headers, status chips |
| `--text-body` | 13px | dense panels, inspector rows, trees, tables |
| `--text-body-lg` | 14px | main content, prose, dialogs |
| `--text-title` | 16px | panel and section titles |
| `--text-heading` | 20px | page heading |
| `--text-display` | 24px | maximum; rare |

Body text is **13–14px**. Nothing exceeds 24px. Line height 1.4 in dense
regions, 1.5 in prose. Weights: 400 body, 500 emphasis, 600 titles — no
700+ in chrome.

## 2. Spacing

4px grid. Permitted steps: **4 · 8 · 12 · 16 · 24 · 32**. Anything else
is a bug, including "just 6px here".

Control heights, both products:

| Element | Height |
|---|---|
| Toolbar | 40–48px |
| Input, select, button (default) | 32–36px |
| Compact / icon button | 28px |
| Table row, tree row | 28–32px |
| Status bar | 28–32px |

shadcn's defaults (`h-10` inputs, `h-11` buttons) are too tall for
scientific density. Override them in the token layer once, not per call
site.

## 3. Radius

| Token | Value | Applies to |
|---|---|---|
| `--radius-control` | 6px | buttons, inputs, chips, badges |
| `--radius-panel` | 8px | panels, cards, nodes |
| `--radius-overlay` | 10px | popovers, dialogs, sheets, tooltips |

Nothing above 10px. `rounded-2xl`, `rounded-3xl`, and 16/24px card
corners are forbidden — large radii on large surfaces are the single
loudest "generic dashboard template" signal.

## 4. Borders and elevation

- Border width is **1px**. Always.
- **Resident surfaces are separated by border and background lightness,
  never by shadow.** Sidebars, inspectors, toolbars, status bars, and the
  bottom panel are part of the frame; they do not float.
- **Shadow belongs to overlays only** — popover, dropdown, dialog, sheet,
  tooltip, context menu, drag preview. One elevation level. Never two.
- Never nest a bordered box inside a bordered box for grouping. Use a
  `Separator` and a label. Grey-border-inside-grey-border is template
  smell, not hierarchy.

## 5. Status color semantics

One vocabulary across every MolCrafts product. Status names are fixed;
new ones are a constitution change, not a product decision.

| Status | Hue family | Token |
|---|---|---|
| `draft` | neutral | `--status-draft` |
| `ready` | neutral, stronger | `--status-ready` |
| `queued` | desaturated blue-grey | `--status-queued` |
| `running` | blue | `--status-running` |
| `completed` | green | `--status-completed` |
| `failed` | red | `--status-failed` |
| `cancelled` | muted neutral | `--status-cancelled` |
| `cached` | purple-grey | `--status-cached` |
| `warning` | amber | `--status-warning` |

```css
--status-draft:     oklch(0.65 0.010 255);
--status-ready:     oklch(0.58 0.020 255);
--status-queued:    oklch(0.62 0.040 250);
--status-running:   oklch(0.62 0.150 250);
--status-completed: oklch(0.60 0.130 150);
--status-failed:    oklch(0.58 0.190  25);
--status-cancelled: oklch(0.60 0.008 255);
--status-cached:    oklch(0.60 0.060 300);
--status-warning:   oklch(0.72 0.140  85);
```

Hard rules:

- Red means error. Only error.
- Amber means warning. Only warning.
- Green means success or completion. Only that.
- **The product accent is never a status color.** An accent whose hue
  sits within 40° of `--status-running` (250) will be misread as
  "running" on a dense screen — pick an accent outside that band. This is
  why the archetype accents are 195 (viewer) and 295 (workbench) rather
  than the more obvious 215 / 270.
- Node type, entity type, and button emphasis never borrow status hues.
- Status is legible without color: pair every status color with a shape,
  glyph, or label. Colorblind users and greyscale screenshots both matter.

Never encode scientific meaning in brand color. Element colors, property
color maps, and charge/energy scales follow their own scientific
conventions (CPK, viridis, diverging blue-white-red) and are immune to
brand palette changes.

## 6. Motion

- Duration **120–180ms**. `--motion-fast: 120ms`, `--motion-base: 150ms`,
  `--motion-slow: 180ms`.
- Easing `cubic-bezier(0.2, 0, 0, 1)` for enter/move, linear for
  continuous progress.
- Motion may only explain **spatial relationship** (a panel slides from
  the edge it belongs to) or **state change** (a run flips to failed).
- Forbidden: bounce, spring overshoot, rotation flourish, gradient
  animation, shimmer used as decoration, staggered list reveals, anything
  looping while idle.
- `prefers-reduced-motion: reduce` collapses transitions to opacity or to
  nothing. Never merely shortens them.
- The 3D viewport is exempt: camera easing and trajectory playback are
  the subject matter, not chrome.

## 7. Icons and brand

- **Lucide**, everywhere. One library, one stroke weight (1.5px), sizes
  14 / 16 / 20px on the 4px grid.
- Emoji are never UI iconography.
- Icon-only controls always carry `aria-label` and a tooltip.
- Product identity appears **once**, top-left of the frame, as
  `MolVis` / `MolExp` in the UI face at `--text-title`, weight 600. No
  logo lockup in the toolbar, no watermark on the work surface, no brand
  gradient.
- Product name in the document title as `<context> — MolVis`.

## 8. Permitted variance

The only axes a product may decide for itself. Everything above is fixed.

| Axis | Free to differ |
|---|---|
| Default theme | dark, light, or both |
| Accent hue | yes — subject to the 40° rule in § 5 |
| Layout topology | yes |
| Information density | yes, within § 2 control heights |
| Panel behavior | floating/contextual vs fixed/resizable |
| Product component set | yes — that is the point |
| Chart and colormap choices | yes, per scientific convention |

## 9. Forbidden

A checklist, in rough order of how often it shows up:

1. `Card` used as page layout rather than as a genuinely standalone object.
2. Radius above 10px.
3. Shadow on a resident (non-overlay) surface.
4. A bordered box nested directly inside a bordered box for grouping.
5. Title + description + overflow menu on every region by reflex.
6. Brand or accent color used for run state.
7. Two colors meaning the same thing, or one color meaning two things.
8. Decorative motion (§ 6).
9. Emoji as icons; mixed icon libraries; mixed stroke weights.
10. Gradient text, glassmorphism blur behind data, neon glow.
11. A different color per node type or per entity type.
12. Body text at 16px+ in a dense panel; headings above 24px.
13. Full-page route transitions for what should be a panel change.
14. A shared cross-product component package (see the skill's guardrails).
