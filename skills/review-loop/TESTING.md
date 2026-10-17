# Testing guidelines

What a good test looks like. The rubric's standard 7 judges tests against this file.
If your repo has its own testing guide, that one wins. If it does not, copy this file
into your repo, fill in the [golden list](#golden-list) and point your team at it.

Stack-neutral. The examples use JavaScript/TypeScript test syntax (`expect`, `vi.fn()`,
`jest.fn()`), but every rule applies to pytest, Go's `testing`, RSpec or JUnit.

## The principle

> Write tests. Not too many. Mostly integration.

Exercise a behavior **from the highest level that is ergonomic, with the fewest mocks
possible.** The more you mock, the less a green run tells you about how the pieces fit.
The lower the level, the more the test is coupled to today's implementation, so a
refactor forces a rewrite.

- **Not too many.** A higher-level test covers more behavior, so you need fewer. The goal
  is catching regressions that matter, not raw coverage.
- **Mostly integration.** Real database, real services. Fake only what you do not control.

**Existing tests are not a reference.** Copying the spec next to your file is how a bad
pattern spreads. When a nearby test disagrees with this file, this file wins. Your
golden list is the reference.

## Test kinds: pick the highest that works

| Kind | When | Setup |
| --- | --- | --- |
| **1. Integration through the door** (the default) | Any behavior a caller can reach: an HTTP route, a CLI command, a job handler, a webhook, a tool an agent calls | Real test database, real services, the real entry point. Fakes only at the [external edge](#the-external-edge). |
| **2. Module suite on the real database** | Behavior inside one module that does not cross a door: a service invariant, a query's semantics (paging, tenancy, upserts) | Real test database, real repositories, the service built with its real collaborators. |
| **3. Pure unit** | Logic with no I/O: parsing, templating, validation, scoring, date math | No setup. If logic only needs data, extract it as a pure function and test that. |
| **4. External client suite** | Your code that talks to a vendor API | The real client over a stubbed HTTP layer. Assert the full request (URL, method, headers, body) and the mapping of real responses you captured from the live API. |
| **5. UI component test** | A screen's or component's behavior | Render it with the app's real providers (router, data cache, notifications) and a fake API server. Query by role, act like a user, assert what the user sees and the requests that reached the server. |
| **6. End-to-end** | A cross-screen flow against the real stack | Few, only for the flows that must never break. |

**Test at the level where the behavior is decided.** If a route only delegates to one
service, a kind-2 suite on that service is the right level. Add a door test only for
what the door itself decides: validation, auth, mapping to the wire shape.

**Unit tests need a reason.** "It was easier" is not one. Make the test database fast
(a migrated template cloned per worker, or a transaction rolled back per test) so
**speed is never a reason to fake storage.**

## The external edge

What a test may fake: systems you do not control, at the **outermost port you own**.
Mock the whole client, not the HTTP library under it. Typical edges:

- Third-party APIs: payments, email delivery, CRM, social networks, enrichment vendors.
- LLM calls. Fake the model's answer, keep your own agent loop and prompt building real.
- Queues, durable workflow engines, object storage, the realtime push channel.
- Product analytics and the logger.
- Time. Inject a clock or use fake timers. In a database test, fake only the date, so
  the driver's own timers keep running.
- The browser's calls to your API, in UI tests: a fake server that replaces `fetch`,
  so your real API client runs.

**A port implemented by another of your own modules is your code, not an edge.** Wire
the real implementation, even if it costs some setup. A recording fake of the port is
acceptable only if the real one drags in a whole subsystem the behavior does not depend
on, and a comment says why.

A **fake** is a working implementation that records what happened (`sent`, `enqueued`),
so the test asserts state. Prefer a fake over a bare mock. A fake must never be more
capable than production: if the real vendor refuses something, the fake refuses it too.

Keep one fake per edge, in a shared `testing/` folder, and reuse it. If an edge has no
fake yet, write a recording one and add it to your golden list in the same PR.

## Anti-patterns

Each one with the right alternative.

- **Never fake your own storage.** No `{ findById: vi.fn() }`, no partial object cast to
  a repository type, no Map-backed repository for your own tables. If the logic only
  needs data, make it a pure function (kind 3). If it needs persistence, seed and assert
  against the real test database. The one exception: simulating a storage *failure* a
  real database cannot produce on demand. Even then, assert the observable reaction
  (error code, fallback, retry), never the call. Better still, make the failure real
  (a trigger that refuses the write).
- **Never mock your own services or modules**, not even a dependency of the class under
  test. The boundary is ownership, not depth. In UI tests, never mock your own hooks,
  API modules or child components.
- **No change-detector tests.** Don't assert *which* of your methods were called or in
  what order (`expect(ourService.method).toHaveBeenCalledWith(...)`). They break on every
  refactor and catch no bug. Assert the observable outcome: the return value, the row
  read back, the HTTP response, the text on screen. A call assertion is legitimate
  **only on an external edge, where the call is the effect**: the email reached the
  provider, the request body reached the server.
- **Never pass `undefined` or an empty stub for a collaborator the path can reach.** It
  hides a crash behind a green test. Wire the real service, or an edge fake.
- **No partial fakes by cast.** `{ ...only what this test needs } as Port` is how a fake
  drifts from the real type. Type fakes and fixtures fully.
- **Don't read production source in a behavior test** (read the file, assert it contains
  a class name). That is a change detector. Put the rule in a lint, or test the behavior.
- **Don't assert class names or DOM structure** in UI tests unless the class *is* the
  behavior. Prefer visibility, role queries and text.
- **Don't test a hook alone when one component uses it.** Test through the component.
- **Never bend a test for coverage**, for example stubbing child components so their
  branches leave the coverage denominator.
- **No sleeps for synchronization.** Use a wait-for helper, polling assertions, or fake
  timers. **Never wait on a production timer** (debounce, poll interval, backoff): make
  the duration injectable, keep the production default, set it near zero in the test.
- **No test-only methods in production code.** Helpers live in test files or `testing/`.

## Conventions

- **A test must earn its place.** It protects observable behavior against a plausible,
  relevant regression that no existing test catches. Skip tests whose only value is
  locking down a constant, trivial wiring, library behavior or the current
  implementation. Judge per behavior, not per PR.
- **Every production bugfix needs regression evidence.** Add a test when it clears the
  bar above: it fails on the base branch and passes with the fix. Otherwise, say why a
  test would be low-value and give the cheapest reliable evidence instead (existing
  coverage, a type check, a live check). No new test is not, by itself, a finding.
- **"Already caught" means an existing test goes red.** Make the edit your test is meant
  to catch and run the existing suites. If they stay green, nothing catches it.
- **Extend before you create.** Add to the existing suite before making a new file,
  unless that suite fakes storage or mocks your own code. Then write the new cases in a
  real-database suite next to it.
- **Coverage is a floor, not a reason.** "Raises coverage" never justifies a test.
- **No conditional assertions.** No `if (...) expect(...)`, no `try { } catch { expect }`.
  An `if` that may not run is an untested branch.
- **No order-dependent asserts on unordered results.** Sort both sides, or compare sets.
- **Tests never read live config** (real environment files) and never depend on the
  real date.
- **Fake timers do not reach the database.** A column the database stamps with `now()`
  follows the database clock, not your fake one. When time matters, write the
  timestamps yourself with fixed dates.
- **No production data in fixtures.** Never paste a real customer, message or email
  into a test. Invent it.

### Size and shape: DAMP, not DRY

A test body fits on one screen: **aim for 25–30 lines, never more than about 45.** It
reads as a straight line: *arrange this state → run this action → assert this outcome.*
A long hard-coded expected value does not count against the limit.

Production code is DRY because tests catch its mistakes. A test has nothing testing it,
so optimize it to be understood alone: **DAMP** (Descriptive And Meaningful Phrases).

- Details **irrelevant** to the case (the connection, the tenant, required-but-unrelated
  columns, wiring) go in helpers.
- The inputs and expectations that **define the case**, what makes this test pass and
  its neighbor fail, stay visible in the body.

Prefer `makeUser({ email: 'not-an-email' })` over a helper named
`seedUserWithInvalidEmail`. Prefer a little duplication over the wrong abstraction.

### Seeding data

- **Seed through the domain API** when one exists: the service method that creates the
  aggregate with its related rows.
- **Raw inserts only when no domain API exists**, hidden in one helper with a complete
  valid default plus overrides: `makeOrder({ status: 'paid' })`. The override is the
  case; the default is noise.
- **Discriminating fixtures.** Use distinct values in fields that could be confused
  (first vs last name, two different ids). Identical values hide swapped-field bugs.
  `'ada-lovelace'` and `'grace-hopper'`, not `'u'` and `'u'`.
- **Read results back through the product's read path** when one exists. No raw SQL
  strings in tests.

### Asserting

- **Assert full equality on the business outcome** (the whole result, row or response)
  with **hard-coded expected values**: `expect(names).toEqual(['gatekeeper', 'warm'])`.
- **Never compute the expectation with the logic under test.**
- **Ids are fine when the test made them.** Never hard-code an id the code under test
  generates.
- **No spot checks.** `expect(x.status).toBe('ok')` alone, `toBeDefined()`, a length
  check alone and partial-match helpers pass no matter what garbage the rest holds. Use
  partial matching only for fields that are genuinely irrelevant *and* vary (generated
  ids, timestamps), and say so in a comment.
- **Errors:** assert the error code and all its parameters, then assert nothing was
  written.

### Table-driven tests

Use parameterized tests **only when the bodies are identical and only input and output
vary.** If the setup changes or the body needs a conditional, write separate tests.
Never loop over cases inside one test: a failure then hides which case broke. Key cases
by name so duplicates are impossible:

```ts
const cases = {
  'simple': { input: 'a/b/c', want: ['a', 'b', 'c'] },
  'trailing separator': { input: 'a/b/c/', want: ['a', 'b', 'c'] },
};

it.each(Object.entries(cases))('%s', (_, { input, want }) => {
  expect(split(input, '/')).toEqual(want);
});
```

### UI specifics

- Query by role, then label and text. Test ids are the last resort.
- Assert what the user sees, and the request that reached the server with its **full
  body**.
- Assert a notification by its text and a redirect by the resulting path, not by
  mocking the router or the toast library.
- Type every fake API response with the shared contract type, so a contract change
  breaks the test.

## Golden list

Fill this in for your repo: one reference suite per test kind, what to copy from it and
what not to. When someone needs an example, they open these, not the spec next to their
file. None has to be perfect; the last column says what to avoid.

| Kind | Suite | Copy this | Do not copy |
| --- | --- | --- | --- |
| 1. Integration through the door | `path/to/…` | | |
| 2. Module suite on the real database | | | |
| 3. Pure unit | | | |
| 4. External client | | | |
| 5. UI component | | | |

## Credits

Adapted from the testing skill in
[Primo's public skills](https://github.com/primo-devs/public-skills). "Write tests. Not
too many. Mostly integration." is Guillermo Rauch's line, popularized by Kent C. Dodds.
The change-detector rule follows Google's "Change-Detector Tests Considered Harmful".
