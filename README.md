# Startup Product Skills

[Claude Code](https://claude.com/claude-code) skills for people who own product outcomes and ship the code themselves: founders, PMs, and product engineers.

Each skill encodes a disciplined workflow, not a one-off prompt. They are meant to be dropped into a real production codebase and run end to end.

## Skills

| Skill | What it does |
|-------|--------------|
| [`build-feature`](skills/build-feature/) | Idea to merged, code-only PR whose success metric you own. Brainstorm, grill the decision tree, define and instrument the metric, validate data, senior plan review, UI review, parallel ownership-disjoint build, local verification, then measure the lift. |

## Install

With the [`skills`](https://github.com/vercel-labs/skills) CLI (works with Claude Code, Cursor, Codex, OpenCode and more):

```bash
# install a specific skill
npx skills add maleonro/startup-product-skills --skill build-feature

# list every skill in this repo
npx skills add maleonro/startup-product-skills --list

# install all of them
npx skills add maleonro/startup-product-skills --all
```

Or install manually by dropping the folder into your skills directory:

```bash
git clone https://github.com/maleonro/startup-product-skills
cp -r startup-product-skills/skills/build-feature ~/.claude/skills/build-feature
# or per-project:
cp -r startup-product-skills/skills/build-feature /path/to/repo/.claude/skills/build-feature
```

Then ask Claude Code to build, ship, or implement a feature and the skill triggers.

## Philosophy

A builder owns the merge. A product owner owns the outcome. These skills are for the second kind.
