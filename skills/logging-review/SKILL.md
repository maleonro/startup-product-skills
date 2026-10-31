---
name: logging-review
description: Audit the backend changes about to be pushed against a logging standard, then apply the fixes. Every meaningful decision and branch is logged, no catch is silent, and every line carries a trace id, a tenant id and a subject id. Use before pushing a change to a backend code path, when asked to "review the logging", "audit the logs", "is this debuggable in prod?", or "add logging to this". Works well as a pre-push gate.
---

# logging-review

Keep your backend logs in step with the code paths they must explain.

You observe a backend through its logs. When a request misbehaves in production, you join
error tracking, logs and database rows on one trace id. A code path that ships
under-logged is invisible. There is nothing to join on, and no record of which branch it
took or why.

This skill is **diagnose, propose, apply**. It reads the diff about to be pushed, audits
it against the standard, and edits the code to close the gaps.

The standard lives in [`references/logging-conventions.md`](references/logging-conventions.md),
next to this file. If your repo has its own logging guide, read that first. Where the two
differ, the repo guide wins.

## Process

1. **Get the diff about to be pushed.** Use the upstream branch if one is set. Otherwise
   use the default branch.

   ```sh
   range=$(git rev-parse --abbrev-ref --symbolic-full-name '@{u}' 2>/dev/null) \
     && range="${range}...HEAD" || range="origin/main...HEAD"
   git diff --stat "$range"
   git diff "$range" -- '<your-backend-source-dir>/**'
   ```

   Read the diff for **code paths**: HTTP routes, queue processors, workflow handlers,
   scheduled jobs, and services with branches. Skip types, fixtures and test-only
   changes. They carry no runtime logging.

2. **Read the standard.** Read `references/logging-conventions.md`. The checklist below is
   the audit derived from it.

3. **Audit each changed code path against the checklist.** For every new or changed unit
   of work in the diff:

   - **(a) Context is open and the subject is set.** Every unit of work (route, job,
     workflow handler) opens a logging context and sets its subject. Path and query
     params can be picked up automatically. Anything else needs an explicit call: an id
     from the body, or one minted after a create. No subject means no subject id on the
     line.
   - **(b) Every meaningful decision logs.** Each branch, early return, skip, dedupe, cap
     and no-op emits a line that says which way it went and why. The silent
     `if (!x) return;` is the classic miss.
   - **(c) Loops log per-item outcome.** A loop over entities logs the outcome of each
     item. For large batches, log one aggregate line plus one line per failure. "Processed
     0 of 50, and here is why each was skipped" must be reconstructable.
   - **(d) No silent catch.** Every `catch` either rethrows or logs at `warn` or `error`
     with context. A swallowed error is the worst case. The failure happened and left no
     trace.
   - **(e) The level is right.** `error` means the code threw. `warn` means an adverse
     *business* outcome the code handled (skipped, rejected, capped, nothing to do).
     `info` means normal progress. Do not log handled business outcomes at `error`. Do
     not bury thrown exceptions at `info`.
   - **(f) No PII in logs.** Decision logs carry only ids, counts and enums. Never an
     email, a name, a message body, content, a token, or a raw entity or request object
     splatted into the line. To identify a record, log its id.
   - **(g) The trace id, tenant id and subject id will be present.** A log mixin or
     middleware usually attaches them, but only if the context is open and the subject is
     set on *this* path (see (a)). Confirm the path you audit really sets them. Do not
     assume the middleware saves a path that never set a subject.

4. **Output: report, then apply.** List each finding as `file:line`, with what is missing
   and the fix. Then **apply the fixes**. This skill edits code. It does not only advise.
   Keep edits to logging: open the context, add the decision line, wrap the silent catch,
   drop the PII field, set the missing subject. Match the surrounding logging style and
   the level vocabulary of the standard.

5. **Hand back.** Say which paths you instrumented and why. Say which paths you reviewed
   and left alone. Then tell the user the change is ready to push.

## Notes

- "Logging already meets the standard" is a valid, common outcome. Do not add noise lines
  to satisfy a gate. A log that fires on every request and says nothing is worse than no
  log, because it drowns the lines that matter.
- Changing a backend path and adding **zero** log lines is the smell this skill hunts.
  It is a prompt to look, not proof of a defect. Pure refactors and trivial getters can
  stay silent.
- A new logging helper, observer or wrapper is almost never the fix. Call the logger you
  already have.
- Web-only, docs-only and config-only changes never need this skill.
- This skill works well as a pre-push gate: have the hook detect backend changes and
  point here. A gate cannot judge whether the logs are *good*. It can only make sure the
  review happened. If the gate cannot compute the diff, let the push through.

## Traps

| Trap | Instead |
| --- | --- |
| Adding one log line "to satisfy the check" | Log the decisions that change the outcome. Skip the rest |
| Logging the whole object so nothing is missed | Log the one field you need. Never a raw entity, request or body |
| Logging a handled business failure at `error` | Use `warn`. Keep `error` for thrown exceptions |
| Trusting the middleware to attach the subject | Check that this path sets it |
| Reviewing only the happy path | Read every early return and every `catch` |
