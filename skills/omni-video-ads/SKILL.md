---
name: omni-video-ads
description: Plans, generates and finishes short video ads with Google's Gemini Omni Flash (gemini-omni-1.1-flash) - brief to shot plan, validated prompts, cost-guarded generation with turn-by-turn edits and extensions, real UGC or screen recordings cut in alongside generated shots, then per-placement cuts (Reels, TikTok, Shorts, 4:5 and 1:1 feed, 16:9) with exact on-screen text, end card and AI disclosure, plus frame-level QC that feeds a lessons log. Use when the user wants an AI-generated video ad, UGC-style or product video, a hook or variant for paid social, or asks to "make a video with Omni/Gemini", "animate this product photo into an ad", "hacé un video para Reels/TikTok", "armá un ad de video", "genera un anuncio en video", even without naming Omni. Not for editing recorded video with no generation, long-form films, or still image ads.
---

# Omni video ads

Turns a brief into finished, placement-ready video ads. Gemini Omni generates the clips; the scripts
decide everything that must be exact (text, timing, crops, safe areas, loudness, cost) so the model only
does what it is good at.

Three rules hold throughout:
1. **Plan, validate, then spend.** No generation runs until `validate_plan.py` reports 0 errors and the
   user has seen the estimated cost. Live runs refuse to start without `--budget`.
2. **The model renders images, not copy.** Ad text in any language is overlaid in assembly (`supers`);
   prompt fields are written in English.
3. **Look at the output.** Read the contact sheets and safe-zone sheets before reporting, and log a lesson
   for every real failure.

## Terms

- **plan**: `adplan.json`, the single source of truth for one ad (one master aspect).
- **shot**: one entry in `plan.shots`: one generation call, or a `recorded` clip cut in as-is.
- **clip**: the video file a generation call returns. **Take**: one version of a shot's clip (each edit
  makes a new take with a new interaction id).
- **chain**: shots linked by `extend`; its last clip holds the whole chain.
- **segment**: one chain (or single shot) placed on the timeline.
- **super**: text drawn over the video in assembly. **End card**: the closing frame with the CTA.
- **placement**: a delivery format (reels, tiktok, feed_4x5...). **Deliverable**: the finished file for one placement.
- **pass**: `draft` (cheap, 360p) or `final`.

## Checklist

Copy this into your task list and tick it off. `<skill>` is this skill's folder; run everything from the
user's working folder (where the plan lives), so outputs land in `out/<plan name>/` there.

```
- [ ] 1. bash <skill>/scripts/check_env.sh            -> LIVE (exit 0) / DRY-RUN (1) / BLOCKED (2)
- [ ] 2. python3 <skill>/scripts/review.py lessons     -> apply what past runs learned
- [ ] 3. Brief -> angle and shot list                  (references/ad-structure.md)
- [ ] 4. Write adplan.json                             (assets/example/plan.json, references/plan-schema.md, references/prompt-craft.md)
- [ ] 5. python3 <skill>/scripts/validate_plan.py adplan.json          -> fix every ERROR, judge every WARN
- [ ] 6. python3 <skill>/scripts/build_jobs.py adplan.json --pass draft -> read the prompts, tell the user the cost
- [ ] 7. python3 <skill>/scripts/generate.py run out/adplan/draft/jobs.json --budget N   (DRY-RUN: --mock)
- [ ] 8. python3 <skill>/scripts/review.py clips out/adplan/draft      -> Read every contact sheet, fix, re-run
- [ ] 9. build_jobs.py adplan.json --pass final -> user confirms cost -> generate.py run out/adplan/final/jobs.json --budget N
- [ ] 10. assemble.py adplan.json --pass final ; review.py cut out/adplan/final -> Read every safe_zone_sheet.jpg
- [ ] 11. review.py lesson ... per real failure; deliver files, spend, disclosure reminder, open placeholders
```

## Step notes

**1. Environment.** `check_env.sh` prints the mode and never prints the key. DRY-RUN is a normal mode:
build jobs, write request payloads with `--dry-run`, and run the whole pipeline with `--mock` (labelled
placeholder clips) to show the user the cut structure, timing and supers before spending. If the user
works from the EEA, Switzerland or UK, set `OMNI_REGION=eu` (or `"region": "eu"` in the plan): Omni blocks
uploaded-video edits/extensions and uploads of recognizable people there (references/omni-api.md section 7).
The working route there: cut the user's real clip in as a `recorded` shot and generate the rest. Do not
suggest VPNs, another region or another account to get around the block.

**3. Brief.** Missing product, audience, offer/CTA or placements: ask once, in one message. Missing angle:
propose 2-3 one-line angles and let the user pick. If the user cannot answer now, continue with clearly
marked placeholders, list them in your final message, and never run a live final pass with placeholders
(the validator warns on `.example`, `TBD` and similar in the end card). Use the user's product photos and
logo: a real product photo as `first_frame` is the most reliable way to keep the pack exact.

One plan = one master aspect. Vertical placements (reels, tiktok, shorts, feed_4x5) come from a 9:16
master; landscape_16x9 needs a 16:9 master. If the user wants both, write two plans (for example
`ad_vertical.json` and `ad_landscape.json`); their outputs go to `out/ad_vertical/` and `out/ad_landscape/`.

**4. Plan.** Copy `assets/example/plan.json` (a complete, valid 15 s example with its images) and replace
the content. The first shot is the hook. Every generated shot gets subject + action, three concrete
details, one camera move, audio direction and a final image. Put anyone who appears in more than one
segment in `characters` with a full identity block. Real material the user owns (UGC, a testimonial,
a screen recording of their product) goes in as `mode: "recorded"` with `source_video` and optional
`trim`: it is cut in unchanged, costs nothing, and works in every region. A real, identifiable person
needs `source_contains_people: true` and, once they have consented in writing, `brief.likeness_consent: true`.

**5. Validate.** Rule IDs and reasoning: references/validation-rules.md. Common fixes: move non-English
`native_text` to `supers`; add the missing detail; shorten the dialogue; keep a recurring person inside
one extend chain or give them a reference still.

**6. Build + cost.** Read the compiled prompts: they are what Omni sees. Report the draft and final
estimate (720p is $0.10/s; extensions bill their cumulative length, including an uploaded source) and get
a yes before any live run. `--only s1,s3` rebuilds just some shots (dependencies are added).

**7-8. Draft and QC.** Draft at 360p. For each contact sheet check: does frame 0-2 s stop the scroll, is
the product recognisable, do faces and hands hold, does the final frame match `final_image`. Score in
`out/<plan>/draft/qc/<shot>/qc.json`. Mock clips are flat colour cards: after a `--mock` run check only
structure (shot order, durations, supers, end card) and leave the creative scores null.
To fix one thing in a take, use a turn-by-turn edit:

```
python3 <skill>/scripts/generate.py edit out/adplan/draft/jobs.json --shot s2 --prompt "Make the can matte" --budget 1
```

It chains from the newest interaction id and keeps the previous take as `s2.v1.mp4`. Anything bigger:
change the plan and re-run (unchanged shots are skipped).

**9. Final.** The final pass regenerates, so takes differ from the draft; shots anchored with a
`first_frame` change least. `generate.py promote` (keep-everything edit at higher resolution) is
experimental: if you use it, run `review.py compare out/<plan>/draft out/<plan>/final` and log the result.

**10. Assemble and review.** `assemble.py` writes one file per placement to `out/<plan>/<pass>/deliverables/`,
with supers inside each placement's safe area, the end card, optional AI label, and audio normalised to
-14 LUFS. Add `--voiceover vo.wav` and/or `--music bed.mp3` to mix recorded audio over the model's sound.
`review.py cut` must report no issues; then Read each `safe_zone_sheet.jpg` (red = platform UI): hook
readable at 0-1 s, product visible in its segment, no text under red, end card legible.

**11. Deliver.** Log one lesson per real failure or surprise (a validator block that changed the plan
counts; `--score` only when the lesson is about one clip). Send the placement files, and tell the user in
one line each: which file goes to which placement, the actual spend, open placeholders, and that
realistic AI people need the platform's AI label on upload (references/compliance.md). Variants that
change only text reuse the clips: edit supers/end card and re-run `assemble.py` alone.

## References (read when the step needs them)

- references/omni-api.md: call shape, limits, modes, tags, editing/extension, pricing, regional blocks, failure signatures
- references/prompt-craft.md: how to write each shot field so it renders
- references/ad-structure.md: hooks, beat patterns, pacing, sound-off, supers, end cards, variants
- references/placements.md: sizes, safe areas, crops from one master
- references/plan-schema.md: every adplan.json field
- references/validation-rules.md: rule IDs and why each threshold exists
- references/compliance.md: disclosure by platform, consent, hard stops, claims
- references/adapters.md: adding another video model (fal, Replicate, Veo, Kling, Seedance)

## Dependencies

Python >= 3.10, Pillow, ffmpeg/ffprobe (overlay filter; drawtext only for `--mock`), and for live runs
`google-genai >= 2.19` plus `GEMINI_API_KEY`. Lessons accumulate in `~/.omni-video-ads/LESSONS.md`
(`LESSONS_PATH` overrides), never inside this skill. Tests: `python3 <skill>/tests/run_tests.py`
(no key needed; `--fast` skips ffmpeg).

## Out of scope

Political or social-issue ads, a real person's likeness without consent, fake testimonials, other
brands' marks (references/compliance.md). Product UI should be recorded, not generated: cut the screen
recording in as a `recorded` shot and generate the human context around it.
