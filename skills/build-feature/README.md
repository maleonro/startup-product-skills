# build-feature

A [Claude Code](https://claude.com/claude-code) skill that encodes a full idea-to-shipped-PR workflow, with product-outcome ownership built in.

It is not a prompt. It is a disciplined loop a non-engineer can run to ship real features into a production codebase, the same way a senior engineer would, plus the one thing most AI build workflows skip: owning the metric.

## What it does

Fifteen steps, idea to merged PR. **Core** steps always run; **Scalable** steps grow with the size of the change.

1. Start from a clean base (rebase).
2. Brainstorm, then grill every branch of the decision tree before writing a plan.
3. Lock decisions fast; default to best practices when indifferent.
4. **Define the success metric and instrument it, before building.** Capture the baseline.
5. Write the plan in `docs/`; validate the SQL against real data before building.
6. Senior plan review by a fresh agent with zero attachment to the idea, multiple rounds.
7. UI review on a mockup, reusing existing components.
8. Build with a parallel, ownership-disjoint workflow (no two agents touch the same file).
9. Run the app and drive it as a user.
10. Iterate on real bugs from runtime evidence.
11. Verification before "done": type check, lint, tests, with passing output as evidence.
12. One PR, code only. No flags.
13. Final functional PR review.
14. Close the loop in the tracker.
15. **Measure the lift** against the baseline. The feature is not done until the number moves, or you understand why it did not.

## Files

- [`SKILL.md`](SKILL.md) — the 15-step workflow and hard rules.
- [`GRILLING.md`](GRILLING.md) — how to run and answer the design grill.
- [`METRICS.md`](METRICS.md) — defining, instrumenting and measuring the success metric.
- [`WORKFLOWS.md`](WORKFLOWS.md) — four parallel-agent workflow patterns (build, review, adversarial verify, remediation).

## Install

```bash
npx skills add maleonro/startup-product-skills --skill build-feature
```

Or manually, by dropping the folder into your skills directory:

```bash
cp -r skills/build-feature ~/.claude/skills/build-feature
# or per-project:
cp -r skills/build-feature /path/to/repo/.claude/skills/build-feature
```

Then trigger it by asking Claude Code to build, ship, or implement a feature.

## Why it exists

A builder owns the merge. A product owner owns the outcome. This skill is for the second kind.

## Credits

This workflow orchestrates skills built by others:

- Grilling: **`grill-me`** / `grill-with-docs` from [Matt Pocock's skills](https://github.com/mattpocock/skills) (MIT).
- UI review: Vercel's `web-design-guidelines` (Web Interface Guidelines) and [`vercel-react-best-practices`](https://github.com/vercel-labs/agent-skills).
