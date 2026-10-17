# review-loop

A [Claude Code](https://claude.com/claude-code) skill that reviews your branch with a very strict rubric, fixes what it finds, and reviews again, until a round finds nothing serious.

Most AI code review is one pass that you then fix by hand. This is a loop with a stop rule, so the PR you hand over is already clean.

## What it does

1. **Prepares.** Finds the base branch, lists what the PR deletes and what those files guaranteed, and does the grep-sized checks itself.
2. **Reviews with fresh eyes.** A new subagent every round reads the diff against the rubric and writes `PR_REVIEW.md`. Each finding is `[Critical]`, `[Major]` or `[Minor]`, with `file:line`. It fixes nothing.
3. **Fixes in your session.** Each finding gets Fix, Skip (with why) or Defer (a follow-up issue). One commit per fix.
4. **Re-runs the checks** the fixes touch: typecheck, lint, the affected tests.
5. **Decides whether to go again.** A fixed Critical or Major buys another round. Only minors: stop. Hard cap of 3 rounds; past that, the design needs a human decision.

It ends with a short report:

```
review: clean after 2 rounds — 3 fixed, 2 skipped, 1 deferred
skipped: <finding> — <why>
deferred: <finding> — <issue to open>
```

## The rubric

The "thermo-nuclear" review asks whether the PR makes the codebase **simpler and better tested**, not merely working. Seven standards:

1. No file crosses 1k lines because of this PR.
2. No ad-hoc conditional bolted into an unrelated flow.
3. Direct, boring code beats magical or wrapped code.
4. Type and boundary contracts are explicit.
5. Logic lives in the canonical layer and reuses existing helpers.
6. Independent work runs in parallel; related state changes are atomic.
7. Every behavior added or claimed-preserved is anchored by a test at the right level.

Above all it hunts for the **code-judo** move: the change that deletes whole branches, helpers or layers instead of rearranging them.

## Files

- [`SKILL.md`](SKILL.md) — the loop, its exit rule and its traps.
- [`RUBRIC.md`](RUBRIC.md) — the seven standards the reviewer applies.
- [`TESTING.md`](TESTING.md) — what a good test looks like: mostly integration, real database, fakes only at the external edge. The rubric judges tests against it. If your repo has its own testing guide, the reviewer uses that.
- [`LESSONS.md`](LESSONS.md) — what made the loop converge in real runs, and what each reviewer costs.

## Install

```bash
npx skills add maleonro/startup-product-skills --skill review-loop
```

Or manually, by dropping the folder into your skills directory:

```bash
cp -r skills/review-loop ~/.claude/skills/review-loop
# or per-project:
cp -r skills/review-loop /path/to/repo/.claude/skills/review-loop
```

Add `PR_REVIEW.md` to your `.gitignore`. The reviewer writes it and it is never committed.

## Use

On your branch, when the work is done, ask Claude Code to `review-loop` (or "review this until it's clean"). Run it once per PR, at the end, not after every small change.

You need:

- **Subagents.** Each round needs a reviewer that did not write the code. In Claude Code that is the Agent tool.
- **A git remote** named `origin` with a default branch. The diff is `git diff origin/<default>...HEAD`.
- **Budget.** Each reviewer costs about 200k tokens and 5 minutes on the most capable model.

Pairs with [`build-feature`](../build-feature/): run it before you open the PR.

## Why it exists

A reviewer in the same context that wrote the code does not see its own mistakes. A reviewer that also fixes stops being strict. And a review with no stop rule either ends too early or never ends. This skill fixes all three.
