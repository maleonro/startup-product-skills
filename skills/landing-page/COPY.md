# The copy document

Write the whole page as a markdown document before touching code. It is what the owner, a few real users and Juan review. It is also where every claim gets checked, which is much cheaper in a doc than in a shipped page.

## Header

- **Status and date.** "Draft 1, to review with <owner> and 3 people who do <the job>. Does not touch code."
- **Who it talks to.** One reader, their current setup, their pain in their words. Say who is out of scope and where they'll be served.
- **How to read it.** Each section has a "what it's for" line (a note, never on the page), then the final text. Notes in brackets are for design or the owner.

## "Before you read: the facts that changed the message"

Open with the claims you had to correct while checking them. Kairon's draft had three:

- "2,000 data sources" was really "more than 1,700" (the provider's own page, read that day, and the service confirmed live in production).
- "A fraction of the price" only held on monthly billing; on annual billing the gap shrank. The line that holds in both cases became "less than what your tools add up to", with the table and the billing note next to it.
- "Gets better results" had no source: the product had never been measured against another tool. It was cut, and the page shows its own numbers instead.

Put these first so the reviewer knows the copy was fought for.

## One block per section

For each section of the page:

```markdown
## 3. Pain

What it's for: <the one job this block does for the reader, in one line>.

### Option A (picked by <owner> on <date>)
- **H2:** …
- **Body:** …

### Option B (dropped: <the reason, with data if there is any>)
- …
```

Keep dropped options with the reason. The next relaunch starts from them.

For the hero, spell out every string: H1 lines, sub lines, the price line under the CTA, the trust line, the input label, the CTA, any secondary link, and the mascot's sign if there is one. Note the risk of the chosen option and a variant to test with real users.

## SEO block

- `<title>` per language, with its character count (fit the search result), and the meta description.
- A search-volume table per market (tool, date read, monthly average over 12 months). Write one line on what it means: which phrases have demand, which are zero. Kairon's reading: "stack" is almost never searched in any market; in Spanish the only phrase with volume was "mcp claude".

## Adversarial pass

Read everything as the most skeptical real buyer (Kairon: "someone in growth who pays for Clay + HeyReach today and distrusts AI"). Log each change:

| Before | Problem | After |
|---|---|---|
| "gets better results" | No source. Never measured against another tool. | Cut. Our numbers, with method. |
| "replaces Clay" | A heavy Clay user disproves it in a minute. | An FAQ saying which use it covers and which not yet. |
| "hyper-personalized messages" | Worn-out word, says nothing about what it reads. | "With what it read on their profile, their posts and their company", plus a real message. |

## Anti-slop checklist, line by line

| Rule | Result |
|---|---|
| No em dashes | … |
| No emoji | … |
| No "it's not X, it's Y" / "X, not Y" | … |
| No rule of three by reflex (lists of exactly three) | … |
| No epigram closing every block | … |
| No rhetorical questions (outside a real FAQ) | … |
| Banned words (easy, simple, fast, seamless, unlock, empower, frictionless…) | … |
| Sentences over 20 words | Allowed only where the nuance needs it; list them |
| Every number has a source | See the claims table |
| No repeated skeleton across sections | Hero, pain and solutions open differently |

Fill the "Result" column honestly. An exception is fine when it says why.

## Claims and sources table

| Claim | Source |
|---|---|
| Competitor X costs $N/month | their pricing page, read <date> |
| Our plan costs $N | `path/to/billing.ts:29` |
| N% acceptance with a warm-up touch | prod, checked by hand on <date> (numerator and denominator) |

A number that can't be reproduced is replaced, even if it was already published. Kairon replaced a published "40–66% vs 23%" and an "18%" that did not hold with figures re-read from production and verified by hand the same day.

## Open items for the owner

A numbered list. Strike through each one when it's decided, with the date and the decision. Typical items: pick the hero, pick the pain, ask N customers for testimonials (with the exact question and permission for name and logo), whether to name competitors, re-check the headline number once more right before publishing.
