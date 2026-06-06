# Parallel-agent workflows

Use the `Workflow` tool once the plan is approved. Four patterns recur. Scale agent count to the work (small change: 3 agents; large feature or full-app sweep: 10).

The non-negotiable rule for any build/edit workflow: **agents are ownership-disjoint** — no two agents ever touch the same file. Partition the work by file-group up front. This is what lets them run in parallel without conflicts and without `isolation: 'worktree'`.

## 1. Build (phased, ownership-disjoint)

The implementation workflow. Phases run in order; only the builders fan out in parallel. Always end with a verify phase that runs the full type check + lint and fixes integration gaps.

```
export const meta = {
  name: 'feature-backend',
  description: 'Build <feature> per the design doc, N agents, ownership-disjoint',
  phases: [
    { title: 'Contracts',  detail: 'schemas + types + interfaces (1 agent, everyone depends on this)' },
    { title: 'Builders',   detail: 'the disjoint units, parallel' },
    { title: 'Engine',     detail: 'composer / orchestration that wires the builders' },
    { title: 'API',        detail: 'controller/routes/service/DI wiring' },
    { title: 'Verify',     detail: 'full tsc + biome, fix integration gaps' },
  ],
}
phase('Contracts')
await agent('Write the shared schemas, types and the builder interface for <feature>. Files: <list>.')
phase('Builders')
await parallel(UNITS.map(u => () =>
  agent(`Implement ${u.name}. ONLY touch ${u.files}. Conform to the contracts from phase 1.`, { phase: 'Builders' })))
phase('Engine');  await agent('Implement the composer/repo that combines the builders. Files: <list>.')
phase('API');     await agent('Wire controller/routes/service + DI registration. Files: <list>.')
phase('Verify');  await agent('Run tsc + biome across the changed files, fix any integration gaps. Report the passing output.')
```

## 2. Functional review (fan-out by domain, then synthesize)

For "review the app and find improvements". One agent per domain, each reads code and reports findings; a final agent merges, dedupes and prioritizes into a roadmap doc.

```
phases: [{ title: 'Review' }, { title: 'Synthesize' }]
const findings = await parallel(DOMAINS.map(d => () =>
  agent(`Review the ${d} domain. Read the code, find functional/UX/error-handling gaps. Cite file:line.`,
        { phase: 'Review', schema: FINDINGS_SCHEMA })))
await agent(`Merge, dedupe and prioritize these into a roadmap: ${JSON.stringify(findings)}`, { phase: 'Synthesize' })
```

## 3. Adversarial verify (trust nothing unverified)

Run this on the output of pattern 2 before acting on it, and as the final functional PR review. A fresh wave of senior agents opens the cited code and confirms or refutes each finding; the doc is rewritten keeping **only what holds firm**.

```
phases: [{ title: 'Verify' }, { title: 'Rewrite' }]
const verdicts = await parallel(FINDINGS.map(f => () =>
  agent(`Open the cited code for "${f.title}" (${f.file}). Confirm or REFUTE against the real code. Default to refuted if uncertain.`,
        { phase: 'Verify', schema: VERDICT_SCHEMA })))
const survivors = FINDINGS.filter((_, i) => verdicts[i]?.confirmed)
await agent(`Rewrite the doc with only these confirmed items, tightened and focused: ${JSON.stringify(survivors)}`, { phase: 'Rewrite' })
```

## 4. Remediation (one phase, disjoint file-groups)

For applying a batch of fixes (e.g. add error/empty/success states across many components). Single phase, N agents, each owns a disjoint group of files.

```
phases: [{ title: 'Implement', detail: 'N agents, disjoint files' }]
await parallel(FILE_GROUPS.map(g => () =>
  agent(`Apply <change> to ONLY these files: ${g.files}. Follow the existing patterns in each.`, { phase: 'Implement' })))
```

## Sequencing across turns

These are single-phase fan-outs you chain by reading each result before launching the next: build (1) → run locally → review (2) → adversarial verify (3) → remediate (4) → verify again. Stay in the loop between workflows; don't try to encode the whole feature in one mega-script.
