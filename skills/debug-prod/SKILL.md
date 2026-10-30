---
name: debug-prod
description: Investigate PRODUCTION errors by joining signals on a trace id. Error tracking (what, who, when), logs, traces and metrics, read-only database queries, and LLM or agent traces. Use when a production error is reported, an error-tracker issue URL is shared, a deployed feature "isn't working in prod", an AI agent misbehaved, a job or campaign "did not run", or you need to read production logs or data. Reads real data before theorizing, gets the base rate, stays read-only, then hands off to a reproduce-and-fix loop.
---

# debug-prod

Find out what really happened in production. Read the real data first. Theorize second.

One id joins the signals: the **trace id**. A well-instrumented backend stamps it on the
error response the client sees, on every log line, on the trace, and on the error-tracker
event. So one bug report becomes a chain: an error-tracker issue, then the logs, then the
trace, then the database row, all on one id.

This skill covers gathering signal. For the fix, it hands off to a reproduce-then-fix loop.

## The rules

1. **Read real production data before you theorize.** Look at the actual rows, logs and
   traces. A story built from the code alone is a guess.
2. **Get the base rate before you call something broken.** How often does this happen
   normally? One failed request in a million is normal. A rate that jumped is not. Do not
   flag normal behavior as a failure. Compare against the same window a week ago.
3. **A query is not a verdict.** An empty result has three causes: the event never
   happened, the data is not there, or your filter is wrong. Prove the filter works on
   something you know is there, before you say "this never ran".
4. **Production is read-only.** Run `SELECT`s only. See the next section.
5. **Measure again after the last change.** A number you quoted earlier may be stale.
   Re-run the query before you report it.
6. **Never swallow errors from your own tools.** Do not add `2>/dev/null` to an
   investigation command. Check the exit code. A tool that fails quietly looks exactly
   like "no data".

## Read-only against production

This is real customer data.

- Connect with a **read-only database role**. If you only have a full-access
  credential, behave as if it were read-only: run `SELECT`, `EXPLAIN` and schema reads.
- Keep credentials in your secrets store or an untracked env file. Never paste them into
  a file you commit, a ticket or a chat.
- **Always scope by tenant** and the narrowest other keys. Never run a query that could
  cross tenants unless the question is cross-tenant.
- Add `LIMIT` and a time window to exploratory queries. Production tables are big.
- **Do not write.** If a fix or recovery truly needs a write, stop. Show the user the
  exact statement, run it first as a `SELECT count(*)` to prove which rows it touches, and
  get an explicit yes. Prefer the reversible path the app already understands (a status
  flip, an admin endpoint) over hand SQL. Run it in a transaction. Schema changes go
  through your migration workflow, never ad hoc.
- Do not copy production personal data into tests, tickets or chat. Use ids and counts.

## The loop: which signal first

1. **What, who, when: error tracking.** Start here for a user-facing error or an "is this
   widespread?" question. (Examples: PostHog, Sentry, Rollbar.) One pass should give you
   impact, first seen, release, browser or OS, a sample event with its trace id, and any
   linked session replay.
2. **Logs, traces, metrics: your observability stack.** (Examples: Grafana with
   Loki, Tempo and Prometheus; Datadog; Honeycomb.) Pull the logs for the trace id. Open
   the trace to see the spans and where time went. Use metrics for "how often, since
   when, how slow".
3. **Raw stack trace, build and deploy logs: your hosting platform.** Carry the trace id
   over. Build and deploy logs often never reach the log stack.
4. **Data state: read-only database query.** Use the entity id and tenant id from the
   event. Inspect the actual rows.
5. **An AI agent did the wrong thing: LLM traces.** (Examples: Langfuse, Helicone,
   LangSmith.) See the section below. These often have no trace id and no error event.
6. **Reproduce, fix, add a regression test.** Hand off to a reproduce-then-fix loop. Build
   a failing test, command or harness against the cause you now understand. If the
   trigger is a UI sequence, watch the session replay first.

If the symptom is backend-only and there is no error event ("the job did not send"), skip
step 1. Go straight to logs and the database. If the symptom is "the agent misbehaved",
go straight to step 5.

## Working with each signal

### Error tracking

- Work from the issue id or URL. Check impact (users, events), first and last seen, and
  what changed at the first-seen time (a release, a flag).
- Pull a sample event and copy its trace id and path. That id is your join key.
- Use the organization or tenant property on the event to learn which customer is hit.
- Router 404s and non-production noise should already be filtered at capture. If they
  are not, fix that first. They bury the signal.

### Logs and traces

- **Know where the fields live.** Many setups ship only the log *message* as the line
  body. Every structured field (trace id, tenant, user, status, duration) arrives as
  **structured metadata or labels**, not as text in the body. Then a text search for the
  trace id returns zero lines, and it reads exactly like "no such request". Filter on the
  field instead, and use a line formatter to make the result readable.
- **Prove the filter first.** If a query scans thousands of lines and returns none, the
  stream is healthy and your filter is wrong. Match something you know exists (a count
  by route, for example) before you conclude "this never ran".
- **A live tail is not a history.** Hosting-platform log commands often return only the
  newest N lines, whatever time window you ask for. A past window may come back empty
  while your log store holds the data. Use the tail for live traffic and raw stack
  traces. Use the log store for anything older.
- **Unauthenticated routes carry no tenant or user.** A sign-in request has no tenant yet,
  by construction. Filter by path, not by the join trio. The trace id is still there.
- **Absence proves nothing before logging existed.** If a code path was added or
  instrumented recently, no line from before that date is not evidence. Corroborate with
  database rows (a created `session` row *is* a successful login) and session replay.
- **Wide results overflow tool limits.** Slice JSON with a script instead of reading it
  raw.

### Database

- Public ids (the ones in URLs, logs and API responses) are directly queryable. Learn
  your id prefixes.
- Check `created_at` / `updated_at` against the incident time. Compare a good tenant to
  the broken one.
- To confirm a migration shipped, read the migration table. "Merged" is not "applied".
- Use `EXPLAIN` for slow queries. Never `EXPLAIN ANALYZE` a write.

## LLM and agent traces

Agents are built to **return tool failures to the model** so it can recover, rather than
throw. So a failed search, a provider error, a too-large filter or a wrong tool choice
often becomes a normal-looking reply. It never becomes a 5xx, so it never reaches the
error tracker or the log store. The LLM trace store is the only place it shows.

- **Different join keys.** LLM traces usually join on user id, session id and tenant,
  held in the trace metadata and tags. They often do not carry the request trace id.
  One agent step is one trace. A conversation shares a session id.
- **Read the tool observations.** Open the trace with its observations. For each tool
  call, read the *input the agent passed* and the *output it got back*. The output may
  hold an error object the agent swallowed.
- **Filter by environment.** Production and local dev often share one project. Filter on
  the environment tag so a local run does not pollute the window.
- **Check your client matches the server.** A CLI or SDK built for a newer API version
  than your self-hosted server may refuse list and get calls with a "deprecated
  operation" error, or return a 404. If it prints that error on stdout and your parser
  expects data, you see `0` and conclude "the agent never ran". Check the exit code. If
  the client cannot read traces, call the REST API directly.
- **The recorded input may not be the prompt.** Some wrappers trace only part of the
  input. A generation showing `input: null` with thousands of input tokens is not a
  broken trace. The prompt was simply not captured. Rebuild what the model saw from the
  source data instead.
- **The reasoning may not be stored.** If the model's output is only a structured verdict,
  every "rationale" field is empty by design. Do not report it as a bug. To test a rule,
  run it on a control group whose right answer you already know.

## Lessons that transfer: check these before a deep dive

- **Merged is not deployed.** Check the running version (commit sha in the app's version
  field or the platform) against the fix commit. Deploys are sometimes skipped or fail
  quietly, and a platform "redeploy" may rebuild the *last successful* build, not the
  newest commit.
- **Merged is not migrated.** A schema change in the code does not mean it ran in
  production. A missing column is a real production failure. Read the migration table.
- **An env var change may do nothing.** Some platforms apply a variable change only on the
  next real deploy. Confirm the new value is live before you test.
- **A silent engine is often a dead worker.** If scheduled jobs or workflows "just stopped"
  and no error exists, check that the worker or consumer process is up. Look for its boot
  line after the latest deploy. A bad queue or signing key, or a crash loop before
  bootstrap, gives silence, not errors. Typical signature: rows in `active` state with
  zero child rows, and a "last run" timestamp stuck null.
- **Bad gateway on a fresh deploy** usually means the app listens on the wrong port or the
  wrong interface. It must bind the port the platform routes to, on `0.0.0.0`.
- **Stale client calls and 404s after a deploy.** A frontend bakes its API base URL in at
  build time. A change needs a rebuild, not a restart. A CDN may also cache a fallback
  page for a new asset path.
- **Third-party account rotated.** If an integration shows 401s and no inbound webhooks,
  the provider may have rotated the host or key. You need new credentials, a redeploy and
  re-registered webhooks.
- **Two orgs, one customer.** One customer can own two tenants with the same display
  name. Scope by id, not name.

## Report

Answer first. Use plain language. State:

1. **What happened** and **who is affected**, in one or two sentences.
2. **The evidence**: the ids, counts, and the base rate that shows this is abnormal.
3. **What you ruled out**, and what you did not check.
4. **Next step**: a fix, a reproduction to build, or one question for the user.

Say plainly when you have NOT verified something.

## Traps

| Trap | Instead |
| --- | --- |
| Theorizing from the code | Read the real rows, logs and traces first |
| Calling a normal rate a failure | Get the base rate and compare to last week |
| Reading an empty result as "it never ran" | Prove the filter on known data |
| Text-searching for the trace id | Filter on the structured field |
| Using the live tail for an old incident | Use the log store |
| Hiding tool errors with `2>/dev/null` | Check the exit code and stderr |
| Looking in the error tracker for an agent mistake | Read the LLM trace and its tool outputs |
| Writing to production "just this once" | Preview with `SELECT`, get a yes, use the reversible path |
| Quoting an earlier number | Re-measure after the last change |
