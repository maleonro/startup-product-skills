---
name: build-feature
description: End-to-end workflow for building a new feature with Claude Code, from idea to a merged, code-only PR whose success metric you own. Covers brainstorming, relentless grilling of the design tree, defining and instrumenting a success metric, data validation, senior plan review, UI review, parallel ownership-disjoint implementation via workflows, local verification, tracker close-out, and verifying the metric moved after shipping. Use when the user wants to build, ship, or implement a new feature, says "vamos a construir", "creemos", "build this", "let's implement", or brings a PRD/idea to turn into shipped code.
---

# Build a Feature

A disciplined idea-to-PR loop. Run the steps in order. **Core** steps always apply. **Scalable** steps grow with the size of the change: skip them for tiny fixes, run them hard for anything user-facing or risky.

When the user gives a short, decisive answer to a design question, take it and move on. When they have no strong preference, decide using domain best practices (UX, outreach, data) rather than stalling.

## Workflow checklist

Create a TodoWrite item per step you intend to run.

1. **[Core] Start from a clean base.** Rebase onto main before touching code.
2. **[Core] Idea to design: brainstorm, then grill.** Use a brainstorming skill (`superpowers:brainstorming`) to frame the idea or PRD. Then run a grilling skill (`grill-me`, or `grill-with-docs` when there's a domain glossary / ADRs) to **walk every branch of the decision tree and resolve dependencies one by one**. Do not write the plan until every branch is resolved. See [GRILLING.md](GRILLING.md).
3. **[Core] Lock decisions fast.** Answer each grill branch tersely and decisively; default to best practices when there's no strong preference. The grill ends when there are no open branches, not when you run out of questions.
4. **[Core] Define the success metric and instrument it.** Before building, name the one metric that proves this feature worked (activation, WAU, acceptance/reply rate, conversion). Either it's already tracked, or instrumenting it becomes part of this build, so a **baseline exists before launch**. A feature without a success metric is a guess. See [METRICS.md](METRICS.md).
5. **[Core] Write the plan + validate data first.** Save the plan as a `.md` in `docs/`. Include the metric and its instrumentation as plan items. If the feature touches the database, write the SQL queries and **validate them against real data before building**, not after. Confirm the queries with the user.
6. **[Scalable] Senior plan review, fresh context, multiple rounds.** Dispatch a strict "head of engineering / CTO" agent with NO build context to review the plan. Iterate rounds until no objections remain. Thoroughness over speed.
7. **[Scalable] UI review on a mockup, before building.** Dispatch a design agent (`vercel-react-best-practices`, `web-design-guidelines`) to judge a mockup. New UI must reuse existing components and visual identity, not invent styles.
8. **[Scalable] Build with a parallel, ownership-disjoint workflow.** Once the plan is approved, implement via a `Workflow` with phased fan-out: contracts/interfaces first, then parallel builders on disjoint files, then engine, then API/wiring, then a verify phase. See [WORKFLOWS.md](WORKFLOWS.md).
9. **[Core] Run it locally and drive it as a user.** Launch the real app (not just tests). Use the run/verify skills, capture runtime evidence.
10. **[Scalable] Iterate on real bugs with evidence.** Fix issues observed in screenshots/runtime (UX, i18n, stale state), not in the abstract.
11. **[Core] Verification before "done".** Type check, lint, and run the relevant tests. Never report complete without the passing output as evidence. See the project's verification commands in CLAUDE.md.
12. **[Core] One PR, code only.** Keep the PR scoped to the change. No docs, no tooling files, no feature flags unless the user asks. Stage explicit paths, never `git add -A`. The user opens the PR from the link; you may make a final commit (e.g. copy) once it's open.
13. **[Scalable] Final functional PR review.** Clean the branch and run one last senior review (a verification workflow works well here) focused on the feature working end to end. See [WORKFLOWS.md](WORKFLOWS.md).
14. **[Core] Close the loop in the tracker.** Document what was done and move the issue to done (Linear or the project's tracker).
15. **[Core] Measure the lift.** After shipping, come back and check the metric from step 4 against its baseline. You own the outcome, not the merge: the feature isn't done until the number moves, or you understand why it didn't and what's next. See [METRICS.md](METRICS.md).

## Hard rules

- **No feature flags** unless the user explicitly requests one.
- **Don't auto-create the PR or push** unless asked; the user creates PRs from the link.
- **Plans live in `docs/`** as `.md`; PRs stay code-only.
- **Evidence before assertions.** A step is done when its output proves it, not when it looks done.
- **You own the outcome, not the merge.** No feature starts without a success metric (step 4) and none is truly done until that metric is measured against its baseline (step 15).

## Reference

- [GRILLING.md](GRILLING.md) — how to run and answer the design grill.
- [METRICS.md](METRICS.md) — defining, instrumenting and measuring the success metric.
- [WORKFLOWS.md](WORKFLOWS.md) — the four parallel-agent workflow patterns (build, review, adversarial verify, remediation).
- Analysis mode (hypothesis to insight) is a separate workflow, not covered here.
