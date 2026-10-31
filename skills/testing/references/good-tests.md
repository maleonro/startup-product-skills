# What a good test looks like

Copy this standard, not the spec next to your file.

## The external edge

A test may fake only systems you do not control, at the **outermost port you own**. Mock
the whole client, not the HTTP library under it.

Typical edges: payment and billing providers, email and SMS senders, LLM providers,
object storage, third-party APIs, queues and durable-workflow engines, analytics, the
clock. Reuse the fake your repo already has. If there is none, write a recording fake
and list it in your testing guide.

- A **fake** is a working implementation that records what happened (`sent`, `enqueued`).
  The test asserts state. Prefer a fake over a `vi.fn()`-style mock.
- A fake must never be more capable than production.
- A port implemented by another module of your own is **your code**, not an edge. Wire
  the real implementation.
- Fake time by injecting a clock. Fake timers do not reach the database's own `now()`.
  When time matters, write timestamps yourself with fixed dates.

## Anti-patterns

Each one comes with the better choice.

- **Never fake storage.** No `{ findById: mock }`, no Map-backed repository, no
  cast-to-the-interface stub for your own tables. If the logic only needs data, make it a
  pure function. If it needs persistence, seed and assert against the real test database.
  The single exception: simulating a storage *failure*. Prefer a real failure (a trigger
  that rejects writes) to a subclass.
- **Never mock your own services or modules.** Not even a dependency of the class under
  test. The boundary is ownership, not depth. In frontend tests, never mock your own
  hooks, API modules or child components.
- **No change-detector tests.** Do not assert *which* of your methods were called, or in
  what order. They break on every refactor and catch no bug. Assert the outcome. A call
  assertion is fine **only at an external edge, where the call is the effect**: the email
  reached the sender, the order reached the vendor.
- **Never pass `undefined` or a cast `{} as never` for a collaborator the path can reach.**
  It hides a crash behind a green test. `undefined` is fine only for an optional
  dependency the path provably never touches. Add a one-line comment saying why.
- **No partial fakes by cast.** Type fakes and fixtures fully (`satisfies Port`) so they
  cannot drift from the real type.
- **Do not read production source in a behavior test** (`readFile` plus `toContain`).
  That is a change detector. Put the rule in a lint, or test the rendered behavior.
- **Do not assert class names or DOM structure** unless the class *is* the behavior.
  Prefer visibility checks, role queries and text.
- **Do not test a hook alone** when one component uses it. Test through the component.
- **Never bend a test for coverage.** No stubbing child components so their branches
  leave the coverage count.
- **No sleep for synchronization.** Use polling helpers, `findBy*` queries or fake
  timers. Never wait on a production timer (debounce, poll interval, backoff). Make the
  duration injectable, keep the production default, set it near zero in the test.
- **No test-only methods in production code.** Put helpers in test files.
- **No conditional assertions.** No `if (...) expect(...)`. No assertion inside a `catch`.
  An `if` that may not run is an untested branch.
- **No order-dependent asserts on unordered results.** Sort both sides, or compare sets.
- **Tests never read live config or the real date.**
- **No production data in fixtures.** Invent it.

## Conventions

- **A test earns its place.** It protects observable behavior against a plausible
  regression that no existing test catches. Skip tests whose only value is locking a
  constant, trivial wiring, library behavior, or the current implementation.
- **Every production bugfix needs regression evidence.** Add a test that fails before the
  fix and passes after. If a test would be low-value, say why. Then give the cheapest
  reliable evidence: existing coverage, a type or lint check, or a live check.
- **"Already caught" means an existing test goes red.** Make the edit and run the suite.
- **Extend before you create.** Add to the existing suite or table first.
- **Coverage is a floor, not a reason.** "Raises coverage" never justifies a test.

## Size and shape: DAMP, not DRY

A test body fits on one screen: **aim for 25 to 30 lines, never more than about 45.** It
reads as a straight line: *arrange the state, run the action, assert the outcome.* A long
hard-coded expected value does not count against the limit. Full equality beats brevity.

Production code is DRY because tests catch its mistakes. A test has nothing testing it,
so write it to be understood alone: **DAMP** (Descriptive And Meaningful Phrases).

- Details **irrelevant** to the case (the tenant, unrelated required columns, wiring) go
  in helpers.
- The inputs and expectations that **define the case** stay visible in the body. They are
  what makes this test pass and its neighbor fail.

Prefer `makeUser({ email: 'not-an-email' })` to `seedUserWithInvalidEmail`. The second
name is where per-case flags start creeping into shared code. Prefer a little duplication
to the wrong abstraction. Wire the system under test in `beforeAll` or `beforeEach`.

## Seeding data

- **Seed through the domain API** when one exists.
- **Raw inserts only when no domain API exists.** Hide them in one helper with a complete
  valid default plus overrides. The override is the case. The default is noise.
- **Use discriminating fixtures.** Use distinct values in fields that could be confused
  (first versus last name, user slug versus company slug). Identical values hide
  swapped-field bugs. Use `'ada-lovelace'` and `'grace-hopper'`, not `'U'` and `'U'`.
- **Read results back through the product's own read path** when one exists. No raw SQL
  strings in tests.
- **Ids are fine when the test made them.** Never hard-code an id the code under test
  generates.

## Asserting

- **Assert full equality on the business outcome**: the whole result, row, response or
  message. Use **hard-coded expected values**.
- **Never compute the expectation with the logic under test.**
- **No spot checks.** `expect(x.status).toBe('ok')` alone, `toBeDefined()`, a lone length
  check, and `objectContaining` all pass no matter what garbage the rest holds. Use a
  partial match only for fields that are irrelevant *and* vary (generated ids,
  timestamps). Say so in a comment.
- **Errors:** assert the error code, **all its params** and its field errors. Then assert
  that nothing was written. A subset matcher passes for any params, so compare params in
  full. Use a small helper that returns what a refused call surfaced:

  ```ts
  async function refusalOf(call: Promise<unknown>) {
    const err = await call.then(() => null, (e) => e);
    return err && { code: err.code, params: err.params, fieldErrors: err.fieldErrors };
  }

  expect(await refusalOf(service.update(tenant, item.id, { endDate: '2026-05-01' }))).toEqual({
    code: 'VALIDATION_FAILED',
    params: {},
    fieldErrors: [{ field: 'endDate', code: 'custom', params: {} }],
  });
  ```

## Table-driven tests

Use a table **only when the bodies are identical and only input and output vary.** If you
must parametrize the setup, or add a conditional to the body, write separate tests. Never
loop over cases inside one test, because a failure then hides which case broke. Key cases
by name so duplicates are impossible:

```ts
const cases = {
  'simple': { input: 'a/b/c', want: ['a', 'b', 'c'] },
  'trailing separator': { input: 'a/b/c/', want: ['a', 'b', 'c'] },
} satisfies Record<string, { input: string; want: string[] }>;

it.each(Object.entries(cases))('%s', (_, { input, want }) => {
  expect(split(input, '/')).toEqual(want);
});
```

## Frontend specifics

- Query by role, then label and text. Test ids are the last resort.
- Render with the app's own providers, router and error handling. Answer the API with a
  fake server that replaces `fetch`, so your real API layer runs.
- Assert what the user sees, and the request that reached the server with its **full
  body**.
- Type every fake response with the shared contract type, so a contract change breaks
  the test.
- Mock only third-party modules that cannot run in the test environment.

## Guard suites

Tests that lint the codebase (no storage fakes, no mocks of own modules) are fine and
useful. Add one so the rules above stay true. Keep them separate from behavior tests.
They are not a model for behavior tests.
