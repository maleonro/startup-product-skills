# Thermo-Nuclear Code Quality Review

Strict review of whether the PR makes the codebase **simpler, more direct, and
better anchored by tests**, not merely "working."

The reviewer applies this file to the branch diff and writes findings. It fixes
nothing.

## Posture

- **Be ambitious.** Look for the *code-judo* move that **deletes** complexity
  (whole branches, helpers, modes, layers). A refactor that only rearranges the
  same complexity doesn't count.
- **"Behavior preserved" is only credible if a test says so.** No test → no
  proof; the claim is unverified.
- **Code that resists testing is telling you the design is wrong.** Hidden
  state, untyped seams, and mock-of-mock setups are design smells, not test
  smells.
- **Following the letter while violating the spirit is still violating it.**
  Don't rubber-stamp work that satisfies a checklist but leaves the codebase
  messier.

## Standards

One concern per line. Each is a presumptive blocker if violated without a
strong, explicit justification.

1. **No file crosses 1k lines as a result of this PR.** Default action:
   decompose first.
2. **No ad-hoc conditional bolted into an unrelated flow.** Push the logic
   behind a dedicated abstraction, state machine, or module.
3. **Direct, boring code beats magical or identity-wrapped code.** Delete thin
   wrappers and generic mechanisms that hide simple data shapes.
4. **Type and boundary contracts are explicit.** Question every `any`/`unknown`/
   cast/optional and every silent fallback that papers over an unclear invariant.
5. **Logic lives in the canonical layer; reuse existing helpers.** Flag feature
   logic leaking into shared paths, code in the wrong package, and bespoke
   duplicates of existing utilities.
6. **Independent work runs in parallel; related state changes are atomic.**
   Flag avoidable serialization and partial-update flows.
7. **Behavior added or claimed-preserved is anchored by a test at the right
   level.** Untested behavior, tests that mock the thing under test, and tests
   asserting implementation details are all structural defects. If a change
   can't be cleanly tested, the **design** is the bug, not the test. Judge tests
   against the repo's testing guide, or [`TESTING.md`](TESTING.md) when it has
   none: faked storage, mocks of our own code, call assertions on our own
   collaborators and spot-check asserts are findings. Untested behavior is a
   finding when a test would earn its place there, not by itself.

## Primary questions

- Is there a **code-judo move** that makes whole branches or layers disappear?
- Does the diff add complexity at a **seam**, a place where the next change
  will compound it?
- Where is the test that **proves** the behavior this PR adds or preserves, and
  is it testing behavior or implementation details?
- Did this PR cross a **size, layer, or duplication boundary** that it shouldn't?

## Output

Lead with **structural regressions** and **missed code-judo moves**, then
**test gaps** (untested behavior, wrong-level tests, fragile mocks), then
boundary / type / file-size concerns. Cosmetic nits only after structure and
tests are clean. Few high-conviction findings beat a long list.

## Approval bar

Approve only if **no standard above is violated without a justification the
author can defend**. Never approve on "it works" alone.

## Tone

Direct and serious, not rude. Shape feedback as *"this works, but X — can we Y?"*:

- `this pushes the file past 1k lines — decompose first?`
- `this adds a special case into an already busy flow — move it behind its own abstraction?`
- `i don't see a test asserting the new behavior — what proves this is preserved?`
- `this test mocks the thing it's supposed to verify — can we test the actual behavior?`
- `there's a code-judo move that makes these branches disappear — can we reframe the model?`
- `bespoke helper for something we already have — reuse the canonical one?`
- `why the cast / optional here — can we make the boundary explicit instead?`
