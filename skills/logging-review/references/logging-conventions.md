# Logging conventions

A standard a team can adopt. It makes production debuggable from the log stream alone.
Adapt the names to your logger and framework. Keep the rules.

The one idea behind it: **a summary line is an addition, not the whole story.** A single
dense line per request (status, duration, counts) is a *summary* layered on top of
ordinary event logging. It never replaces it. A team that adopts only the summary line
goes blind: a job that did nothing leaves no trace, and an entity id matches almost no
lines.

## The three layers

| Layer | What | One per |
|---|---|---|
| **Summary** | One dense line for a whole unit of work: status, outcome, duration, counts | request, job or workflow run |
| **Event** | A line at each real decision, branch, skip, loop outcome and caught error *inside* a unit of work | decision |
| **Debug** | Verbose detail, level-gated, off in production by default | call site |

The summary tells you *that* a unit of work happened and how it ended. The event layer
tells you *what it did*. The event layer is the one teams forget, so it is the rule here.

## What to log: the four mandates

1. **Log every meaningful decision.** Each branch that changes the outcome gets a line:
   which path was taken, and why. "Nothing eligible", "day already claimed", "cap
   reached" and "filter excluded" are all lines.
2. **No silent branch.** When the code decides *not* to do the obvious thing (skip,
   dedupe, cap, early return, filter out), it leaves a trace. Silence must mean "did not
   run". It must never mean "ran and did nothing, for a reason you cannot see".
3. **No silent catch.** Every `catch` either rethrows or logs at `warn` or `error` with
   enough context to act. A swallowed error with no line is a defect.
4. **Loops over entities log per item.** A loop that creates or changes entities logs each
   item's outcome (`created`, `deduped`, `failed`). At high volume, log one aggregate line
   plus one line per failure. A dropped item is never invisible.

If you change a backend code path and add **zero** log lines, look again.

## How to tag: the correlation trio

Every line carries three keys. Attach them automatically, from a request-scoped context
(async local storage or your framework's equivalent), through a logger mixin or
middleware. Do not thread them by hand.

- **`traceId`**: which request or run. Use the active tracing span id when tracing is on,
  so it equals the trace id in your tracing backend. Fall back to an inbound
  request-id header, then to a generated id (for dev and test). Each async hop (a queued
  job, a workflow step) gets its own trace id plus a **`parentTraceId`** that links back
  to the hop that triggered it.
- **`tenantId`**: whose data. This is non-negotiable in a multi-tenant system. A line
  without it cannot answer "is *this customer's* automation working?". Set it in the
  auth guard (HTTP) or in the handler (jobs, workflows, webhooks).
- **`subjectId`**: *which entity* the unit of work is about, as the public id you
  actually search for (`order_…`, `campaign_…`). Carry a `subjectType` next to it. Also
  carry the raw database id if you want it paste-ready for SQL.

### Setting the subject

The subject comes from four places. The first two are free. The last two are your job.

| Source | Example | How |
|---|---|---|
| Path param | `GET /orders/:orderId` | Interceptor, automatic |
| Query param | `?orderId=order_…` | Interceptor, automatic |
| Body field | `POST /orders/ship { orderId }` | Call `setSubject(id)` |
| Created or resolved later | A `POST` that mints the id. A webhook's external id that a job resolves to an internal one | Call `setSubject(id)` once you know it |

`setSubject(id)` is a one-liner callable anywhere. Every line after it carries the id.
Never scan request bodies automatically. It is ambiguous (which field?), so the rule is:
**subject not in the path means set it explicitly.**

The payoff: one filter on `subjectId` rebuilds the whole life of an entity. It shows the
request, the cron that fanned it out, every job run and every child item, because the id
rides every line across every hop.

## Levels: three buckets

- **`error`**: the code threw. An engineer is needed. Keep it a reliable "something is
  broken" signal.
- **`warn`**: the code worked, but the outcome was adverse. A failed send, a canceled run,
  a deduped item, a capped turn. **A legitimately failed business action is `warn`, never
  `error`.**
- **`info`**: normal progress.

Then an alert on `error` only ever fires on real code breakage.

## PII: safe by default, then disciplined

- **The auto-attached context is structurally safe.** The context holds only ids (trace,
  tenant, subject, user). It has no field for an email or a secret, so the keys on every
  line cannot leak PII.
- **Ad-hoc fields are your responsibility.** The object you pass to the logger carries
  **only ids, counts and enums**. Never an email, name, phone, message body, tool
  argument, raw request or response object, or token. Backstops: configure the logger's
  `redact` option to censor known-PII keys, and audit the diff before each push.
- **Never** `logger.info({ req })`, `JSON.stringify(body)`, or a whole entity. Log the
  field you need, not the object that contains it.

## Wiring (so nobody re-invents it)

- **One log context** backed by async local storage, with setters for trace, identity
  (tenant, user), subject, outcome and error. The setters are safe no-ops outside a scope.
- **One mixin** projects `{ traceId, tenantId, subjectType, subjectId }` onto every line.
- **Every entry point opens the scope** and emits one summary line at the end: HTTP
  requests, queue jobs and workflow runs.
- **Everywhere else, just call the logger.** A decision is
  `logger.info({ itemId }, 'item enrolled')`. New code adds no new observer classes, no
  timeline modules and no per-line builders.
- Framework-free domain code that cannot import the logger takes a thin logger port
  (`info`, `warn`, `setSubject`). That is still "just call the logger".

## Worked example: a nightly enrollment job

Before: the due-check emitted nothing. The consumer logged one aggregate line only when it
claimed the day. The per-item loop and the filter logged nothing. A stuck item was
invisible.

After, the pattern to copy:

```ts
// dispatcher: the due-check is no longer dark
logger.info({ considered, due, skipped }, 'enrollment due-check');
for (const c of due) {
  logContext.setSubject(c.id);                 // the campaign id is now on every line below
  logger.info({ localDay }, 'campaign due, fanning out');
}

// consumer: the silent returns now speak
if (!claimed) { logger.info({ localDay }, 'enroll skipped: day already claimed'); return; }
if (remaining === 0) { logger.info({ usedToday }, 'enroll skipped: daily cap reached'); return; }

// the per-item loop: every outcome, every item
for (const m of memberships) {
  const run = await createRun(m);
  if (run) logger.info({ itemId: m.itemId }, 'item enrolled');
  else logger.warn({ itemId: m.itemId, reason: 'deduped' }, 'item skipped');
}
```

## Enforcement

- **A pre-push gate** that detects backend changes and points to the `logging-review`
  skill. It cannot verify the logs are *good*. It only makes sure someone looked.
- **The `logging-review` skill**: a diff-aware audit of the push against this file.
- **Contract tests** that hold the guarantees: the mixin puts the trio on every line, and
  scopes do not leak between concurrent requests. If someone rips the wiring out, CI
  goes red.
