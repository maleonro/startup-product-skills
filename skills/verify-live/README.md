# verify-live

A [Claude Code](https://claude.com/claude-code) skill that makes "done" mean *you watched it work*. It starts your local stack for the current git worktree, proves the whole stack is alive, then checks your change in a browser or with curl.

Most AI work ends at "it compiles and the tests pass". This skill ends at "I opened it and saw it work", or an honest "I did not verify this live, and here is why".

## What it does

1. **Finds the real URLs.** Each worktree gets its own ports and containers. The skill reads them from the env file and Docker. It never assumes defaults.
2. **Starts the stack.** Database and cache in Docker, migrations, then the dev servers in the background.
3. **Proves it is alive.** Liveness and deep readiness checks with curl. Then the web app in a real browser, showing live data and a clean console.
4. **Watches the change work.** UI: screenshots, phone width, all four states. API: curl the real endpoint and check the data. Bug: reproduce first, then watch the fix.
5. **Says plainly what it did not verify.** Every task ends with "Verified live" or "NOT verified live", with the reason.
6. **Stops what it started.** And leaves alone what the user is running.

## Files

- [`SKILL.md`](SKILL.md): the start, prove, watch and stop loop, with traps.

## Install

```bash
npx skills add maleonro/startup-product-skills --skill verify-live
```

Or manually, by dropping the folder into your skills directory:

```bash
cp -r skills/verify-live ~/.claude/skills/verify-live
# or per-project:
cp -r skills/verify-live /path/to/repo/.claude/skills/verify-live
```

## Use

Ask Claude Code to "run the app", "verify it live", or "check it in the browser". It also fits at the end of any feature or fix.

You need:

- **Docker** for the database and cache.
- **A browser tool** (a Chrome MCP or Playwright) for the web check. Without one, the skill says so and falls back to curl.
- **Start commands in your repo's README or scripts.** The skill reads them. It does not invent them.

Pairs with [`frontend-ui`](../frontend-ui/) and [`build-feature`](../build-feature/).

## Why it exists

Two worktrees sharing a port make you verify the wrong code. A 200 from the dev server hides a dead database. A fix you never reproduced proves nothing. This skill closes those gaps and keeps the report honest.
