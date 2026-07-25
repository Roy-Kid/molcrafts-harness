# UI Guidelines — <product>

Product-local UI record, maintained by `/mol:ui`. The shared MolCrafts
constitution is **not** restated here; it lives in the `mol` plugin at
`skills/ui/references/visual-language.md`. This file records only what
*this product* decided.

Human prose may be added anywhere outside the managed markers below and
will never be rewritten.

<!-- mol:ui:begin -->

## Surface

| | |
|---|---|
| Frontend root | `<path>` |
| Archetype | `<viewer \| workbench>` |
| Default theme | `<dark \| light \| both>` |
| Token layer | `<path to the @theme / tokens file>` |
| Last ladder stage applied | `<stage>` on `<YYYY-MM-DD>` |

## Accent

```css
--color-accent: <value>;   /* hue <n>, ≥40° from --status-running (250) */
```

## Layout shell

`<one paragraph: the regions, their sizes, what resizes, what persists>`

## Product components

| Component | Wraps | Owns |
|---|---|---|
| `<Name>` | `<base primitives>` | `<domain responsibility>` |

## Base primitives installed

`<list — the base floor plus anything added, with the component that
justified each addition>`

## Permitted variance claimed

Only rows from `visual-language.md` § 8 may appear here.

| Axis | This product | Rationale |
|---|---|---|
| `<axis>` | `<choice>` | `<one line>` |

## Known debt

| Item | Stage | Severity |
|---|---|---|
| `<what is still non-conforming>` | `<ladder stage that fixes it>` | `<🔴 \| 🟡>` |

<!-- mol:ui:end -->
