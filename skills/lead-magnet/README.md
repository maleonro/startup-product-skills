# lead-magnet

A [Claude Code](https://claude.com/claude-code) skill that turns your core offer into a lead magnet: a complete solution to one narrow problem, given before any ask.

It defaults to the highest-converting kind: a **personalized, done-for-you artifact built from the prospect's own public data**. You design it as an engine an agent runs once per prospect. Example: if you sell lead generation, the magnet is not an ebook. It is a report with 10 qualified leads for that prospect, each with a ready-to-send first line.

Second step of the GTM set: **`icp-definition` → `lead-magnet` → `gtm-roadmap`**.

## What it does

1. Picks one narrow, urgent problem from the ICP that sits next to your core offer.
2. Hunts the personalization angle first: what can we find or compute about this exact prospect?
3. Generates 3-5 candidates and scores them (personalized, zero effort, reveals the next problem, ICP-aligned, cheap to scale).
4. Designs the winner as an engine: public inputs, transformation, accuracy checks, cost per prospect.
5. Maps the bridge: problem solved, next problem revealed, core offer, CTA.
6. Shows one worked example on a real prospect, then plans production and distribution.

## Files

- [`SKILL.md`](SKILL.md) — the 8-step workflow and quality bar.
- [`HORMOZI-LEADMAGNETS.md`](HORMOZI-LEADMAGNETS.md) — Hormozi's 7 steps, types, formats and scoring.
- [`PERSONALIZED-MAGNETS.md`](PERSONALIZED-MAGNETS.md) — how to invent a personalized magnet for any offer, and where to mine public data.
- [`TEMPLATE.md`](TEMPLATE.md) — the lead magnet spec deliverable.

## Install

```bash
npx skills add maleonro/startup-product-skills --skill lead-magnet
```

Or install the whole GTM set at once:

```bash
npx skills add maleonro/startup-product-skills --skill icp-definition --skill lead-magnet --skill gtm-roadmap
```

## Credits

The reasoning spine is Alex Hormozi's *$100M Offers* and *$100M Leads*. The skill turns those frameworks into an agent workflow that pulls live data first and cites it.
