# Analytics, deploy, share (steps 6, 8, 10)

## The funnel

Send a small set of named events from the first public build. The first game's, translated:

| Event | Properties | Answers |
|---|---|---|
| pageview | (sent by hand, first) | how many opened the link |
| portrait_seen | | how many phones opened upright |
| started | | how many pressed start |
| room | room, floor | how far they got |
| lost | room, cause, attempt | where and why they lose |
| minigame | id, ok, attempt, seconds | which idea they did not get |
| finished | rank, seconds, retries, alerts | who finished, and how |
| share, download, cta | | what they did at the end |

Also send **time played**. The first game did not, so it could not be compared with the 3-minute bar.

- Turn analytics on only on the production host. `?analytics=1` forces it on for a local check,
  `?analytics=0` turns it off.
- Load the analytics library lazily and queue events until it is ready. Send the pageview by hand
  before the queue: a fast player's "started" otherwise lands first and the ordered funnel drops
  them.
- No autocapture, session replay, surveys or chat widgets over the game.
- An ad blocker must not stop the game: the analytics is best effort.
- **Unit-test the event mapping.** Some analytics libraries (posthog-js does) drop events from an
  automated browser, so a bot run will never show up in the dashboard. The live proof is a real
  device, filtered by host.
- **Agents never open the live game:** every visit counts. `curl` is fine for checking tags, because
  it runs no JavaScript.

Read it with base rates. The first game's first week: 12 people opened it, 7 started, 1 finished;
6 phones, all upright.

## Deploy

- A static host with direct upload is enough (Cloudflare Pages on the first game). One script:
  build, then `scripts/check-dist.mjs`, then upload.
- **The owner runs the deploy and the DNS change.** Hand them the exact command. Agents in an
  auto-approve mode are blocked from public deploys and DNS anyway.
- **Deploy from the main branch.** If the owner deploys a branch, merge it the same day: the next
  deploy from main brings the old version back.
- After each deploy, `curl` the page and check the new bundle name and the share tags are served.
- A leaderboard needs a server bit: a small function and a key-value store (Cloudflare Pages
  Functions and KV on the first game).

## The share card (Open Graph)

The link preview is the first thing most players see.

- 1200x630. The game's name big, the hook in its own font, and a real scene from the game on one
  side. Leave the bottom-left corner free: X lays the title over it.
- `og:title` adds what the image does not say, such as "free in the browser". Set `og:description`,
  `og:image` (absolute URL), `og:image:width/height` and `twitter:card` = `summary_large_image`.
- **Give the image a new file name on every change** (`og-v2.jpg`). Caches key on the URL.
- **Do not fetch a new asset's URL before it is deployed.** A CDN can cache the not-found
  fallback for hours under that URL.
- **X caches a card per URL.** A link with a new query string (`?utm_source=x&utm_medium=thread`)
  gets a fresh card, and it also tags the traffic.
- Check what the crawler gets: `curl -A "Twitterbot/1.0" <url>` and read the tags.

## The result to share

- **A result grid, like Wordle's:** one colored square per room ("no alerts", "an alert", "a
  retry"), with a one-line legend. It shows how you did without spoiling the game.
- **A rank that says its place** ("6 of 7; the best is ...") and a downloadable card (1200x675 PNG)
  with the score and the link.
- A top 3 with three letters, if the game has a score worth beating.

## The launch post

The first game's launch thread, in order: the hook and the trailer; how it was built and what it
cost (1,444 M tokens, about US$620 at API prices; 97% of the tokens were context read again); what you do in the
game; one lesson from the theory that changed the game; what we would do differently; the link,
with a UTM, in the last post (posts with links get less reach).

## Read it again (step 10)

48 hours after each push of traffic: arrivals by source, started, past room 3, finished, time
played, phones upright. Compare with the base rate before calling anything a change. The next PRD
starts from these numbers.
