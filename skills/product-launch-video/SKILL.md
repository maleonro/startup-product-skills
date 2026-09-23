---
name: product-launch-video
description: Builds a launch-grade product video (15-45 s) with Remotion for any product (SaaS, AI agent, dev tool, app): the kind a YC company posts on X, LinkedIn or Product Hunt on launch day. Rebuilds the product's key screens as animated components cut to music, from real screenshots, real data and the product's own site and brand, and never misrepresents what the product does. Runs a design-judge loop and measures motion and loudness. Use when the user wants a launch video, demo clip, feature announcement, promo, animated walkthrough, or to turn screenshots or a recording into a video, even without mentioning Remotion. Product specifics live in references/products/<product>.md.
---

# Product launch video

A launch video has one job: make the viewer feel, in the first 3 seconds and without sound, that
this product does something they want, and prove it with the real product. Two lessons shape this
skill:

- **A tidy walkthrough is not a launch video.** Panning over real screenshots in silence scored
  4/10 against the YC bar, even with perfect craft. What moved it to 8/10: music on a beat grid,
  the product visibly *doing* things (typing, streaming, counting, state changes), one recurring
  visual device, and a hook legible in one glance. See `references/craft.md`.
- **Honesty is not optional.** Every number, label and state shown must be one the real product
  produces. Rebuilt UI is fine; invented capability is not.

Before step 1, read:
- `references/products/<product>.md` if it exists (brand, claims, where the real UI lives,
  decisions already taken). If it does not, create it as you go from the template at the end of
  `references/products/README.md`.
- `references/craft.md`: the measured rules for hooks, motion, type, sound, camera and loops.

Read at the step that needs them: `references/capture.md` (step 3), `references/review-loop.md`
(steps 4 and 7), `references/remotion.md` (step 6).

## Honesty rules
1. Show only what is live in production. Anything else is labeled "coming soon", or cut.
2. Labels, buttons and product copy come from the real product or its own site.
3. Data values (names, companies, message texts) may be sample data of the kind the product shows;
   prefer seeded demo data over blurring real people. Numbers used as claims must be real and
   traceable (a DB query, the user, the published site), and are shown with their base.
4. **Rebuilt UI** (animated React components) may only show states the real product shows. Build
   each from a real screenshot or the product's own site component, and name that source.
5. A real wait is never hidden: speed-ups carry a "sped up Nx" label; a cut that skips a long wait
   carries a label or a visible clock.
6. No personal data of real people. Never name a customer without written consent.
7. A third party's UI (Claude, ChatGPT, Slack, LinkedIn…) appears as a real recording, or rebuilt
   only if the product's own site already depicts it that way and the user approves.
8. **Truth-check every on-screen sentence against the source data before delivery.** Examples of
   what this caught: "36 founders" when 6 of the 36 were not founders; "warms them up before it
   writes" when the first step already wrote a note.

If a request breaks these, say so in one sentence and offer the honest alternative.

## Workflow
Copy this checklist into your response and check items off:
```
- [ ] 1. Intake: product profile read, bar and channel set
- [ ] 2. Research the bar and the brand (site + manual), if not already in the profile
- [ ] 3. Real material captured; the case and its numbers verified from source
- [ ] 4. Plan reviewed by the design judge; user approved the concept and open decisions
- [ ] 5. Storyboard validated (scripts/validate.py for screenshot scenes; copy rules for all)
- [ ] 6. Built; type-checks; fonts load; sound wired
- [ ] 7. Judge loop to 8/10; motion and loudness measured; truth check done
- [ ] 8. Delivered with what was and was not verified; subjective picks offered as A/B
```

### 1. Intake
Fill everything you can from the conversation and the product profile. Then ask only what is
missing, one question at a time, each with a proposed default:
- The bar: "tidy product explainer" or "launch-grade" (default: launch-grade; see craft.md).
- The one thing to remember, and who it is for (the ICP in their own words).
- Channel and formats: 1x1 master for X and LinkedIn (watched on phones), 16x9 for Product Hunt /
  YouTube / web; 9x16 only for Reels, Shorts, TikTok.
- Length: 30-36 s default.
- Sound: music + SFX default. Voiceover only if a person will record it.
- The exact CTA, price wording and URL.

### 2. Research the bar and the brand
- **The brand has two sources: the manual and the live site.** Read both. A site built later is
  often bolder than the manual (it was here: dark canvas, serif headlines, mascot, an animated
  host window) and the user may call the site "more spectacular". Ask which governs marketing
  surfaces; if the site wins, update the manual first (a separate agent can rebuild it with a
  changelog), then design from it.
- **The bar:** if the profile has no research on launch videos, measure 10-20 recent ones in the
  category with `scripts/motion.py` and look at their first 4 s. The findings in `craft.md` come
  from 20 such videos (2025-26).

### 3. Capture the real material
See `references/capture.md`: seeded copy of a real case, 3x device scale, crops that avoid UI
oddities, and the real site components to rebuild from. Pick the case from real data (the best
result that is honest and showable), and write down its numbers with the query that produced them.

### 4. Plan, reviewed before building
Write the concept in 3 sentences and a storyboard table (time, what is on screen, what moves,
sound cue, exact copy). Send it to the design judge in plan mode (`review-loop.md`). Bring the user
the concept plus the decisions only they can take (max 4, each with a recommendation), for
example: rebuilt vs recorded third-party UI, music source, voiceover, caption policy. Do not build
before the user says yes.

### 5. Validate
- Screenshot scenes: write them in `storyboard.json` and run `scripts/validate.py` (crops inside
  bounds, no upscaling, headline reading time, banned phrases, CTA present).
- All copy: max 7 words per headline line; reading time words/3 + 0.5 s for kinetic type that
  arrives with the beat (words/3 + 1 s for static text); the brand's banned words; no em dashes.

### 6. Build
Follow `references/remotion.md`. Keep timing on the music's beat grid (e.g. 120 BPM = 0.5 s).
Put every tunable (times, copy, colors, which hook, which track) in one place so variants are
props, not forks.

### 7. Judge loop, measure, truth-check
- Render, then run design-judge rounds until 8/10 ("would ship as is"): `review-loop.md`.
- Measure every render with `scripts/motion.py` (targets in craft.md) and loudness with ffmpeg
  `loudnorm` (-14 LUFS integrated, -1 dBTP).
- Check the loop: the last frame should equal frame 0 (pixel diff).
- Truth-check every sentence against the source (honesty rule 8).

### 8. Deliver
- The files (full path), each with duration, size and audio stream confirmed.
- A notes file next to them: storyboard, what is real vs sample, licenses, how to re-render.
- What you verified and what you did not. **You cannot listen:** say so, and never pick the music
  alone. Offer the user 2-3 full renders that differ only in the track (and likewise for other
  taste calls such as the hook), and let them choose by eye and ear.
- Never upload or post the video. Publishing is the user's call.
