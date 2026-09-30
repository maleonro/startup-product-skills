# omni-video-ads

A [Claude Code](https://claude.com/claude-code) skill that makes short video ads with **Google's Gemini Omni Flash**. The model generates the footage. Scripts handle everything that must be exact: on-screen text, timing, crops, safe areas, loudness and cost.

It is the generative sibling of [`product-launch-video`](../product-launch-video/). That skill rebuilds your real product UI in Remotion, with no generated footage. This one generates people, products and scenes for paid social, and cuts your real recordings in next to them.

## What it does

1. Turns a brief into an angle and a shot list (hook first).
2. Writes one `adplan.json` and validates it: no generation runs until the validator reports 0 errors and you have seen the cost.
3. Drafts at 360p with a hard `--budget`, then shows contact sheets to judge each shot.
4. Fixes one thing at a time with turn-by-turn edits, then runs the final pass.
5. Cuts one file per placement (Reels, TikTok, Shorts, 4:5 and 1:1 feed, 16:9) with supers inside the safe area, an end card, the AI label and audio at -14 LUFS.
6. Logs one lesson per real failure, so the next run starts smarter.

Your own UGC or screen recordings go in as `recorded` shots: cut in as they are, at no cost. Product UI should be recorded, not generated.

## Files

- [`SKILL.md`](SKILL.md) — the 11-step checklist and step notes.
- [`LESSONS.md`](LESSONS.md) — seed lessons; your runs add more in `~/.omni-video-ads/LESSONS.md`.
- [`references/`](references/) — Omni API, prompt craft, ad structure, placements, plan schema, validation rules, compliance, adapters for other video models.
- [`scripts/`](scripts/) — validate, build jobs, generate (live or `--mock`), assemble, review.
- [`assets/example/`](assets/example/) — a complete, valid 15 s plan with its images.
- [`tests/`](tests/) — `python3 tests/run_tests.py` (no API key needed; `--fast` skips ffmpeg).

## Requirements

Python 3.10+, Pillow, ffmpeg/ffprobe. For live runs: `google-genai >= 2.19` and `GEMINI_API_KEY`. Without a key it runs in dry-run mode with placeholder clips, so you can check the cut before you spend.

## Install

```bash
npx skills add maleonro/startup-product-skills --skill omni-video-ads
```
