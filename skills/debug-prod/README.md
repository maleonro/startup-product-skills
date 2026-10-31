# debug-prod

A [Claude Code](https://claude.com/claude-code) skill that investigates production errors by joining every signal on one trace id.

Most production debugging goes wrong early: someone theorizes from the code, reads an empty query as "it never ran", or flags a normal rate as an outage. This skill enforces the habits that prevent it.

## What it does

1. **Starts with the right signal**:
   - error tracking for what, who and when;
   - logs, traces and metrics for the story of one request;
   - the hosting platform for raw stack traces and deploy logs;
   - a read-only database query for data state;
   - LLM traces when an AI agent misbehaved.
2. **Joins them on the trace id**, so one bug report becomes a chain of evidence.
3. **Keeps the discipline**:
   - read real data before you theorize;
   - get the base rate before you call something broken;
   - prove a filter works before you trust an empty result;
   - stay read-only against production;
   - re-measure after the last change.
4. **Checks the classic causes first**: merged but not deployed, merged but not migrated, an env var that did nothing, a dead worker, a rotated third-party key.
5. **Reports answer first**, then hands off to a reproduce-then-fix loop.

Tools are examples of a category, not requirements: PostHog or Sentry for error tracking, Grafana, Loki, Tempo or Datadog for logs and traces, Langfuse for LLM traces. Use what your stack has.

## Files

- [`SKILL.md`](SKILL.md): the rules, the signal loop, per-signal pitfalls, LLM-trace pitfalls and the lessons that transfer.

## Install

```bash
npx skills add maleonro/startup-product-skills --skill debug-prod
```

Or manually, by dropping the folder into your skills directory:

```bash
cp -r skills/debug-prod ~/.claude/skills/debug-prod
# or per-project:
cp -r skills/debug-prod /path/to/repo/.claude/skills/debug-prod
```

## Use

Ask Claude Code to debug a production error. Paste an error-tracker URL, a trace id, or just describe the symptom ("the nightly job did not run").

You need:

- **Read access** to the signals you have: error tracker, logs, database (a read-only role), LLM traces.
- **A trace id on every log line and error response.** If you do not have one yet, [`logging-review`](../logging-review/) sets up the standard.

Pairs with a reproduce-then-fix loop for the fix, and with [`testing`](../testing/) for the regression test.

## Why it exists

Production data answers questions that code reading cannot. But only if you ask the right question, with a filter you have proven, against a baseline you have measured.
