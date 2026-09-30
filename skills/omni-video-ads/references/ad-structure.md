# Ad structure: from brief to shot list

Read this when turning a brief into the `shots` of a plan. It decides what the ad says and in what
order; prompt-craft.md decides how each shot is written.

## Contents
1. Brief checklist
2. The first two seconds (R18)
3. Beat patterns by ad type
4. Length and pacing
5. Sound-off design
6. Supers
7. End card (R19)
8. Variants for testing

## 1. Brief checklist

Before writing shots, have (from the user, their files, or a connected brand tool):
- Product and the one thing it should be remembered for.
- Audience in one line, and the moment of pain or desire the ad enters.
- Offer and CTA (the end card needs a CTA; R19).
- Placements, which set master aspect, length and safe areas.
- Assets: product photos (best `first_frame` material), logo, brand colours, font.
- Claims and their proof (R20).

If the angle is missing, write 2-3 angle options in one line each and ask which one to shoot. Do not
build a plan around two angles at once: the cut changes its mind halfway.

## 2. The first two seconds (R18)

The first shot has role `hook`. A scroller decides in about two seconds, often muted. The hook must
work with the image plus one super, no sound. Proven openings:

| Hook | What the first frame shows | Example super |
|---|---|---|
| Problem callout | the pain, physically, mid-action | "¿Te pasa a las 3pm?" |
| Result first | the after state, then rewind | "Así quedó en 7 días" |
| Pattern interrupt | an unexpected action or object, already moving | (none, or one word) |
| Curiosity | a close detail that raises a question | "Nadie te cuenta esto" |
| POV / UGC | handheld, first person, a real-looking moment | "POV: ..." |

Rules: start mid-action (no slow establishing shot), keep the first super at 0-0.5 s and <= 7 words,
show motion in frame 1, and put the product on screen by ~40% of the cut at the latest.

## 3. Beat patterns by ad type

Roles map to validator roles. Durations assume a 15 s cut with a 2 s end card.

- Problem -> solution (default for performance): hook/problem (3) -> reveal (3-4) -> use (3) ->
  proof or reaction (2-3) -> hero (2-3) -> end card.
- Product drama (premium, food, beauty): hook as sensory macro (3) -> reveal (3) -> macro texture (3) ->
  use (2-3) -> hero (2) -> end card.
- Demo / how it works (B2B, apps): hook as result (3) -> use in 2-3 steps (3 each) -> proof -> end card.
  Screens and UI are better recorded than generated: cut them in as `recorded` shots and generate
  the human context around them.
- UGC style: one continuous handheld take built with `extend` (hook 5 + 5 + 5), talking to camera if
  the language is English, otherwise supers plus a recorded voiceover.
- Real UGC + generated: the customer's own clip as a `recorded` hook or proof shot (with her written
  consent), generated product shots around it. Recorded shots cost nothing and work in every region.

Every shot does one job. If two shots do the same job, cut one.

## 4. Length and pacing

- Reels, feed: <= 15 s. TikTok and Shorts: 15-30 s. The validator warns past each placement's best length.
- 3-4 s per shot keeps a 15 s ad moving; hero and hook can be shorter.
- Use `extend` when continuity matters more than variety (same person, same take). Use separate
  generations when you want cuts between angles.

## 5. Sound-off design

Most feed video plays muted. The ad must be understood with sound off: supers carry the message, the
product is visible, the action is legible. Sound is the bonus layer. For Reels and feed, assume mute.

## 6. Supers

- One idea per super, <= 7 words in the hook, <= 8 elsewhere, readable at ~3 words per second (R15).
- Positions: `top`, `center`, `lower`. Each renders inside the placement's safe area (platform UI
  covers the rest), so one plan serves Reels, TikTok and 4:5 feed.
- Do not overlap supers. Do not put the URL in a super; it belongs on the end card.

## 7. End card (R19)

1-4 s. Logo (optional), `headline` (the offer), `cta` (a button), optional `url`. If the ad shows
realistic generated people, `disclosure.ai_label: true` puts "Video generado con IA" (or your text)
on the card; `disclosure.overlay: true` also adds a small label across the whole cut.

## 8. Variants for testing

Cheap variants reuse the generated clips: change supers, the hook super, the end-card offer or the
voiceover, then re-run only `assemble.py`. A new hook shot costs one short generation: copy the plan,
replace `s1`, and use `build_jobs.py --only s1` (other shots are reused when you copy their outputs,
or regenerate them if you want a fresh take).
