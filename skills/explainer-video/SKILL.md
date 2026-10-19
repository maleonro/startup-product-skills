---
name: explainer-video
description: Builds a Kurzgesagt-style educational explainer video (about 8-10 min, any language) end to end - a fact-checked sources sheet, a script curated in rounds by an editor subagent, paper-collage images made the cheapest way available (code, an image agent or LLM subscription you already pay for, then a paid API such as Higgsfield), a synthetic voice, one music piece per chapter, a Remotion edit scored by a design-judge subagent, burned-in subtitles and the YouTube package - with the measured rules and traps from the first one. Use when the user wants an educational or explainer video, "a video like Kurzgesagt", a YouTube video that teaches, or to script, storyboard, voice, score, edit or publish one.
---

# Explainer video (Kurzgesagt style)

The bar: someone with no background gets one idea on the first listen, learns something new, and
can retell it the next day. It is not an ad. The first video made this way (8:51, Spanish,
https://youtu.be/pio_TsNUXNQ) took 11 script versions, 4 cuts and about 170 Higgsfield credits of
paid generation. Every rule here is a correction its owner had to make on it.

## Hard rules

1. **Every number comes from the sources sheet** (`sources.md`): voice, screen and description.
   Every "Do not say" in it holds. Check against the original paper, not a summary. See
   [references/script.md](references/script.md).
2. **Educational, not commercial.** If a company makes the video, its product appears once, in a
   closing block like Kurzgesagt's sponsor segment. Before it, own data is cited as "Data: 40
   companies", never with the brand. The lesson must not contradict what the product does: fix the
   idea, never hide the product.
3. **No paid generation without the owner's OK on the exact cost.** Quote first, from the price
   page or from a cost call if the API has one. A cap covers only the unit prices you quoted: if a
   step costs more, stop and ask. Free first: what the owner already pays for, and graphics drawn in code (see
   [references/images.md](references/images.md), "Pick the source").
4. **Nothing countable or textual in a generated image.** Image models cannot count rings, flags or
   people, and they misspell. Ask for the empty scene and draw the rest in code.
5. **You cannot hear or watch the video: measure it.** Frozen frames, silence at joins, music level,
   sound peaks. Then look at stills yourself. Code that looks right rendered 5 defects on first try.
6. **The strongest model directs, a cheaper one executes** (Claude Opus and Sonnet on the first
   video). Execution agents get a closed brief: what, where, spend cap, how it is checked. At most 2
   long agents at once. You review every render: agent self-reviews missed real defects.

## Workflow

Copy this checklist into your reply and tick it off. Every step marked `$` can spend money: quote
it, then get the owner's OK on that number (rule 3).

```
- [ ] 1. Topic, length, language and voice agreed; sources sheet built and fact-checked  (script.md)
- [ ] 2. Script curated by the editor subagent until the owner likes it; timed at the
         voice's measured pace                                              (script.md, editor.md)
- [ ] 3. Shot list; image source picked; cost plan; storyboard sketched (free source first);
         owner picks                                                                 (images.md)
- [ ] 4. $ Finals under the approved cap; cutouts; code layers
- [ ] 5. $ Voice: 3 samples on the hook, owner picks; full take; word times           (sound.md)
- [ ] 6. $ Music: 3 style samples under the voice, owner picks; one piece per chapter, levelled
- [ ] 7. Remotion edit per section, subtitle zone kept free; paper sounds; contact sheets;
         frozen < 15 %, joins <= 2 s                                                   (edit.md)
- [ ] 8. Burned-in subtitles + .srt; sources page; every on-screen text checked against the voice
- [ ] 9. The design judge scores the whole cut (picture and sound measures) until 8/10  (edit.md)
- [ ] 10. YouTube package with the youtube-seo skill, after a benchmark of similar videos
- [ ] 11. Deliver; after 7 days and 100 views, read the numbers in Studio
```

Read each reference at the step that needs it:
[script.md](references/script.md) and [editor.md](references/editor.md) (1-2),
[images.md](references/images.md) (3-4), [sound.md](references/sound.md) (5-6),
[edit.md](references/edit.md) (7-9).

The judge's bar is 8/10. The first video shipped at 7/10 because its owner approved it: ask, do not
assume.

## The project folder

`<name>/`: the scripts (`script-v<n>.md`), the editor's reviews (`review-<n>.md`), `sources.md`, the
owner's notes (`notes-v<n>.md`), `sketches/`, `finals/`, `audio/`, `src/` (Remotion), `scripts/`,
`out/` and `youtube/`.

**Commit the text and the code the day you start (never `out/`), and back up `finals/` and `audio/`
outside the repo.** The first video was never committed. Its workspace was deleted and took the code
with it: only the renders and the YouTube package survived. Scratch folders are wiped between
sessions too, so keep helper scripts (runners, measurements, sheets) in `scripts/`.

## Working with the owner

- Taste calls go as 3 samples, never a description: 3 voices on the hook, 3 music styles mixed under
  the voice at the final level (plus "how it sounds today"), 3 very different thumbnails.
- The owner sends notes in batches. Collect them in `notes-v<n>.md` and give them to the editor
  together.
- Move large files with a CLI (rclone, gsutil, aws s3), not a chat connector that takes base64 only.
- When the owner hands over ("you don't need me to review"), ask for a spend cap if they gave none,
  set your own below it, write the plan to a file, and still review every render yourself.

## Publish

Use the **`youtube-seo`** skill. Before writing the description or the thumbnails, benchmark the
most-viewed similar videos of the last 6 months: the owner rejected a description built from blog
rules and accepted one built from 67 peers. Thumbnails can be strong, but only with numbers the
video gives. Say which text goes into which Studio field, title apart: the owner once pasted two
description lines into the title field.

## Related

Skills from the same repo (`maleonro/startup-product-skills`); install the ones you use.

- `youtube-seo`: the publish package and its checker. Needed for step 10.
- `landing-page`: `JUAN.md` and `JUAN-PROMPT.md`, the full design-judge pattern. Optional.
- `product-launch-video`: 15-45 s launch films. Its `references/remotion.md` covers Remotion and its
  `scripts/motion.py` is a start for the frozen-frame measure. Optional.
