# Gemini Omni Flash: what the API does and where it stops

Checked 2026-09-27 against Google's docs (ai.google.dev/gemini-api/docs/omni, /pricing) and Google's
reference skill (github.com/google-gemini/gemini-skills, `gemini-omni-flash-api`, updated 2026-09-23).
Re-check when a call behaves differently from this page, then log a lesson.

## Contents
1. Model and call shape
2. Limits
3. Modes and how the scripts map them
4. Role tags
5. Turn-by-turn editing and extension
6. Resolution, draft vs final, upscaling
7. Regional restrictions
8. Pricing
9. Failure signatures

## 1. Model and call shape

- Model id: `gemini-omni-1.1-flash` (override with `GEMINI_OMNI_MODEL`). SDK: `google-genai >= 2.19`, Python >= 3.10.
- One call = `client.interactions.create(model, input=[parts...], response_format={...}, store, background, previous_interaction_id?)`.
- `input` is an ordered list: image parts, video parts, then one text part. Local media is uploaded first
  through the Files API and referenced by `uri` + `mime_type` once the file is `ACTIVE`.
- `response_format`: `type: "video"`, `aspect_ratio` `9:16`|`16:9`, `resolution` `360p`|`720p`|`1080p`|`4k`,
  `duration` `"3s"`..`"10s"`, `delivery` `uri` (used here) or `base64` (default, only for clips < ~4 MB).
- `store: true` is required for any later edit or extension of that output. `background: false` makes the
  call synchronous; a 4K call can take several minutes (`OMNI_TIMEOUT_S`, default 900).
- Output is MP4 with generated audio and an invisible SynthID watermark on every clip.

## 2. Limits

| Limit | Value | Enforced by |
|---|---|---|
| Clip length per call | 3-10 s, integer | validator R4 |
| Extension | +10 s max per turn, 40 s cumulative per chain | R17 |
| Reference images | 6 per call | R6 |
| Reference videos | 3 per call, ~3 s each works best | R6 |
| Uploaded video to edit/extend | <= 10 s | R6 |
| Aspect ratios | 9:16, 16:9 only | R2 (4:5 and 1:1 are crops in assembly) |
| Languages | English fully supported; others not evaluated | R13, R14, R15 |
| Voice editing, YouTube URLs as input | not supported | - |

## 3. Modes and how the scripts map them

| Plan `mode` | Inputs | Use in an ad |
|---|---|---|
| `text_to_video` | prompt | hooks, lifestyle, problem scenes |
| `first_frame` | `first_frame` image | product reveal from a real product photo (keeps the pack exact) |
| `first_last` | `first_frame` + `last_frame` | transitions, before/after, loops (same image twice) |
| `reference` | `image_refs` (+ `video_refs`) | same product/person in a new scene; motion borrowed from a clip |
| `extend` | `continues` (a generated shot) or `source_video` | a longer continuous take, 10 s at a time |
| `edit` | `edits` (a generated shot) or `source_video` + `edit_prompt` | fix one thing in an approved take |
| `recorded` | `source_video` (+ `trim`) | not an Omni call: real UGC, testimonials or screen recordings cut in unchanged |

`first_frame` is the most faithful way to keep a product's label and shape; references are looser.

## 4. Role tags

Simple cases: prefix `<FIRST_FRAME>` or `<FIRST_FRAME> <LAST_FRAME>`. Mixed inputs use declarations first,
guidance last (the compiler writes these):

```
[# Sources <FIRST_FRAME>@Image1] [# References <IMAGE_REF_0>@Image2] <IMAGE_REF_0> is the product. ...
Use Image1 as the starting frame. Use the given image(s) as references for video generation.
The images should not be used as literal initial frames.
```

Images and videos are numbered separately in input order, from 1. Reference tags count from 0.

## 5. Turn-by-turn editing and extension

- Each turn returns a new interaction id and a new video. Always chain from the newest id; editing
  from an older id silently forks from an older state. `generate.py` keeps `history` per shot and uses
  the last entry.
- Extensions return the cumulative video (the earlier clip plus the new part; Omni retouches the last
  frames of the earlier part so the join is seamless). `assemble.py` measures the output and falls back
  to stitching if a provider ever returns only the new part.
- Timecodes in an extension prompt count from the start of the new part.
- Edit prompts: short and literal ("Make the can matte. Keep everything else the same."). Long,
  descriptive edit prompts change things you did not ask for.
- Setting `generation_config.video_config.task` (`extend`, `edit`...) disables multimodal references.
  The scripts never set it; prompting ("Extend this video.") is Google's recommended default.
- Extending an uploaded video where someone speaks cannot add new dialogue; dialogue extension works
  only on generated videos via `previous_interaction_id`.

## 6. Resolution, draft vs final, upscaling

- 360p is the cheap draft tier (about 1/3 the price of 720p, up to 60% faster). 720p is native;
  1080p and 4K are upscaled from the native generation, so they add sharpness, not detail.
- A draft cannot be promoted by a documented API call. The final pass regenerates, and the same prompt
  gives a different take. Consequences for ads:
  - Anchor shots that must match the approved draft with `first_frame` from a high-res still (a product
    photo, a static ad frame). The draft then validates the motion, and the final keeps the composition.
  - `generate.py promote` tries a keep-everything edit at a higher resolution. This is EXPERIMENTAL
    (undocumented); run `review.py compare` and log a lesson with the outcome.
- Default: draft 360p, final 720p. Choose 1080p final for delivery sharpness on 1080x1920 placements.

## 7. Regional restrictions (EEA, Switzerland, UK)

Blocked there: editing or extending uploaded videos, and uploading images of recognizable people or
minors. Editing and extending videos Omni generated works everywhere. Safety filters also vary by region.
Set `OMNI_REGION=eu` (or `--region`) and the validator (R8) blocks these before any spend. Workaround:
rebuild the shot from a first frame (a still with no recognizable person), describe the person in text,
or cut the real clip in unchanged as a `recorded` shot (no upload to Omni; needs the person's consent).
The restriction is Google's legal boundary: never suggest a VPN, another region or another account to
get around it.

## 8. Pricing (estimates; the provider bills the truth)

| Resolution | USD / output second | Source |
|---|---|---|
| 360p | ~0.03 | third-party list price |
| 720p | 0.10 | Google: 5,792 output tokens/s at $17.50 per 1M tokens |
| 1080p | ~0.15 | third-party list price |
| 4k | ~0.30 | third-party list price |

Override with `OMNI_PRICE_JSON='{"1080p":0.12}'`. The estimator bills extensions at their cumulative
length, including an uploaded source clip (upper bound, because output tokens cover the whole returned
video), and edits at the length of the clip being edited.

## 9. Failure signatures

| Symptom | Likely cause | Fix |
|---|---|---|
| "Omni returned no video", no error | safety filter, or regional block on uploads | check R8; soften the prompt; remove recognizable people |
| Several cuts inside one clip | model default multi-shot behaviour | keep `single_take: true` (adds "Single continuous shot, no scene cuts.") |
| Generic orchestral score | no audio direction | set `audio` / `music` / `style.audio_bed` (R12) |
| Garbled on-screen words | model-rendered text in a non-English ad | use `supers` (R15) |
| Edit changed the whole scene | edit prompt too descriptive | shorten; end with "Keep everything else the same." |
| Face changes between shots | separate generations with no reference | `ref_image` + `image_refs`, or chain with `extend` (R16) |
