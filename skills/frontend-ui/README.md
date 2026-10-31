# frontend-ui

A [Claude Code](https://claude.com/claude-code) skill that keeps AI-built UI inside your design system: reuse first, tokens only, no raw HTML controls, and a real look at the result.

AI agents love to hand-roll a `<select>`, paste a hex color, or patch one screen and leave the rest. This skill stops that.

## What it does

1. **Finds your sources of truth.** The primitives folder, the token file and your design doc. It never invents values.
2. **Reuses before it builds.** It searches for an existing primitive or composed component first.
3. **Asks before adding a primitive.** A new shadcn component changes dependencies and the design system. It is your call.
4. **Uses tokens only.** No hex, no arbitrary values, no repainting a primitive from the call site.
5. **Keeps responsive CSS-first.** One shared table, no fixed-px layout widths, a viewport smoke test.
6. **Sweeps shared defects.** A bug in a pattern is fixed everywhere, not on one screen.
7. **Verifies the rendered result.** It opens each changed screen in a browser, checks phone width, the four states and the console, and reports what it saw.

## Files

- [`SKILL.md`](SKILL.md): the conventions and the traps.
- [`references/ui-patterns.md`](references/ui-patterns.md): the tactical rulebook. 41 rules for how each recurring element behaves. Rename the components to match your repo.

## Install

```bash
npx skills add maleonro/startup-product-skills --skill frontend-ui
```

Or manually, by dropping the folder into your skills directory:

```bash
cp -r skills/frontend-ui ~/.claude/skills/frontend-ui
# or per-project:
cp -r skills/frontend-ui /path/to/repo/.claude/skills/frontend-ui
```

## Use

Ask Claude Code to build or change any screen or component. The skill triggers on UI work.

You need:

- **React with shadcn/ui and Tailwind v4.**
- **A browser tool** (for example a Chrome MCP or Playwright) to verify the result.

Pairs with [`design-judge`](../design-judge/) (score the result) and [`verify-live`](../verify-live/) (run the stack).

## Why it exists

A design system only works if the agent cannot quietly route around it. These rules close the usual escape routes: the "temporary" native control, the one-off color, the screen-only patch, and "it compiles" as proof.
