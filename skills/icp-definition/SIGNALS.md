# Signals → where to find them

How to turn ICP hypotheses into things you can actually detect in public data. The skill is tool-agnostic: use whatever you have connected — a LinkedIn data MCP, Sales Navigator, Apollo, Clay, Crunchbase, job boards, `WebSearch`/`WebFetch`. The tables name the **data you need**; pick the tool that returns it.

## Two kinds of signal

- **Fit signals (static):** does this account/person match the ICP at all? Firmographics, role, seniority, geography, tech. Used to *qualify*.
- **Timing signals (dynamic):** is *now* the moment? Recent events that create need or openness. **Prioritize these.** A perfect-fit account with no timing signal is a "later"; a fit account *with* a fresh trigger is a "today".

## Reverse-engineering the best customers (step 2)

Given 2–5 best-customer company/profile URLs:

| Goal | Data to pull |
|---|---|
| Enrich a known person | Profile by URL: current role, tenure, past employers, education |
| Company firmographics | Company by domain: industry, HQ, founded, funding stage |
| Size band | Employee count (and its trend, if available) |
| Who the buyer really is | The title/seniority of the person who signed, and who else was involved |
| Find *more like these* | "Similar profiles" / lookalike search from a seed profile or company |

Look across the set for shared denominators: industry, size band, region, buyer title, company stage, tech, growth motion. Those denominators become the draft ICP.

## Common timing signals → how to detect

| Timing signal | Why it matters | Where it shows up |
|---|---|---|
| **Hiring for a role** (esp. the function you serve) | Budget + active pain in that area | Company job posts, job-board search, open-role count over time |
| **Recent job change / new role** | New leaders re-tool in their first 90 days | Profile tenure (< 90 days in role) |
| **Posting about a relevant topic/pain** | Stated intent, the warmest possible opener | Their recent posts; post search by keyword/hashtag |
| **Engaging with competitor/topic content** | In-market, comparing options | Reactions/comments on competitor or topic posts |
| **Funding / growth / expansion** | New budget, new initiatives | Funding news, headcount trend, new offices/markets |
| **Active right now** | Reply rates spike when they're online | Last-activity timestamp, if your tool exposes it |

## Fit signals → search filters

To build a repeatable target list, express fit as people/company search parameters: title/seniority, industry, headcount band, geography, keywords. Run it, eyeball 5–10 results, and tighten until the list is mostly on-target. **Record the exact filter** in the brief so it's reproducible.

### Lookalike method (preferred when you have customers)

The strongest target list isn't guessed from abstract firmographics; it's **reverse-engineered from who you already win.** With 2–5 best customers:

1. From step 2 you already have the **shared denominators** — industry, headcount band, region, buyer title/seniority. Those *are* the lookalike fingerprint.
2. Run them as a **Sales Navigator (or equivalent) search**. Map the denominators onto its filters:
   - `industry`, `location`, `function` — usually human-readable.
   - `seniority` — a fixed set (owner/partner, CXO, VP, director, …).
   - `company headcount` — fixed bands (1-10, 11-50, 51-200, …).
   - `keywords` — free text for niche descriptors the structured filters can't capture.
3. Eyeball the first page, tighten until the list is mostly on-target, then **record the exact filter set** in the brief so it can be re-run. Paginate only as needed — most tools meter per page.

Complement with per-profile lookalike tools when you want "more people like *this exact person*" rather than "more companies like this segment."

**Fallback (no usable customers yet):** build the list from first principles off the offer + 2–5 aspirational accounts, then validate the same way.

## Tribes → where to mine them (step 8)

| Tribe type | Where it shows in data |
|---|---|
| Alma mater | Education on the profile |
| Former employer ("ex-X") | Experience history |
| Region / hometown | Profile location |
| Communities / groups | Group memberships, Slack/Discord communities they post in |
| Newsletters / thought leaders followed | Followed newsletters/creators, if exposed |
| Shared investor / portfolio | Company funding data + posts |
| Conferences / events | Recent posts, event attendee lists |

For each tribe, write the *honest* opener it enables. If you can't state a true, specific commonality, drop it.

## Handling large payloads

Post and list endpoints often return payloads too big for a tool result, so they get spilled to a file. **Don't `Read` it raw** (one giant JSON line breaks offset/limit chunking). Parse only the fields you need, e.g.:

```bash
python3 -c "import json; d=json.load(open('<file>')); [print(p.get('text','')[:500]) for p in d['data']['items']]"
```

Note: a "profile posts" feed often includes **reposts**. A feed full of reshares tells you which communities they amplify (a tribe signal) but is *not* their own point of view. A thin original-content footprint is itself a finding worth flagging.

## Cost discipline

These calls are usually metered. Enrich a *handful* of high-signal profiles rather than bulk-scanning. Prefer one good lookalike search over ten blind ones. Note in the brief which signals were validated against live data vs. assumed.
