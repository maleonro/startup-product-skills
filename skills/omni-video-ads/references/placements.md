# Placements, safe areas and crops

The data lives in `assets/placements.json`; assembly and QC read it. This page explains it.

| Placement | Size | Master | Unsafe top / bottom / left / right | Best length |
|---|---|---|---|---|
| `reels` (IG/FB Reels, Stories) | 1080x1920 | 9:16 | 14% / 35% / 6% / 10% | <= 15 s |
| `tiktok` | 1080x1920 | 9:16 | 10% / 20% / 6% / 10% | 15-30 s |
| `shorts` | 1080x1920 | 9:16 | 12% / 25% / 6% / 12% | <= 30 s |
| `feed_4x5` (Meta, LinkedIn feed) | 1080x1350 | 9:16 crop | 5% / 8% / 5% / 5% | <= 15 s |
| `square_1x1` | 1080x1080 | either, crop | 5% / 8% / 5% / 5% | <= 15 s |
| `landscape_16x9` (YouTube in-stream, web) | 1920x1080 | 16:9 | 6% / 14% / 5% / 5% | <= 30 s |

Values are conservative unions of 2026 platform guidance (Meta: ~250 px top and ~670 px bottom on
1080x1920; TikTok: ~120 px top, ~380 px bottom, right icon rail). Platforms change their UI; if a
review shows text under UI, tighten the numbers in placements.json and log a lesson.

## Masters and crops

Omni renders only 9:16 and 16:9. The plan picks one `master_aspect`:
- 9:16 master -> reels, tiktok, shorts directly; feed_4x5 and square_1x1 by center crop.
  4:5 keeps the central ~70% of the height; 1:1 keeps ~56%. The compiler tells Omni to keep the subject
  and product in that band. `crop_anchor` (0 = top, 0.5 = center, 1 = bottom) moves the window.
- 16:9 master -> landscape_16x9 and square_1x1. A vertical placement from a 16:9 master would discard
  two thirds of the frame, so the validator refuses it (R2): make a second plan with a 9:16 master and
  reuse the same shots' content.

## Why overlays are drawn in assembly

Text is drawn per placement after cropping, so the same super sits inside the Reels safe area on the
tall frame and inside the feed margins on the 4:5 frame. `review.py cut` tints the unsafe area red on
sampled frames and fails the check if any super box leaves the safe rectangle.
