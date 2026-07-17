# radar-de-rondas-latam

A [Claude Code](https://claude.com/claude-code) skill that runs a weekly radar of startup funding rounds across Latin America and turns them into a prospecting signal, not just news.

It is not a search prompt. It is an empirically validated data pipeline: in a six-week test window, this multi-source setup found **31 rounds** where a manual run over the single best source found only 17. The skill operates in Spanish (sources span English, Spanish and Portuguese).

## What it does

One weekly run, six steps:

1. **Discovery** — parallel fetches over a layered source pipeline, each on its own cadence: [LatamList](https://latamlist.com) funding category (weekly backbone, ~75% of volume), LatAm Tech Weekly's "Deals of the week" (weekly, catches micro-rounds), Brazilian press — Brazil Journal, NeoFeed, Finsiders (biweekly, rounds that only exist in Portuguese), and latamfintech.co's monthly top 10. Dead channels (LinkedIn search, open web search, blocked outlets) are documented so no run wastes time rediscovering them.
2. **Extraction** — every round goes into a raw CSV under strict data rules: the date of the original announcement (not the aggregator's), no M&A, no VC-fund raises, no companies headquartered outside LATAM, and no invented fields — what the source doesn't say stays empty.
3. **Consolidation** — `scripts/consolidar.py` normalizes amounts (including BRL→USD at the day's rate) and round types, dedupes both within the run and against the ledger, classifies each round's commercial signal, and appends to `data/rondas-latam.csv`, a cumulative ledger with `first_seen_date` per row plus a per-run delta file.
4. **LinkedIn enrichment** — for new expansion-stage rounds only, one targeted search per company to find the founder's own announcement post.
5. **Artifact** — regenerates an interactive explorer (React) over the full ledger, with a "this week's signals" section for the new expansion-stage companies.
6. **Report** — new rounds by source, country and sector, expansion signals for prospecting, ledger totals, failed sources, and the honesty caveats that must accompany any published figures.

## The thesis

A funding round is not news — it is a commercial signal. A company that just closed a Series A/B/C enters expansion mode: it hires, opens markets, and tries new tools, which makes it unusually receptive to sales conversations. The `signal=expansion` classification turns the ledger into a prioritized prospecting list, refreshed weekly.

## Files

- [`SKILL.md`](SKILL.md) — the six-step weekly workflow and hard rules.
- [`references/fuentes.md`](references/fuentes.md) — sources, cadences, exclusions, dead channels, and publication caveats.
- [`scripts/consolidar.py`](scripts/consolidar.py) — normalization, dedup, signal classification, ledger merge.
- [`artifact/explorador-capital-latam.jsx`](artifact/explorador-capital-latam.jsx) — the interactive explorer over the ledger.
- [`data/rondas-latam.csv`](data/rondas-latam.csv) — the cumulative ledger (never edited by hand), seeded with 240+ real rounds.

## Install

```bash
npx skills add maleonro/startup-product-skills --skill radar-de-rondas-latam
```

Or manually, by dropping the folder into your skills directory:

```bash
cp -r skills/radar-de-rondas-latam ~/.claude/skills/radar-de-rondas-latam
```

Then trigger it by asking Claude Code to run the rounds radar, update LATAM rounds, or find companies in expansion mode.

## Why it exists

Every VC newsletter tells you who raised. None of them tells you, week after week, in one deduplicated ledger, **who just entered buying mode** — and hands you the founder's announcement post to open the conversation.
