---
name: frontend-ui
description: Design-system conventions for a React app on shadcn/ui and Tailwind v4. Reuse existing primitives first, ask before adding a new one, use design tokens only, never use raw HTML form controls, and verify the rendered result in a browser. Use when creating or modifying any UI, such as React components, routes, shadcn primitives, styling or markup, or when the user says "build this screen", "add a component", "style this", or "does this match our design system".
---

# frontend-ui

One design system: **shadcn/ui on Tailwind v4**. Do not invent a parallel one. No second component library. No raw HTML form controls.

This skill ships one reference file, in the same directory as this `SKILL.md`:

- [`references/ui-patterns.md`](references/ui-patterns.md): the tactical rulebook. It says how each recurring element behaves (icon button, async button, destructive action, empty state, the four states).

Read it before you build any component. If your repo has its own UI rulebook, read that one instead and treat the reference as a starting point.

This skill is the strategic layer: reuse, tokens, responsive, copy, verify. The reference is the tactical layer.

## Find your sources of truth first

Before the first edit, find these in the repo. Write the paths down.

1. **The primitives folder.** Usually `components/ui/`. This is where shadcn components live.
2. **The token file.** Usually a global CSS file with CSS custom properties and a Tailwind `@theme` block.
3. **Your design doc**, if there is one. It holds the intent: palette rules, type scale, tone.

If a source does not exist, say so and ask the user. Do not invent values.

## Reuse before you build

Before you write any UI markup:

1. **Look in the primitives folder** for a primitive that fits.
2. **If none fits but the thing is primitive-shaped** (button, input, dialog, dropdown, select, table), shadcn almost certainly ships it. **Ask the user whether to add it** before you pull it in:
   ```bash
   pnpm dlx shadcn@latest add <name>
   ```
   Adding a primitive changes dependencies and the design system. It is the user's call, not a silent one.
3. **Never** use a raw native control (`<select>`, `<input type=…>`) as a "temporary" stand-in to dodge adding the primitive. It ignores the tokens and looks broken next to everything else. If the user declines the primitive, ask how to proceed. Do not fall back to bare HTML.
4. Do not hand-roll a primitive that shadcn already ships.
5. Search for an existing composed component too (a row menu, an empty state, a page header). Building a parallel version of something that exists is the most common review miss.

## Placement

- A composed component used in **one** place can live next to its route.
- When a **second** route needs it, lift it to a shared folder named after the domain noun, not the route. Never leave reusable markup inline in a route file.
- The primitives folder belongs to the design system. Only the shadcn CLI or deliberate token-matching tweaks touch it.

## Tokens only: reference the system, never override it

The theme layer is the single place style is defined. It holds design tokens as CSS custom properties, surfaced as semantic Tailwind classes (`bg-primary`, `text-muted-foreground`, `border-border`, `rounded-lg`, `bg-destructive`).

**Always reference tokens. Never override the system at the call site.**

- **No raw values.** No hex, rgb or oklch. No Tailwind arbitrary values (`text-[#1d1d1f]`, `w-[437px]`, `bg-[oklch(...)]`). No inline `style={{ color: … }}` for anything the theme owns.
- **Use semantic tokens, not the raw palette.** Prefer `text-muted-foreground` over `text-neutral-500`. Semantic tokens carry intent and re-theme on their own.
- **Do not override a primitive's internals.** Use its documented `variant` and `size` props. Do not repaint it with `className`. If a variant is missing, add it to the primitive.
- **Changing the look is a theme-layer edit.** A new palette, radius or spacing scale must be a one-file change. If you are tempted to override locally, the token is missing or you picked the wrong one.

Layout utilities (`flex`, `grid`, `gap-*`, `p-*` on the spacing scale) are fine. They compose the system.

If your design doc and a skill or guideline disagree on a literal (an easing curve, a radius), **your design doc wins**. Take the principle from the guideline and the number from your tokens.

## Responsive

Target: **desktop-primary, mobile-functional.** Dense work is tuned for desktop. Every core read or triage flow still works on a phone.

1. **CSS first.** Use responsive Tailwind utilities (`sm:`, `md:`, `lg:`). Tailwind's breakpoints are the single source of truth. Do not invent new ones.
2. **A JS media hook is for behavioral swaps only.** Use it when *which component renders* must change (a sidebar that becomes a sheet). Never use it for plain layout. It causes a first-paint flicker and splits the breakpoint definition.
3. **All tabular data goes through one shared table component** that renders a table on desktop and stacked cards on mobile. Do not hand-roll a `<table>`. Do not wrap a table in `overflow-x-auto` as a shortcut.
4. **No fixed-px widths** on layout containers. Use the spacing scale, `max-w-*`, or fractional and grid widths.
5. **Add a viewport smoke test** that asserts no horizontal overflow at 375, 768 and 1280. Add each new route to its list.

## Copy

- Every user-facing string goes through your i18n layer. No hardcoded copy, including tooltips, aria-labels, empty states and toasts.
- Dates, numbers and currency go through one formatter bound to the active locale. Never call `toLocaleString()` ad hoc.
- Buttons and labels are sentence case. A button that makes a new thing says "New x". A button that attaches existing things says "Add x".

## Fix the pattern, not the screen

Found a defect in a shared pattern (an alignment, a missing tooltip, a spacing rule)? **Sweep every instance.** Search the codebase for all tables, all dialogs, all icon buttons. Never patch only the screen where it was reported.

## Verify what you built: look at it

UI you have not seen rendered is UI you have not finished. Typecheck and e2e tests prove it *works*. They do not prove it *looks right*.

After any UI change, check it in a real browser. This step is required.

1. Make sure the app is running (see the [`verify-live`](../verify-live/) skill).
2. Open each changed screen with a browser tool. Take an accessibility snapshot and a screenshot. Look at both.
3. For anything layout-bearing, check a phone width (375px).
4. Check with your own eyes: tokens applied (no unstyled or clashing controls), no overflow, strings come from the i18n layer, and the flow you touched behaves.
5. Check the four states: loading, empty, error, populated. A screen with only the populated state is not done.
6. Check the console. Expect no errors or warnings.

Report what you saw, with the screenshot. "Typecheck passed" is **not** visual verification. If you could not open a browser, say so plainly.

## Traps

| Trap | Instead |
| --- | --- |
| A native `<select>` "for now" | Ask to add the primitive; never ship bare HTML |
| `text-[#333]` or `w-[437px]` | A semantic token or the spacing scale |
| Repainting a primitive with `className` | Use its variant, or add a variant to the primitive |
| Hand-rolled table or `overflow-x-auto` | The shared table component |
| Fixed the bug on one screen | Sweep every instance of the pattern |
| "It compiles, so it is done" | Open it in a browser and look |
