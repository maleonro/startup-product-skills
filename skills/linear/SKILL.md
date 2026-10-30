---
name: linear
description: Work with Linear over its MCP. Create issues with context pulled from the current session and codebase, triage and edit existing issues, and solve an issue end to end (pull, claim, branch, fix, comment back, move state, open the PR). Use when the user references a Linear issue (an ID like "ABC-123" or a linear.app URL), says "create a Linear issue", "log this as a ticket", "fix this issue", "work on this ticket", "what's assigned to me", "update the issue", or wants work tracked in Linear.
---

# linear

Linear is the source of truth for tasks and bugs. This skill owns the Linear mechanics. The fix itself follows your normal debugging and testing flow.

The skill uses the Linear MCP tools (for example `get_issue`, `save_issue`, `list_issues`, `save_comment`, `list_comments`). If the tools are not connected, say so and ask the user to connect the Linear MCP. Do not pretend an issue was created.

## Workspace facts: look them up once

Do not guess these. Read them at the start of the session, then reuse them.

- **Team:** `<your-team>`. Pass it when you create an issue. If there is more than one team, ask which one.
- **States:** list them with the MCP (`list_issue_statuses`). A common flow is `Backlog` → `Todo` → `In Progress` → `In Review` → `Done`, plus `Canceled` and `Duplicate`.
- **Labels:** list them (`list_issue_labels`). Common ones: `Bug`, `Improvement`, `Feature`.
- **Priority:** `1` Urgent, `2` High, `3` Medium, `4` Low, `0` None.
- **Identifiers** look like `<TEAM>-123`.
- **Markdown fields take literal newlines.** Never send escape sequences like `\n`.

## Workflow A: create an issue

Pull the body from the current conversation and codebase. Do not make the user retype it.

1. Decide the label and priority from context. Ask only if it is truly unclear.
2. Draft a tight title and a Markdown body with the template below.
3. Call `save_issue` with `team`, `title`, `description`, `labels` and `priority`. The default state is `Backlog`. Use `Todo` only if the user wants it actionable now.
4. Return the new identifier and its URL.

To split a plan into **many** vertical-slice issues, order them by dependency and make each one shippable alone. Create the parent first, then link the others with `parentId`, `blockedBy` or `blocks`.

A good issue:

- The title says the outcome or the symptom, not the file. "Export fails for lists over 10k rows", not "Fix export.ts".
- The body is decision-rich. Link, quote and reference. Do not paste a log dump.
- A bug has repro steps and the observed versus expected result.
- Acceptance criteria are checkable.
- Check for a duplicate first (`list_issues` with `query`). Link it instead of filing a copy.

<issue-template>
## What and why

One or two sentences: the behavior wanted, or the bug observed, and why it matters.

## Context

Repro steps (for bugs). Relevant `file_path:line`. Trace IDs, error links, screenshots. Related issues.

## Acceptance criteria

- [ ] Criterion 1
- [ ] Criterion 2
</issue-template>

## Workflow B: edit or triage an issue

Call `get_issue` first to read the current state. Then call `save_issue` with the `id`.

Common moves:

- Set `state`, `priority`, `labels`.
- Set `assignee` (`"me"` for yourself).
- Add `links`.
- Set `blockedBy`, `blocks` or `parentId`. Relations are append-only. Use the `remove…` fields to detach.
- Use `save_comment` to record a decision or a status note. Do not rewrite the description to do it. A rewrite erases the history.

When you triage a pile of issues, change one thing at a time and report what you changed. Do not close or cancel an issue the user did not ask you to close.

## Workflow C: solve an issue end to end

1. **Pull.** Call `get_issue <id>` with relations. Read the description. Then call `list_comments` for prior discussion. If the user gave a `linear.app` URL, the identifier is in it. Check for attached images or linked PRs.
2. **Claim.** Call `save_issue` to set `assignee: "me"` and `state: "In Progress"`.
3. **Branch.** Work on a branch whose name carries the identifier (Linear can link it to the issue). Use a separate git worktree if other work is open.
4. **Fix.** Pick the route by type:
   - **A bug.** Reproduce it first. Fix it. Add a regression test that fails without the fix.
   - **A production error** (it has a trace ID or an error-tracker link). Read the real logs and data before you theorize.
   - **A feature or a larger scope.** Write the plan in 2 or 3 sentences and get a yes before you build.
5. **Verify.** Watch it work on the running app. See [`verify-live`](../verify-live/). Say plainly if you did not.
6. **Comment back.** Call `save_comment` with one paragraph: the root cause and the fix. For a bug, state the hypothesis that proved right. Linear then carries the post-mortem.
7. **PR and state.** Open the PR. Put the identifier in its description so Linear links it. Then call `save_issue` to set `state: "In Review"`. Leave the move to `Done` to the merge or to automation, unless the user says otherwise.

If the issue is unclear, comment with ONE question and stop. Do not guess at a spec.

## Finding work

- "What is assigned to me" or "what should I work on": `list_issues` with `assignee: "me"` and `state: "Todo"` or `"In Progress"`. Order by priority.
- Search by text: `list_issues` with `query`. Filter by `label`, `state` and `priority` as needed.
- Before you start something, check whether someone already has it (`assignee`, `In Progress`).

## Traps

| Trap | Instead |
| --- | --- |
| Guessing state or label names | Read them from the MCP once |
| Filing a duplicate | Search first and link |
| A title that names a file | Name the outcome or the symptom |
| Rewriting a description to log progress | Add a comment |
| Moving an issue to `Done` yourself | Move to `In Review`; merge closes it |
| Fixing a bug you never reproduced | Reproduce, then fix, then add a test |
| Guessing at an unclear spec | Ask one question in a comment |
| Reporting "created" when the MCP call failed | Check the result and say so |
