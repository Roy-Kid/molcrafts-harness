# De-Templating

shadcn is a good foundation and a bad destination. Left at its defaults
it produces a recognizable look — cards everywhere, large radii, grey
borders inside grey borders, a title/description/menu on every region,
and scientific data buried under decorative containers.

This file is the catalog: how to measure the smell, and how to remove it.

---

## Detection

Mechanical counts, run from the frontend root. Adjust the glob to the
project's extensions. These are evidence for the conformance table — not
a substitute for the `web-design` agent's judgment pass.

```bash
# 1. Literal colors outside the token layer          target: 0
rg -n --glob '!**/ui/**' --glob '!**/*token*' \
   -e '#[0-9a-fA-F]{3,8}\b' -e '\brgba?\(' -e '\bhsla?\(' src

# 2. Oversized radius                                target: 0
rg -n -e 'rounded-(2xl|3xl|full)' \
      -e 'rounded-\[(1[2-9]|[2-9][0-9])px\]' \
      -e 'border-radius:\s*(1[2-9]|[2-9][0-9])px' src
#    rounded-full is legitimate on avatars, dots, and pills only.

# 3. Card density               target: <= 1 per standalone object
rg -c '<Card\b' src | sort -t: -k2 -rn | head -20

# 4. Oversized controls                              target: 0
rg -n -e 'h-1[0-4]\b' -e '\bpy-3\b.*\bpx-6\b' src

# 5. Shadow on resident surfaces                     target: 0
rg -n 'shadow-(sm|md|lg|xl|2xl)' src \
   | rg -i 'sidebar|panel|inspector|toolbar|statusbar|rail|tree|table|node'

# 6. Raw shadcn API leaking into feature code        target: 0
rg -n --glob '!**/components/ui/**' '<Button\s[^>]*variant=' src

# 7. Body text too large in dense regions            target: 0
rg -n 'text-(base|lg|xl|2xl|3xl)' src \
   | rg -i 'panel|inspector|row|cell|tree|node|toolbar'

# 8. Heading pile-up: CardTitle+CardDescription pairs
rg -c '<CardDescription' src
```

Report each as `measured / target` with 🔴 (structural: 1, 3, 5, 6),
🟡 (drift: 2, 4, 7, 8).

---

## Container removal

Stage 4 of the ladder, and the fastest visible improvement in the whole
skill.

### The test for keeping a `Card`

Keep it only when the box maps to a **standalone object the user could
reasonably drag, delete, share, or open on its own** — a saved structure,
a run record, a workflow node, an artifact.

Delete it when it is:

- A page region (sidebar, inspector, canvas frame, bottom panel) →
  `Panel` + `Separator`.
- A grouping of related fields → section label + `Separator`.
- A wrapper around a single control, table, chart, or list → the child,
  directly.
- A wrapper whose only job is padding → padding on the parent.
- Nested inside another `Card` → always wrong, one of the two goes.

### Procedure

1. Census: list every `<Card>` with its file and what it wraps.
2. Classify each as *object* or *layout*. Only *object* survives.
3. Replace layout cards bottom-up (innermost first) so intermediate
   states stay renderable.
4. Preserve every semantic and a11y attribute the wrapper carried —
   `role`, `aria-labelledby`, heading level, keyboard handlers. A card
   that was a labelled region becomes a `<section aria-labelledby=…>`,
   not an unlabelled `<div>`.
5. Re-run the typecheck after each file. Delete now-unused imports.
6. Re-run detection. Card density should drop to the object count.

### Header discipline

`CardHeader` + `CardTitle` + `CardDescription` + overflow menu on every
region is the loudest template tell.

- A region gets a title only when the user could otherwise not tell what
  it is. The inspector next to a selected atom does not need the heading
  "Inspector".
- Description text is for genuinely non-obvious regions. Most regions are
  obvious. Delete it.
- An overflow menu exists when there are ≥2 real actions that don't fit
  inline. Otherwise show the action, or show nothing.
- Section labels inside a panel are `--text-label`, uppercase optional,
  muted — not headings competing with the page title.

---

## Substitution table

| Template shape | MolCrafts shape |
|---|---|
| `<Card>` as page region | `Panel` + `Separator` |
| `<Card>` per field group | section label + `Separator` |
| Nested bordered boxes | one border, background lightness for depth |
| Shadow on sidebar/panel | 1px border + surface lightness step |
| `rounded-2xl` surface | `--radius-panel` (8px) |
| `h-10` input / `h-11` button | 32–36px via token override |
| `text-base` panel body | `--text-body` (13px) |
| Dialog for a small edit | inline editing or popover |
| New route for logs/errors | a tab in the bottom panel |
| Grid of stat cards | one dense table, or a status bar |
| Colored badge per entity type | one glyph + a light type stripe |
| Skeleton block per card | one skeleton matching the real row height |
| Spinner centered on the page | in-place skeleton or an inline indicator |

---

## Density without harm

Removing decoration is safe. Removing affordances is not. Density is
achieved by:

- deleting wrappers, headers, descriptions, and redundant menus,
- tightening control heights to § 2 of the constitution,
- moving rarely-used controls into context (they appear on selection),
- replacing card grids with tables.

Never by: shrinking focus rings, dropping labels for placeholders,
lowering text contrast, shrinking touch targets below 44×44pt on touch
surfaces, or removing tooltips from icon-only controls.

If a screen still feels cluttered after all of the above, it has too many
*features* on it — that is a product decision, and the skill reports it
rather than compressing it further.
