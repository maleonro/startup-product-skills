# gtm-roadmap

A [Claude Code](https://claude.com/claude-code) skill that turns an ICP brief and a lead magnet into a sequenced outreach plan: which campaigns to switch on, in what order, and what each one says.

Third step of the GTM set: **`icp-definition` → `lead-magnet` → `gtm-roadmap`**.

## What it does

It orders campaigns by **warmth, warmest first**, because warm leads reply faster and more often:

1. **Existing network** — people who already know you. Warm A-C-A message (acknowledge, compliment, ask). Human-approved.
2. **Schedule / event** — people where you will be. "I'll be in <city> for <event>, coffee?" Human-approved.
3. **ICP × tribes** — strangers who share a tribe with you. One campaign per tribe, run in parallel. The winner becomes the default message.
4. **Always-on signals** — strangers with a live timing signal. The signal is the honest reason to reach out. Automated with guardrails; every reply goes to a human.

Autonomy grows as leads get colder. The lead magnet is the value in every wave. The plan always names a first move for this week.

## Files

- [`SKILL.md`](SKILL.md) — the warmth ladder, workflow and quality bar.
- [`WAVES.md`](WAVES.md) — the full spec per wave: audience, list, message, magnet role, channel, cadence, autonomy, metric.
- [`HORMOZI-OUTREACH.md`](HORMOZI-OUTREACH.md) — the Core Four, warm and cold outreach, Rule of 100, More-Better-New.
- [`TEMPLATE.md`](TEMPLATE.md) — the roadmap deliverable.

## Install

```bash
npx skills add maleonro/startup-product-skills --skill gtm-roadmap
```

Or install the whole GTM set at once:

```bash
npx skills add maleonro/startup-product-skills --skill icp-definition --skill lead-magnet --skill gtm-roadmap
```

## Credits

The reasoning spine is Alex Hormozi's *$100M Offers* and *$100M Leads*. The skill turns those frameworks into an agent workflow that pulls live data first and cites it.
