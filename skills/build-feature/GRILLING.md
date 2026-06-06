# Grilling the design

The grill is the bridge between a loose idea and a writable plan. It runs after brainstorming and before the plan doc. The goal is a shared understanding with **no open branches**, not a fixed number of questions.

## Which skill

- `grill-me` — default. Interview the user relentlessly, walking down each branch of the decision tree, resolving dependencies between decisions one by one.
- `grill-with-docs` — when the project has a domain glossary, `CONTEXT.md`, or ADRs. Same grilling, but it sharpens terminology against the existing domain model and updates the docs inline as decisions crystallize.

## How to run it

1. Lay out the decision tree: every choice the design forces (scope, data source, time windows, who-can-do-what, edge cases like empty/zero results).
2. Take one branch at a time. Resolve it before opening the next. When a decision depends on an earlier one, surface that dependency explicitly.
3. For each branch, either get a decision from the user or propose the best-practice default and confirm it.
4. End only when every branch is closed. Then write the plan (step 4 of the main workflow).

## How the user answers (match this rhythm)

- Short and decisive: "for v1 go with A", "yes, only people we messaged".
- Delegates to best practices when indifferent: "whichever is better for UX", "pick a sensible outreach floor".
- Flags real product concerns mid-grill (e.g. "why create an audience if it's really just a list you can't edit?") — treat these as new branches to resolve, not noise.

## Anti-patterns

- Writing the plan with branches still open.
- Asking questions whose answer is already implied by an earlier decision.
- Stalling on a branch the user is indifferent about instead of proposing a default.
