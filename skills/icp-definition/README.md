# icp-definition

A [Claude Code](https://claude.com/claude-code) skill that turns "we sell to everyone" into a sharp, evidence-backed Ideal Customer Profile. It pulls live data on your best customers first, then interviews you to fill the gaps.

It is the first step of the GTM set: **`icp-definition` → `lead-magnet` → `gtm-roadmap`**.

## What it does

1. Reverse-engineers 2-5 of your best customers from public data.
2. Finds contradictions in your positioning (headline vs. website) and makes you resolve them.
3. Scores the market on Hormozi's four traits: pain, purchasing power, easy to target, growing.
4. Drafts the company ICP and the persona ICP, anchored on the Dream Outcome.
5. Defines **fit signals** (who qualifies) and **timing signals** (why now), each mapped to a real search.
6. Builds a lookalike target list from your best customers (Sales Navigator or equivalent).
7. Finds **tribes**: true, shared identities that give an honest ice-breaker.
8. Writes a brief where every claim is tagged `[data]`, `[owner]` or `[assumption]`.

## Files

- [`SKILL.md`](SKILL.md) — the 10-step workflow and quality bar.
- [`HORMOZI.md`](HORMOZI.md) — the market and offer frameworks behind it.
- [`SIGNALS.md`](SIGNALS.md) — fit and timing signals, and where to find each in public data.
- [`TEMPLATE.md`](TEMPLATE.md) — the ICP brief deliverable.

## Install

```bash
npx skills add maleonro/startup-product-skills --skill icp-definition
```

Or install the whole GTM set at once:

```bash
npx skills add maleonro/startup-product-skills --skill icp-definition --skill lead-magnet --skill gtm-roadmap
```

## Credits

The reasoning spine is Alex Hormozi's *$100M Offers* and *$100M Leads*. The skill turns those frameworks into an agent workflow that pulls live data first and cites it.
