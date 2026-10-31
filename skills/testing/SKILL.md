---
name: testing
description: Decide what to test and write the tests. Mostly integration tests, a real test database, fakes only at the external edge, every test earning its place, tests proposed before they are written. Use when writing, adding or improving tests; after implementing a non-trivial change (propose the tests first); when a bugfix needs regression evidence; when a TDD loop reaches "write the test"; or when asked "what tests does this change need?", "write tests for this", "add tests", "is this test worth keeping?".
---

# testing

This skill decides *what* to test, then turns the answer into a small, strong suite.

> Write tests. Not too many. Mostly integration.

A test runs from the highest level that is practical, with the fewest mocks possible.
The more you mock, the less a green run tells you. The lower the level, the more the
test depends on today's implementation, so a refactor forces a rewrite.

This skill ships two reference files in the same directory:

- [`references/failure-modes.md`](references/failure-modes.md): a checklist of failure modes to scan while planning.
- [`references/good-tests.md`](references/good-tests.md): what a good test looks like, and the anti-patterns.

## Set up once: the golden list

Existing specs are not a reference. Most suites carry old habits, and copying a nearby
spec is how a bad pattern spreads.

Before the first use, pick **3 to 5 suites in your own repo** as the golden list: one
per kind of test you use (see the table below). Pick the closest to the standard in
`references/good-tests.md`. For each, write one line: what to copy, and what NOT to copy.
Save the list in your repo's testing guide, or in the PR description. When you need an
example, open these suites, not the spec next to your file.

If the repo has its own testing guide, read it first. Where it disagrees with this
skill, the repo guide wins.

## 1. Read the code

- Read the code under test in full. Read the door a caller reaches it through (HTTP
  route, CLI command, job handler, tool, component).
- Find the existing suite for it. **Extend it before you create a file.** The exception:
  the suite fakes storage or mocks your own code. Then do not add to those fakes. Write
  the new cases in a real-database suite next to it, and say so in the PR.
- Check any spec you want to copy against the golden list and the standard. If they
  differ, the standard wins. Ask the user only when the intended *behavior* is unclear.

## 2. Plan: what are we testing?

Split the input and state space into **equivalence classes**: groups the system treats
the same way. Write one test per class. A list of 2 items and a list of 3 items are one
class ("more than one item").

- **Happy paths.** Which kinds of input are supported?
- **Failures.** Scan `references/failure-modes.md`. For each mode, find the input or
  state that triggers it in this code.

**Black box first, then white box.** Split by the contract: what should happen for each
kind of input. Then read the implementation. It shows edge cases the contract misses,
and cases the code treats the same (merge those). Use branches to find cases. Assert
only observable behavior, so a refactor that keeps behavior never breaks the test.

**Litmus test: if one realistic code edit breaks input A but not input B, they are
different classes.**

For each candidate test, write **one sentence: why does it earn its place?** Name the
edit that would break it. Say why that edit is realistic. Example: *"If someone drops the
tenant filter from `TagService.forSubject`, another tenant's tag shows up and this test
fails."* "Increases coverage", "good practice" and "the function exists" do not count.
No sentence, no test.

Then check two things:

1. **Nothing already catches it.** An existing test would go red with your edit. Run the
   suite to know. If one does, extend that test or add a table row instead. A spot check
   that stays green does not count.
2. **You own it.** Test your logic, not that the ORM, the validation library or the HTTP
   framework works. DO test how your code handles their failures.

### Choose the kind of test

| Kind | When | Setup |
| --- | --- | --- |
| **1. Integration through the door** (default) | Any behavior a caller can reach: a route, a command, a job, a webhook, a tool | Real test database, real repositories and services, the real door. Fakes only at the external edge |
| **2. Module suite, real database** | Behavior that stays inside one module: an invariant, query semantics, paging, tenancy, upserts | Real test database, real collaborators |
| **3. Pure unit** | Logic with no I/O: parsing, templating, scoring, date math | None. If the logic only needs data, extract a pure function that takes domain types |
| **4. External client suite** | Your code that talks to a vendor | The real client over a stubbed HTTP layer. Assert the full request (URL, method, headers, body) and the mapping of real, recorded responses |
| **5. Component test** | A screen or component | Render with the app's real providers, answer the API with a fake server. Query by role, act like a user, assert what the user sees |
| **6. End-to-end** | A cross-screen flow on the real stack | Few. Only for flows that must never break |

**Test at the level where the behavior is decided.** If every door only delegates to one
service, a kind 2 suite on that service is the right level. Add a door test only for what
the door itself decides: validation, auth, the shape of the response.

A pure unit test (kind 3) needs a stated reason. "It was easier" is not one. Speed is
never a reason to fake storage: clone a migrated template database per worker, and a real
database is fast.

**Never fake storage.** If you reach for a repository mock to feed data, make the
function pure, or use the real test database. The one exception is simulating a storage
*failure* a real database cannot produce on demand.

### Build two lists

**Tests to write:**

| Test | Kind | Why it earns its place: the edit that breaks it, and why it is realistic |
| --- | --- | --- |
| Adding a person to the block list removes them from every campaign | 1 | If the sweep call is dropped from `BlockList.addPerson`, the person stays in live campaigns and keeps getting messages |
| A tag from another tenant is refused and nothing is written | 2 | If `setTags` stops scoping the lookup by tenant, a cross-tenant id tags the subject |
| A missing `{{slot}}` is named, not silently blanked | 3 | If `renderTemplate` stops reporting `missing`, the sender ships a blank hole |

- **Kind** is 1 by default. Justify every 3.
- One independently breakable branch is one row. One failure mode is one test.

**Tests to skip:**

| Skip | Why |
| --- | --- |
| `isActive()` getter | One line. The callers' tests cover it |
| Validation library rejects a wrong type | Library behavior. You only declare the schema |
| The controller forwards to the service | Pass-through. The integration test through the door covers it |

### Red flags: too many tests

- **Testing library behavior.** "The validator rejects a string". "The ORM orders by id".
- **Vague reasons.** "Critical", "error-prone", "must work". Which bug, in your code?
- **Testing one-liners.** Getters, pass-throughs, a controller that only delegates.
- **Several tests for one failure mode.** Merge them, or make a table.
- **Unit tests where integration works.** The goal is "mostly integration".
- **Inconsistent reasoning.** Skipping one helper as "trivial" but testing its twin.

### The filtering mindset

**Look for reasons NOT to write each test.** If there is no strong reason to skip it, it
belongs. If you are stretching to justify it, skip it. Judge each behavior on its own,
even inside a big feature.

### Risk slices (large features only)

Group the tests into slices to keep a budget:

- Happy path and invariants
- Validation failures
- Idempotency and duplicates (retries, a webhook delivered twice)
- External dependency failures (vendor errors, the LLM, the queue)
- Authorization and tenancy (another tenant's id is a not-found, never a touch)

Budget 1 to 3 tests per slice. Past about 8 tests total, go back to the skip table. A
table of cases counts as one test.

## 3. Propose, then write

**Show both tables to the user before you write any test.** Wait for a yes on anything
non-trivial. Put the same tables in the PR description (or the plan doc) so a reviewer
sees them.

Then write:

- Use the repo's test harness: boot the real app or module, hit the real door.
- Use real services. Fake only at the external edge, with a working fake that records
  what happened. Reuse the repo's existing fakes. If the edge has none, write one and
  list it in your guide.
- Seed through the domain API when one exists. Use raw inserts only when none exists,
  hidden in one helper with a complete valid default plus overrides.
- **Test behavior, not implementation.** A refactor that keeps behavior must not break
  the test.
- Assert observable outcomes: the return value, the row read back, the response, what
  the user sees, the request that reached an external edge.
- Avoid generated ids in assertions, the real clock, sleeps, order dependence between
  tests, `undefined` for a collaborator the path reaches, and partial fakes made by cast.

**The code must match the table.** No test that is not in it. If you find a new case while
writing, add it to the table, with its sentence, first.

## 4. Run

Run the focused test first, then the package, then the full suite at the end. Use your
repo's commands. Start the test database before the run if the suite needs it.

## 5. Prove each test can fail

**Break the code on purpose.** For each new test (at least one per slice), make the edit
named in its "earns its place" sentence. Run the test. Watch it go red for the right
reason. Then revert the edit. A test that always passes is worthless.

For a bugfix, the regression test must fail on the old code and pass with the fix.

Say in your report which edits you tried.

## 6. Self-check

Before you present the work:

- [ ] Every test written is in the plan table. Every obvious case skipped has a reason.
- [ ] No anti-pattern from `references/good-tests.md` is present. In particular: no
      faked storage, no mock of your own code, no call assertion on your own
      collaborator, no `undefined` for a reachable dependency.
- [ ] For every critical branch, you can name the test that fails if it is deleted.
- [ ] Boundaries are covered or skipped on purpose: empty, null, max, off-by-one.
- [ ] Every unit test (kind 3) has a reason it is not an integration test.
- [ ] You broke the code for at least one test per slice and saw it fail.
- [ ] The focused test command passed.
- [ ] No production data in fixtures. Invent it.

## Traps

| Trap | Instead |
| --- | --- |
| Copying the spec next to your file | Copy from the golden list |
| Writing tests to raise coverage | Write a test only if you can name the edit that breaks it |
| Mocking your own service "just here" | Wire the real one, or the edge fake |
| Asserting that a method was called | Assert the outcome. Call assertions fit only at an external edge, where the call is the effect |
| Computing the expected value with the logic under test | Hard-code the expected value |
| Writing tests, then showing the plan | Show the plan first |
