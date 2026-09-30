# Juan: an AI design judge to raise the taste bar

Juan is a subagent, not a style guide. You build the evidence (mocks, screenshots). He looks at it and writes a verdict file with a score and exact fixes. You apply the verdict and run the next round. He never edits the repo.

The point is taste you can iterate on. A model asked "is this good?" says yes. A model given a named bar, a strict lens, measurements and a score to beat finds what is generic, and says how to fix it.

## Give him a bar

Juan is modeled on one real designer whose work sets the bar (Kairon's Juan: the designer-founder of Ato, with heyato.ai/launch as the reference). Pick yours: a product whose design you'd be proud to be compared to. Name it in the prompt. A named bar beats a list of adjectives.

## His lens

Visual craft. One idea per area. The interface carries the meaning, not a caption. Low cognitive load. Nothing generic. Every pixel earns its place. He **measures** (positions in device pixels, hit areas, pixel diffs); he does not guess.

## Launch

- `Agent` tool, `subagent_type: "general-purpose"`, on your strongest model.
- The prompt is the template in [JUAN-PROMPT.md](JUAN-PROMPT.md). Fill every `{…}`. Never drop the constraints block: it is your design system, and without it he redesigns your brand.
- One Juan per round. Relay his score and top 3 issues to the owner in plain words.

## Two modes

**1. Plan mode (design partner).** While the page or flow is still a plan, before code.
- Give him the real screens of today and the proposed structure (the copy document, a rough mock).
- Ask for structure: sections, what each one asks of the reader, the states. No score, or a score of the plan only.
- His output feeds the plan. It is not a sign-off.

**2. Judge loop (mock, then live).**
1. **Mock.** An HTML mock with the real design tokens from your code (the code is the source of truth for colors, fonts, radius) and real data, anonymized. Show "today" beside "proposal".
2. **Shoot.** Screenshots with Playwright, light and dark, at every width.
3. **Round.** Juan writes `verdict-juan-rN.md`. Apply the fixes. Repeat until 8/10.
4. **Live.** Build it. Judge the REAL page, not the code: screenshots of every state. Force states by intercepting API responses; log in once and reuse the session.

## Shoot the hard states in round 1

Every round of a Kairon loop that went 6 → 7 → 7.5 → 8 was caught on something missing from this list. Shoot them all up front:

- Every viewport: large desktop, the width where the layout changes, short laptop heights, phone.
- Light and dark.
- Every locale (long Spanish or German strings break what English fits).
- For an app screen: every role and permission, every billing state, empty, loading, error, and the worst case where all of them pile up.
- Real hit areas (he measures them) and one action at a time per block.

## Every round after the first

- Give him his previous verdict. Ask for **fixed / partly / not** per issue, with evidence.
- List what changed as **claims to verify, not to trust**.
- Ask for a pixel diff against the previous round. A "visually neutral" refactor once moved two things nobody else saw.
- List the decisions that are final, so he doesn't re-raise them every round.
- After a code-review round, re-shoot before the next Juan round. Juan and a code reviewer can run in parallel on the same shots.

## For a landing: a panel

On Kairon's home, Juan sat on a panel of three lenses: Juan (visual craft), the founder (synthesis: does it say what we are) and the growth owner (acquisition and truth: will it convert, is every claim true). Run Juan as the subagent; the other two are people, or two more subagents with those lenses. They disagree on purpose. The owner breaks ties.

## Rules for you

- Evidence lives in a scratch folder. Never commit screenshots or verdicts.
- Check any copy he proposes against your voice rules before applying it.
- 8/10 means "I would ship it as is". Don't call a page done below that without telling the owner.
