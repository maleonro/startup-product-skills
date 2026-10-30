# design-judge

A [Claude Code](https://claude.com/claude-code) skill that gives you a strict product-designer subagent. It shapes a flow while it is a plan, then judges your mocks and your live build from screenshots, round after round, until it scores 8/10.

Most AI design feedback is one soft pass: "looks good, maybe more spacing". This is a loop with a bar, a score and a stop rule.

## What it does

1. **Picks a bar.** You name a reference product. If you do not, the skill asks for one.
2. **Plan mode.** The judge sees today's screens and your proposed flow. It returns the structure: steps, what each screen asks for, empty and error states.
3. **Judge loop.** You build evidence (an HTML mock, then screenshots of the live app). The judge writes a verdict file with a score, issues and exact fixes. You apply them. A fresh judge checks each issue as fixed, partly or not, and pixel-diffs against the last round.
4. **Stops at 8/10.** 8 means "I would ship it as is".

## The rules that came from mistakes

- Shoot the hard states in round 1 (every role, every money state, empty, loading, error, narrow and short viewports). Every late round in real runs was caught on one of these.
- Treat the author's list of changes as claims to verify. A "neutral" refactor once moved two things nobody saw.
- List final decisions so the judge does not raise them again.
- Judge the live build, not the mock and not the code.
- The judge never edits files. It writes the verdict only.

## Files

- [`SKILL.md`](SKILL.md): the two modes, the round loop, the hard-states list and the traps.
- [`PROMPT.md`](PROMPT.md): the prompt template for the judge subagent.

## Install

```bash
npx skills add maleonro/startup-product-skills --skill design-judge
```

Or manually, by dropping the folder into your skills directory:

```bash
cp -r skills/design-judge ~/.claude/skills/design-judge
# or per-project:
cp -r skills/design-judge /path/to/repo/.claude/skills/design-judge
```

## Use

Ask Claude Code to "bring in the design judge" for a screen or flow. Name a reference product you want to match.

You need:

- **Subagents.** The judge is a separate agent. In Claude Code that is the Agent tool.
- **A way to take screenshots.** A browser tool or a Playwright script, light and dark.
- **Budget.** Use the most capable model. Each round is one judge run.

Pairs with [`frontend-ui`](../frontend-ui/) (build) and [`verify-live`](../verify-live/) (watch it work).

## Why it exists

A designer who also built the screen cannot see its flaws. A judge with no bar gives soft scores. And a loop with no stop rule never ends. This skill fixes all three.
