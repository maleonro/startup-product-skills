# linear

A [Claude Code](https://claude.com/claude-code) skill for working with Linear over its MCP: create issues from what is already in the session, triage them, and solve one from first read to open PR.

You stop retyping context into tickets, and tickets stop going stale while the work moves.

## What it does

1. **Creates issues from context.** It pulls the title, repro steps, file references and acceptance criteria from the conversation and the codebase. It checks for duplicates first.
2. **Edits and triages.** It reads the issue, then changes state, priority, labels, assignee and relations. It comments instead of rewriting the description.
3. **Solves an issue end to end.**
   - Pull the issue and its comments.
   - Claim it (assign to you, `In Progress`).
   - Branch with the identifier in the name.
   - Fix it. A bug is reproduced first and gets a regression test.
   - Verify it live.
   - Comment back with the root cause.
   - Open the PR and move the issue to `In Review`.
4. **Finds work.** "What is assigned to me" becomes a prioritized list.

## Files

- [`SKILL.md`](SKILL.md): the three workflows, the issue template and the traps.

Replace `<your-team>` in the skill with your Linear team name.

## Install

```bash
npx skills add maleonro/startup-product-skills --skill linear
```

Or manually, by dropping the folder into your skills directory:

```bash
cp -r skills/linear ~/.claude/skills/linear
# or per-project:
cp -r skills/linear /path/to/repo/.claude/skills/linear
```

## Use

Mention an issue ("fix ABC-123"), paste a linear.app link, or say "log this as a ticket".

You need:

- **The Linear MCP** connected to Claude Code.
- **Git and a PR flow** for Workflow C.

Pairs with [`verify-live`](../verify-live/) and [`build-feature`](../build-feature/).

## Why it exists

Tickets filled by hand lack context. Tickets updated by hand lag the work. Bugs "fixed" without a repro come back. This skill puts the context in at creation, the post-mortem in at the end, and a reproduction in between.
