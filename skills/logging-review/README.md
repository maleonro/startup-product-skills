# logging-review

A [Claude Code](https://claude.com/claude-code) skill that audits the backend change you are about to push against a logging standard, then fixes the gaps.

When production breaks, you debug from the logs. A code path that ships without logs is invisible: nothing to join on, and no record of which branch it took. This skill makes sure each path you change can explain itself.

## What it does

1. **Gets the diff about to be pushed** and reads it for code paths: routes, jobs, workflow handlers, services with branches.
2. **Audits each path** against a seven-point checklist:
   - the log context is open and the subject is set;
   - every meaningful decision logs (no silent `if (!x) return;`);
   - loops log per-item outcome;
   - no silent `catch`;
   - the level is right (`error` for thrown, `warn` for handled adverse outcomes, `info` for progress);
   - no PII in log lines;
   - the trace id, tenant id and subject id will really be on every line.
3. **Applies the fixes.** It edits the code. It does not only advise.
4. **Hands back** which paths it instrumented and which it left alone.

"The logging already meets the standard" is a valid result. The skill does not add noise lines to please a check.

## The standard

A team-adoptable standard is in [`references/logging-conventions.md`](references/logging-conventions.md):

- **Three layers**: a summary line per unit of work, event lines at each decision, debug detail off by default.
- **Four mandates**: log every decision, no silent branch, no silent catch, loops log per item.
- **A correlation trio** on every line: trace id, tenant id, subject id. Attached automatically, so no one threads them by hand.
- **Three level buckets** and a strict no-PII rule.

## Files

- [`SKILL.md`](SKILL.md): the audit process and checklist.
- [`references/logging-conventions.md`](references/logging-conventions.md): the logging standard the audit applies.

## Install

```bash
npx skills add maleonro/startup-product-skills --skill logging-review
```

Or manually, by dropping the folder into your skills directory:

```bash
cp -r skills/logging-review ~/.claude/skills/logging-review
# or per-project:
cp -r skills/logging-review /path/to/repo/.claude/skills/logging-review
```

In `SKILL.md`, replace `<your-backend-source-dir>` in the diff command with your backend source folder.

## Use

Before you push a change to a backend code path, ask Claude Code to `logging-review`. Or ask "is this debuggable in prod?".

It works well as a **pre-push gate**: a hook detects backend changes and points to the skill.

Pairs with [`debug-prod`](../debug-prod/), which joins signals on the trace id this standard puts on every line.

## Why it exists

You can only debug what you can see. The trace id, tenant id and subject id on every line turn a pile of log text into a story you can follow across requests, jobs and workflows.
