---
name: design-judge
description: Bring in a strict, read-only product-designer subagent. It shapes a flow while it is still a plan, then judges mocks and the live build from screenshots, round after round, until it scores 8/10. Use when the user says "bring in the design judge", "judge this design", "design review until it's good", "score this screen", "be my product designer", or wants a design partner for a screen, an onboarding or other multi-step flow, or a landing page.
---

# design-judge

The judge is a subagent, not a style guide. You build the evidence. It looks at the evidence and writes a verdict file. You apply the verdict and run the next round. It never edits the repo.

This skill ships one reference file, in the same directory as this `SKILL.md`:

- [`PROMPT.md`](PROMPT.md): the prompt template for the judge. Fill every `{…}` before you launch it.

## Pick the bar first

The judge needs a reference product to measure against. It scores "would this sit well next to that product?"

1. If the user named a reference product (a site, an app, a launch page), use it.
2. If not, **ask one question**: "Which product has the design quality you want to match?" Do not start without an answer.
3. Put the reference in the prompt. Ask the judge to open it and name what it does well, so the bar is concrete.

## Launch

- Use a subagent (in Claude Code: the `Agent` tool, general-purpose type) on the most capable model you have. A weaker model gives soft scores.
- The prompt is the template in [`PROMPT.md`](PROMPT.md). Fill every `{…}`. Do not drop the constraints block.
- Run one judge per round. A fresh judge each round, with its last verdict file as input.
- After each round, tell the user the score and the top 3 issues in plain words.

## The judge's lens

Visual craft. One idea per area. The interface carries the meaning, not a caption. Low cognitive load. Nothing generic. Every pixel earns its place. The judge measures (positions, hit areas, pixel diffs). It does not guess.

## The two modes

**1. Plan mode (design partner).** Use it while the flow is still a plan, before any code.

- Give it the real screens of today (screenshots of the running app) and the proposed flow as short text or a rough mock.
- Ask for the structure: steps, what each screen asks for, where the user can leave and come back, the empty and error states.
- Give no score, or score the plan only.
- Its output feeds the plan. It is not a sign-off.

**2. Judge loop (mock, then live).**

1. **Mock.** Build an HTML mock with the real design tokens from your code. The code is the source of truth for colors, fonts and radius. Use real data from the app, anonymized. Show "Today" beside "Proposal".
2. **Shoot.** Take screenshots with your browser tool, light and dark.
3. **Round.** The judge writes `verdict-rN.md`. You apply the fixes. Repeat until 8/10.
4. **Live.** Build it. Then judge the REAL app, not the code. Take screenshots of every state. Force states by intercepting API responses. Log in once and reuse the saved session.

## Draw the hard states up front

In the runs this skill came from, every round was caught on something missing from this list. Shoot all of them in round 1:

- Every role: owner or admin, a member without billing rights, staff, impersonation.
- Every money state: trial, last 2 days of trial, low balance, no balance, payment failed.
- Empty, loading, error, and the worst case where all of the above pile up.
- Viewport: wide desktop, the narrow desktop where the sidebar collapses, short heights (about 700px and 650px), and a phone.
- Real hit areas (the judge measures them) and one action at a time per block.

## Each round after the first

- Give the judge its previous verdict file. Ask for **fixed / partly / not** per issue, with evidence.
- List what changed as **claims to verify, not to trust**.
- Ask for a pixel diff against the previous round. A "visually neutral" refactor once moved two things nobody saw.
- List the decisions that are final, so the judge does not raise them again every round.
- After a code-review round, re-shoot before the next judge round. The judge and a code reviewer can run in parallel on the same shots.

## Rules for you

- Keep evidence in a scratch folder. Never commit screenshots or verdicts.
- Check any copy the judge proposes against your product's voice rules before you apply it.
- 8/10 means "I would ship it as is". Do not call a screen done below that without telling the user.
- Do not trust "it renders, so it matches the mock". The judge looks at the built page, not the mock.
- Set a cap before you start (for example 5 rounds). If the score stalls for two rounds, the structure is wrong. Stop and ask the user one question.
- For a landing page, add other judges with other lenses (for example clarity of message, and honest claims). One designer's score is not enough there.

## Traps

| Trap | Instead |
| --- | --- |
| Judging only the happy path | Shoot the hard states in round 1 |
| Trusting the author's list of changes | Treat it as claims; pixel-diff against last round |
| The judge re-raises settled decisions | Put them in the "Decided and final" list |
| Judge edits files | Constraint: it writes the verdict file only |
| Scoring a mock and calling the live build done | Judge the live build with screenshots of every state |
| Shipping at 7 because it is "close" | 8 is the bar; tell the user if you stop below it |
