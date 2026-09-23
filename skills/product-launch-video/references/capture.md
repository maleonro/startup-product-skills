# Capturing the real material

## Pick the case from real data
Query the product's data for the strongest honest result (best rate with a meaningful base, e.g.
interested replies over invites with 40+ invites). Record the query and the numbers. Check every
descriptor you will put on screen (role, segment, "founders") against the rows, not the name of
the campaign.

## Show it without real people: a seeded copy
Export only the **structure** of the real case (graph/config, statuses, outcomes, timestamps) and
rebuild it in a local dev org with sample people, companies and texts that follow the real
template. The product's own UI then computes the real numbers itself. Keep the seed script out of
git. Never import names, message bodies or enrichment blobs.

## Screenshots
- Playwright, fixed viewport (e.g. 1440x900), **deviceScaleFactor 3**: a legible 1080 crop is
  1100-1400 source px wide, which 2x cannot give without upscaling.
- A shorter viewport (e.g. 1440x640) pulls a composer or footer up under the content when the gap
  between them is empty.
- Log in once and reuse `storageState`. Wait for data to load; check for toasts and error states.
- Crop around UI oddities instead of scrolling through them (e.g. a run view that also lists the
  untaken branch's steps in grey reads as duplicates) and tell the user: it may be a product bug.
- Look at every crop at full size before using it; clipped headers and sliver rows at the band
  edges are the most common defect.

## The site's components
If the product's marketing site already animates the product (a chat window, a workflow graph, a
proof grid, a mascot), rebuild those in the video from the site's source (CSS tokens, sprite sheets,
component structure). They are already approved brand, and they animate better than screenshots.

## Local stack gotchas seen so far
- Background workers (e.g. an Inngest dev server) may block the API from starting.
- Routes may take a typed ID (e.g. `camp_…`) rather than the DB UUID.
- Dev servers can die under memory pressure (exit 137); restart them. Stop what you started when done.
