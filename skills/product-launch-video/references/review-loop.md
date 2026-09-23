# The design-judge loop

A strict, read-only design subagent judges the plan, then each render, until it scores 8/10
("I would ship it as is"). If the repo has a named design judge (e.g. a `juan` skill), use it and
its prompt template; otherwise launch a general-purpose agent with the prompt below. One judge
across rounds (resume the same agent) keeps context; give it its previous verdict every time.

## Plan mode (before building)
Give it: the brief in the user's words, the research on the bar, the brand manual and site, the
real screenshots, and the current video if one exists. Ask for:
- a diagnosis with measurements (e.g. "16 chips, 58 moving words, 765 px/s"), not adjectives;
- a full storyboard: time, on screen, what moves, sound cue, exact copy, crop rects in source px;
- 2-3 alternatives for the riskiest part (usually the hook), ranked, with a recommendation;
- the decisions only the user can take, max 4, each with a recommendation.

## Live rounds
- Evidence: the MP4s plus full-size stills at key times (frame 0, each scene's first frame and
  midpoint, every transition, the end card). Tell it how to extract frames itself.
- List what changed as **claims to verify, not to trust**. When you deviate from its fix, say why
  (it may be wrong: a crop it proposed once cut a card by its own measurements).
- List **decided and final** items so it does not re-raise them.
- Ask for fixed / partly / not on every previous issue, pixel diffs against the last round, and
  issues most severe first with exact fixes (times, px, copy). Mark which block an 8.

## Rules for you
- Verify its measurements before applying them; re-crop and look.
- Its copy suggestions still pass the honesty rules and the truth check.
- The user's standing decisions beat the judge (e.g. a user who cut provenance captions from the
  site does not get them back because a judge asked).
- The bar can move: an 8.5 under "tidy" rules became a 4 under "YC launch" rules. When the user
  raises the bar, say so and re-plan rather than polishing.
- Taste calls the judge cannot make (music, which hook the user prefers): render 2-3 variants as
  props of the same composition and let the user choose.

## Prompt skeleton
```
You are a strict, read-only product designer and design judge. Lens: visual craft, one idea per
area, the interface carries the meaning, low cognitive load, nothing generic. You measure what you
claim (positions in px, speeds, pixel diffs); you do not guess.
The job: {product, audience, what the video must do, the user's words}.
Mode: {PLAN | LIVE round N}. Judge only {scope}.
Evidence: {paths}. Read your last verdict first: {path}.
What changed (claims to verify): {list}. Decided and final: {list}.
Constraints: {brand rules, honesty rules, copy rules}.
Write {verdict path}: score /10 (8 = ship as is), previous-issue check, what works (max 3),
issues most severe first with exact fixes, one bigger idea only if it clearly wins.
Never edit anything but the verdict file. Reply with the score and top 3 in under 150 words.
```
