# product-launch-video

A [Claude Code](https://claude.com/claude-code) skill that builds a launch-grade product video (15-45 s) with [Remotion](https://www.remotion.dev): the kind a YC company posts on X, LinkedIn or Product Hunt on launch day. It works for any product (SaaS, AI agent, dev tool, app).

It is not a screen recorder. It rebuilds the product's key screens as animated components cut to music, from real screenshots, real data and the product's own site and brand, and it never shows a capability the product does not have.

## What it does

Eight steps, each with a gate:

1. **Intake**: the bar (tidy explainer or launch-grade), the one thing to remember, the ICP in their own words, channel and formats (1x1 master, 16x9, 9x16), length, sound, CTA.
2. **Research the bar and the brand**: the brand manual *and* the live site (the site is often bolder), plus 10-20 recent launch videos in the category measured with `scripts/motion.py`.
3. **Capture the real material**: a seeded copy of a real case, 3x device scale, crops that avoid UI oddities, and the site's own animated components to rebuild from.
4. **Plan, reviewed before building**: a 3-sentence concept and a storyboard table, reviewed by a design judge; the user approves before any code is written.
5. **Validate**: `scripts/validate.py` checks the storyboard (crops in bounds, no upscaling, reading time, banned phrases, CTA present).
6. **Build** in Remotion on the music's beat grid, with every tunable in one place so variants are props, not forks.
7. **Judge loop to 8/10**, motion and loudness measured (-14 LUFS), a seamless loop checked, and every on-screen sentence truth-checked against the source data.
8. **Deliver** the files with notes on what is real vs sample, licenses and how to re-render. Taste calls (music, hook) come back as A/B renders for the user to pick; the skill never uploads or posts.

## The thesis

A tidy walkthrough is not a launch video. Panning over real screenshots in silence scored 4/10 against the YC bar, even with perfect craft. What moved it to 8/10: music on a beat grid, the product visibly *doing* things (typing, streaming, counting, state changes), one recurring visual device, and a hook legible in one glance, with no sound, in the first 3 seconds.

And honesty is not optional: every number, label and state on screen must be one the real product produces. Rebuilt UI is fine; invented capability is not.

## Files

- [`SKILL.md`](SKILL.md): honesty rules and the eight-step workflow.
- [`references/craft.md`](references/craft.md): measured rules for hooks, motion, type, sound, camera and loops, from 20 launch videos (2025-26).
- [`references/capture.md`](references/capture.md): capturing real material and picking the showable case.
- [`references/remotion.md`](references/remotion.md): project layout and Remotion patterns.
- [`references/review-loop.md`](references/review-loop.md): the design-judge loop, in plan mode and on renders.
- [`references/products/`](references/products/): one profile per product (brand, claims, real UI, past videos, decisions taken). The skill creates it on the first video from the template in its README and keeps it updated.
- [`scripts/validate.py`](scripts/validate.py): storyboard validator.
- [`scripts/motion.py`](scripts/motion.py): motion metrics for any mp4 (mean frame difference, static %, longest hold). Needs `numpy` and `imageio-ffmpeg`.

## Install

```bash
npx skills add maleonro/startup-product-skills --skill product-launch-video
```

Or manually, by dropping the folder into your skills directory:

```bash
cp -r skills/product-launch-video ~/.claude/skills/product-launch-video
```

Then ask Claude Code for a launch video, demo clip, feature announcement or animated walkthrough, or to turn screenshots into a video.
