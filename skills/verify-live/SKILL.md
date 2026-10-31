---
name: verify-live
description: Launch the app's local stack (API, web, database and cache in Docker) for the current git worktree, discover its real ports, prove the whole stack is alive, then watch the change work in a browser or with curl. "Done" means you watched it work. Use when asked to run, start or smoke-test the app locally, to "verify it live", "check it in the browser", "does it actually work", or before you say a change is finished.
---

# verify-live

"Done" means you **watched it work**. Not "it compiles". Not "the tests pass". You ran the app, did the thing, and saw the result.

This skill has two jobs. First, find the right URLs for THIS checkout and prove the stack is alive. Second, watch your change work on that stack.

## Say it plainly

At the end of every task, state one of these:

- **Verified live:** what you did (which URL, which action) and what you saw.
- **NOT verified live:** why (no browser tool, no seed data, stack would not start) and what is left for the user to check.

Never write "should work". Never let a green test suite stand in for a live check.

## Find the repo's own start commands

The repo's README or scripts own the exact commands. Look there first. Do not copy commands from this skill if the repo says otherwise. Typical shape:

```bash
docker compose up -d      # database + cache
<migrate command>         # apply migrations
<dev command>             # API + web, long-running
```

If you cannot find them, ask the user. Do not guess a start script.

## Ports are not fixed: discover them

Only the main checkout usually owns the default ports (for example `:3000` and `:5173`). Each **git worktree** should have its own ports and its own database and cache containers. If two checkouts share a port, the second one silently talks to the first one's stack. You then verify the wrong code.

So never assume default ports. Read the real ones:

```bash
grep -E '(_URL|_PORT)=' .env          # or your env file; API_URL and WEB_URL are the authority
docker compose ps                      # containers scoped to this worktree
lsof -iTCP -sTCP:LISTEN -n -P | grep -E 'node|vite'
```

Rules for per-worktree ports:

- Derive the ports from the worktree (a hash of its path or name) and write them to the env file once. Do not pick them by hand each time.
- Give each worktree its own compose project name, so containers and volumes do not collide.
- A named local URL (a local proxy or a `*.localhost` host) is fine. If it fails but the derived port works, the proxy is the problem, not the app.
- If an env change or a change in a built shared package is not picked up, restart. Watch mode does not catch those.

Write the URLs as `$API_URL` and `$WEB_URL` in every step below.

## Start it

1. Check whether it is already running (`docker compose ps`, the listening ports). Do not start a second copy.
2. Start the database and cache, migrate, then start the dev servers **in the background**. Dev servers run until stopped.
3. Wait 5 to 15 seconds for both servers.
4. If you need a login, use the repo's seed script. Do not create real accounts.

## Prove the stack is alive

Do this before you test your change. A dead dependency makes every later result meaningless.

**1. Liveness and readiness, with curl.** Use the repo's health routes. Check for an API prefix (many APIs mount routes under `/api`).

```bash
curl -sk "$API_URL/health"          # liveness: {"status":"ok"}
curl -sk "$API_URL/health/deep"     # readiness: database and cache each "up"
```

Use `-k` if the local URL uses a self-signed certificate. A readiness check that shows both the database and the cache as `up` is the real "backend healthy" signal. A bare 200 is not.

**2. Load the web app in a browser.** A 200 from the web URL only proves the dev server sent the HTML shell.

1. Open `$WEB_URL`.
2. Take a snapshot of the page (the accessibility tree).
3. Confirm it renders **live data** from the API, not an empty shell.
4. Read the console. Expect no errors or warnings.

If the web is up but data is missing, debug the API side. Do not start by changing the frontend.

## Watch your change work

Now do the thing the change is for. Be specific.

- **A UI change.** Open the changed screen. Do the action. Take a screenshot. Look at it. Check a phone width. Check loading, empty, error and populated states. Use the [`frontend-ui`](../frontend-ui/) checks.
- **An API change.** Call the real endpoint with curl against the running API. Check the status code, the body, and the data in the database. Check the error path too.
- **A background job or webhook.** Trigger it. Read the logs. Check the row it should have written.
- **A bug fix.** Reproduce the bug first, on the stack, so you know your check can fail. Then apply the fix and watch the same steps pass.

Force hard states instead of waiting for them: intercept API responses in the browser, or seed the rows. Save the logged-in browser session once and reuse it.

Record evidence in a scratch folder (screenshots, curl output). Do not commit it.

## Stop what you started

A running stack costs real memory: many processes plus containers. The rule is simple: **whoever started it for themselves stops it.**

- **You started it just to verify a change:** stop it when verification is done. Use a stop that keeps data, so a restart takes seconds.
- **The user asked to run the app, or is using it:** leave it running. Do not kill it after a commit or push. Watch mode reloads on its own.
- **Never stop a stack you did not start** without asking. It may be the user's.

Useful commands:

```bash
docker compose ps        # container health, scoped by this worktree's project name
docker compose stop      # stop, keep data
docker compose down -v   # destructive: also removes this worktree's volumes
```

Leftover processes after a session end are common. Before you finish, check for stray dev servers and stop yours.

## Traps

| Trap | Instead |
| --- | --- |
| Assuming default ports | Read the env file and `docker compose ps` |
| Two worktrees share one database | Own compose project and ports per worktree |
| A 200 from the web URL means it works | Load it in a browser and confirm live data |
| Testing the change before the stack is proven | Run the health checks first |
| Green tests, so "done" | Watch it work, or say you did not |
| Fixing a bug you never reproduced | Reproduce on the stack first |
| Leaving verification stacks running | Stop the stack you started |
| Killing the user's running app after a push | Leave it; watch mode reloads |
