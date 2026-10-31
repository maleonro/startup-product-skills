# testing

A [Claude Code](https://claude.com/claude-code) skill that decides what to test, proposes the tests before writing them, and writes a small suite where every test earns its place.

Most AI-written tests are many, mocked and tied to the current code. They go green, then break on every refactor and miss real bugs. This skill goes the other way: few tests, mostly integration, a real database, and proof that each test can fail.

## What it does

1. **Reads the code** and its door (route, command, job, component). Extends the existing suite before it makes a new file.
2. **Plans by equivalence classes.** One test per class of input. A failure-mode checklist finds the cases. Black box first, then white box.
3. **Makes every test earn its place.** One sentence per test: the realistic code edit that would break it. No sentence, no test.
4. **Proposes two tables before writing**: tests to write (with kind and reason) and tests to skip (with reason).
5. **Writes** with real services and a real test database. Fakes only at the external edge.
6. **Breaks the code on purpose** to watch each test go red for the right reason, then reverts.
7. **Self-checks** against a list of anti-patterns.

## The standard

> Write tests. Not too many. Mostly integration.

- Never fake storage. Never mock your own code.
- Fake only what you do not control, at the outermost port you own.
- Assert outcomes with hard-coded full-equality values, not calls on your own collaborators.
- Keep bodies short and readable alone (DAMP, not DRY).
- Existing specs are not a reference. You pick a **golden list** of 3 to 5 suites in your own repo, and copy those.

## Files

- [`SKILL.md`](SKILL.md): the workflow, the test kinds, the two plan tables and the self-check.
- [`references/failure-modes.md`](references/failure-modes.md): a checklist of failure modes to scan while planning.
- [`references/good-tests.md`](references/good-tests.md): the external edge, the anti-patterns, and how to seed, assert and size a test.

## Install

```bash
npx skills add maleonro/startup-product-skills --skill testing
```

Or manually, by dropping the folder into your skills directory:

```bash
cp -r skills/testing ~/.claude/skills/testing
# or per-project:
cp -r skills/testing /path/to/repo/.claude/skills/testing
```

## Use

Ask Claude Code to write tests, or to say what tests a change needs. It also fits right after a non-trivial change, and when a bugfix needs regression evidence.

You need:

- **A real test database** you can start locally and clone per worker. Speed is never a reason to fake storage.
- **A golden list.** Pick 3 to 5 good suites in your repo the first time. The skill tells you how.

Works with a TDD loop: the TDD loop owns the red-then-green order, and this skill owns which tests exist.

Pairs with [`review-loop`](../review-loop/), whose rubric judges tests against the same standard.

## Why it exists

A green test run only means something if the tests could have failed. This skill makes that the rule.

## Credits

Adapted from the testing skill in [Primo's public skills](https://github.com/primo-devs/public-skills).
