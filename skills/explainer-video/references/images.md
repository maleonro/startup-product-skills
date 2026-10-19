# Images: sketch at no cost, pay once

Style: cut-paper collage, a cartoon, never realism. The recipe that worked on the first video: a
sketch at no extra cost, the owner picks, then one final per shot. The first video needed 55-84
images for 10 minutes, so the source you pick decides most of the bill.

## 1. Pick the source: use what you already pay for

Before you quote, ask the owner which of these they have. Code comes first for anything countable
or textual (hard rule 4) and for anything that must stay identical across shots. For every other shot, walk down the list and use
the first source that passes it.

| Source | Cost per image | Best for |
|---|---|---|
| 0. **Code** (SVG, canvas, a React component) | none | always for counts, labels, funnels, flags, a wall sign; exact every time |
| 1. **An image agent you already run**: a CLI or agent with an image tool covered by a subscription (the first video used xAI's Grok Build CLI) | none per image; it draws on the subscription's usage balance | every sketch; finals too when they pass. Scriptable and parallel |
| 2. **The images your LLM subscription includes** (the ChatGPT, Gemini or Grok apps, for example) | none per image, within the app's daily cap | a few shots by hand: the owner pastes your prompts and drops the files in `sketches/`. Slow for a whole video |
| 3. **A paid image API**: an aggregator such as Higgsfield (one balance, many models), or a vendor's own API | per image; quote first | masters that must look the same in every shot; edits from references; 2K output |

- Claude itself does not generate images. It writes the prompts, scripts the agent or the API, and
  draws code layers.
- Check each app's terms and limits before you plan on it: daily caps, and some apps add a visible
  watermark. A watermarked image is a sketch, never a final.
- No subscription at all: sketch the storyboard as rough code placeholders (shapes and labels), or
  quote a cheap draft model on the paid API and get the owner's OK first.
- Count every retry: the real price is per usable image. On the hook, the paid finals cost about 1.45
  credits per image, retries included.
- A subscription balance can run out mid-batch (a `402 usage balance exhausted` from Grok Build was
  temporary). Retry a few minutes later before you switch to a paid source.
- Mix sources only after a test: the same prompt in two models gives two styles. Make the masters in
  one, and edit from them.

## 2. Shot list and cost plan

List the shots sentence by sentence. For each shot decide: generated image, or code only. Quote the
plan source by source and get the owner's OK on a cap. Put the free routes in the quote too: the
first quote forgot them, and the owner caught it.

Prices on the first video (Higgsfield, 2026-10; a credit was about US$0.05, so time and retries
mattered more than money). Prices change: quote again.

| What | Model | Cost |
|---|---|---|
| Masters: characters, places | `nano_banana_pro`, 2K | 2 cr |
| Variants: poses, objects, edits of a master | `seedream_5_0_flash` | 0.5 cr |
| Sketches | Grok Build CLI image tool | no credits; the subscription's usage balance |

Plan credits can expire when the plan renews: check the balance before planning.

## 3. Sketch with the free source

The call that worked with xAI's Grok Build CLI (`grok` 1.0.62, 2026-10; check `grok --help`, flags
change):

```
grok -p "Use your image_edit tool ONCE right now, then copy the result to <out.jpg>.
Source images: <a.jpg> <b.jpg>. Edit prompt: <prompt>" --always-approve --output-format plain < /dev/null
```

- 23 s to 2 min per image, 4 in parallel, 1280x720 out. The hook went 20 of 20 on the first try.
- **Make two molds first** (the place, the protagonist) and make every other shot an edit of them.
  The protagonist then looks the same in every shot.
- It drew photo faces: ask for "faces cut from paper". It swapped objects (planes where the script
  said envelopes): be literal ("envelopes with tiny paper wings").
- Two source images at once can paste a head onto the wall. A fresh generation from one material
  reference fixed it.
- Put the sketches on one contact sheet. The owner approves the storyboard before any spend.

## 4. Finals

With a paid API, run it from a runner script that takes a spend cap and stops before it would pass
it. Higgsfield example: quote with `higgsfield generate cost ... < /dev/null` (without the
`< /dev/null` it can hang), then
`higgsfield generate create <model> --prompt ... --image <ref> --aspect_ratio 16:9 --resolution 2k --wait --json`.

- **One master per character.** Variants are edits with the master plus the sketch as references.
  Give a variant one reference only when it must line up with a code layer: with more, it zoomed in
  and moved the background.
- **Never ask a model to count.** A 4-ring funnel failed twice; 4 people came out as 5; flags came
  out 6. Ask for the empty scene; draw counts in code, or crop the extra person in a cutout.
- **Hands that grip come out with holes.** A top-down shot with flat hands worked. Test it with the
  free source first.
- Read each final before you use it: one drew a male scientist as a woman (fixed with an edit), one
  erased the wall sign (a code layer puts it back).
- An HTTP 503 can still charge; a 520 on upload did not. Check the balance after errors.

## 5. Code layers and cutouts

Anything that must stay the same across shots (a wall sign, labels) is a code layer over the image,
with the character masked back in front of it.

- On a Mac, masks from Apple Vision with a small Swift script. **Objects mode** cuts paper figures
  whole; person mode fades them. Threshold cuts fail on white-on-grey pieces.
- Dilate masks at 640x360 and scale up: a large `MaxFilter` at full size is very slow.
- Zero the RGB where alpha is 0: the PNGs went from 4 MB to 55-306 KB.
- Envelopes, planes, cards and lists that move are drawn in code over an empty scene.
