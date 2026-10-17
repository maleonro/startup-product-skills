---
name: review-loop
description: Review the current branch against a very strict maintainability and testability rubric (the "thermo-nuclear" review) and fix what it finds, in rounds, until a round finds nothing Critical or Major (max 3 rounds). A fresh reviewer subagent each round, fixes applied in this session, checks re-run after every round. Use before handing a PR to a human, when a branch is "ready", or when the user says "review-loop", "thermo-nuclear review", "review and fix until clean", "revisalo hasta que quede limpio", "revisá y arreglá". The model may invoke it on its own; that is the point.
---

# review-loop

Hand over a PR that is already clean. A fresh reviewer reads the diff against a strict
rubric and writes findings. This session fixes them. Repeat until a round finds nothing
serious.

Run it **once per PR, at the end** of the implementation, not after every slice. Running
it on every small diff burns the signal and slows you down.

This skill ships three reference files, in the same directory as this `SKILL.md`:

- [`RUBRIC.md`](RUBRIC.md): the seven standards the reviewer applies.
- [`TESTING.md`](TESTING.md): what a good test looks like. The rubric judges tests against it.
- [`LESSONS.md`](LESSONS.md): what made the loop converge in real runs. Read it before round 1.

If the repo has its own testing guide, the reviewer uses that one instead of `TESTING.md`.

## Before round 1

1. **Find the base.** Run `git fetch origin`, then take the default branch:
   `git symbolic-ref --short refs/remotes/origin/HEAD` (usually `origin/main`). The diff
   under review is `git diff <base>...HEAD`.
2. **Inventory what the PR deletes.** For every file or test the diff removes, read it
   (`git show <base>:<path>`) and write down what it guaranteed. In real runs, most
   blockers were a behavior whose test was deleted along with the old code. Check each
   guarantee is still anchored by a test, or is gone on purpose.
3. **Do the grep-sized checks yourself.** Orphaned keys, dead imports, a leftover old
   name. They take a minute and do not need a reviewer.

## The loop

For round `n` = 1, 2, 3:

1. **Review, with fresh eyes.** Spawn a NEW subagent. Never reuse the previous round's
   reviewer, and never review in the context that wrote the code. Give it the absolute
   paths of `RUBRIC.md` and `TESTING.md` and tell it to:
   - read both files and apply the rubric to `git diff <base>...HEAD` in this repo;
   - tag every finding `[Critical]`, `[Major]` or `[Minor]`, with `file:line` and one
     line of evidence;
   - raise `[Critical]` or `[Major]` only for something concrete: an input that fails,
     or a mutation of the code that no test catches. A preference of shape is `[Minor]`;
   - write the findings to `PR_REVIEW.md` at the repo root, and fix nothing.

   From round 2 on, also pass the list of findings you skipped, each with its reason.
   Ask the reviewer to judge whether each skip is defensible, and not to raise it again
   if it is. Without that list, reviewers contradict each other and the loop never ends.

   Wait for the reviewer in the foreground. Do not end your turn while it runs.
2. **Triage and fix, in this session.** Read `PR_REVIEW.md`. Give each finding a verdict:
   **Fix**, **Skip** (with one line of why) or **Defer** (becomes a follow-up issue).
   Apply only the Fixes, one commit per independent fix. Never commit `PR_REVIEW.md`.
3. **Re-run the checks** the fixes touch: the project's typecheck, lint and the affected
   tests. A red check is fixed before the round ends.
4. **Exit rule.**
   - This round fixed a `[Critical]` or `[Major]` → go to round `n+1`.
   - Only `[Minor]` findings, or none → stop. Do not re-review after minor-only fixes.
   - Round 3 still fixed a `[Critical]` or `[Major]` → stop and hand the open items to
     the human. A 4th round means the design, not the code, needs a decision.

Delete `PR_REVIEW.md` when the loop ends.

## Report

Plain language, a few lines:

```
review: clean after 2 rounds — 3 fixed, 2 skipped, 1 deferred
skipped: <finding> — <why>
deferred: <finding> — <issue to open>
```

If it stopped at the cap, list what is still open and ask the human ONE question.

## Traps

| Trap | Instead |
| --- | --- |
| Reviewing in the same context that wrote the code | A new subagent every round |
| Reviewer also fixes | Reviewer only writes `PR_REVIEW.md`; this session fixes |
| A blocker that is really a taste call | Blockers name a failing input or an uncaught mutation |
| Round 2 re-raises what round 1 skipped | Pass the skip list with reasons to every new reviewer |
| Re-reviewing after only-minor fixes | Only `[Critical]`/`[Major]` buy another round |
| Reporting "clean" before the checks re-ran | A green check only covers the code that existed when it ran |
| Ending the turn to wait for the reviewer | Wait for its result in the foreground |
