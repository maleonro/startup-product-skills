# The edit: rhythm, motion, review

The first full cut ran 9:35 and the owner said: "the pauses and transitions between chapters are far
too long, it feels like it ended; there is little movement; the code-animated pieces are weak, except
the number bars". The design judge scored it 5/10. The re-edit ran 8:51, with the same voice and the
same images, and scored 7/10. The numbers below are what changed.

## 1. Structure (Remotion 4)

The first video's code was lost. This is the structure that worked, to rebuild. Remotion is free for
individuals and companies with up to 3 employees; larger companies need a company license
(remotion.dev/license). Ask the owner once, before step 7.

- One composition per section (hook, chapters, close, product block), each built from
  `src/<section>-timing.json`.
- A `prep` script turns Whisper's words into the timing: one shot per sentence. A shot starts 0.1 s
  before its first word. `voice` is the first word heard, never the start of the audio segment: a
  `voice` before the shot's start broke `interpolate`. `pause` adds silence before a sentence and
  `hold` adds it after, for reading a number.
- `film.tsx`: the shared section (shots, voice per sentence, subtitles). `kit.tsx`: the shared
  pieces (marks, counters, paper cards, each with its own sound). `full.tsx`: chains the sections
  (each slides in over 12 frames) with the sources page.
- Input props switch layers off for measuring: `music`, `sfx`, `subs`.
- Bundle once (`npx remotion bundle src/index.ts --out-dir <dir>`), then run `render` and `still`
  against the bundle. The full render took 16-20 min: run it in the background. Audio only
  (`--codec=wav`) took about 5 min.
- Thumbnails are Remotion stills from the video's own art (`npx remotion still ...`).

## 2. Rhythm targets

| Measure | Before | Target | Final |
|---|---|---|---|
| Silence at a chapter join, voice to voice | 4.1-6.8 s | <= 2.0 s | 1.6 s |
| Silence between sentences | no cap | <= 0.7 s (bets: 1.0-1.2 s) | met |
| Frozen frames, whole film | 46.7 % | < 15 % per section, no still run > 1.5 s | 1.9 % |
| Chapter card on screen | 0.9 s | readable | about 2.8 s |

Frozen = a frame whose mean absolute grey difference from the previous frame is under 0.15, on a
0-255 grey scale, at 192x108, every frame at the render's fps. The first video's code was lost and
did not record the unit or the frame step, so calibrate before you trust the gate: a held still must
count as frozen, and a shot with the slow camera below must not. `product-launch-video`'s
`scripts/motion.py` is a starting point, but it samples at 10 fps, 64x36, threshold 0.4: change all
three.

## 3. Visual rules (from the design judge)

- A slow linear camera on every shot (2 % per second, at most 12 %, alternate the direction).
  Consecutive shots of one scene share the camera.
- Hard cuts. A dissolve only where it means something.
- The main object is on screen from frame 0. Something small moves during every wait.
- Paper enters by sliding 30-60 px with a 1-2 degree settle over 10-14 frames.
- One light direction, real paper texture under the sheets, one red (`#b8322c`) for marks only.
- Four marks: underline (8 frames), open oval (12), count-up with tabular figures (18), a single
  big word (at most 3 in the video). At most 1 per shot and 4 per chapter. None in the product block.
- **Minimal.** Delete labels that repeat the voice. "One in N" is a row of N with one lit. The
  number bars were the one code graphic the owner liked: make the rest that simple.
- The camera must not crop the frame of a card (it cut the product block's border).

## 4. Subtitles

Burned in, plus the same timing as a `.srt` for YouTube.

- Bottom centre, one paper strip per line, hard in and out. Keep that zone free of graphics; the
  citation moves to the top left ("Author, year · caveat").
- In 2 frames before the first word, out 12 frames after the last, at least 1.0 s, never across a
  join. Never split a number from its unit ("1 in 14" stays whole).
- `.srt`: the first time is never negative (YouTube rejects the file), at most 2 lines of 42
  characters.

## 5. Review: look at frames, not at code

- Contact sheets: 2 frames per shot (at 40 % and 85 % of it), 12 per sheet. The first chapter render
  had 5 defects that the code did not show.
- A cheaper-model sweep of the sheets found 27 candidates; at full size, 8 were real. Verify each one.
- Read every on-screen text against the voice and `sources.md`. Agents flipped meanings, rounded "at
  least 3 years" to "3 years", and cited the brand outside the final block.
- Cross-check every on-screen citation against the sources page and the description. The study that
  opens the video was missing from the sources page.

## 6. The design judge

A fresh subagent each round, on your strongest model, that scores and never edits.

- Give it a named bar: Kurzgesagt. A named bar beats a list of adjectives.
- Evidence: contact sheets of the shots, strips of the joins (the last second of one chapter and the
  first of the next), and the measures (frozen %, join silences, music floor, peaks). It cannot watch
  the video either.
- Ask for a verdict file: a score out of 10, the top 3 issues, and exact fixes with shot names.
- From round 2, give it the previous verdict and ask which fixes landed: fixed, partly or not.
- Apply the fixes, render, measure, and run a new judge. Stop at 8/10, or when the owner approves.
- The full pattern, with a prompt template, is `JUAN.md` and `JUAN-PROMPT.md` in this repo's
  `landing-page` skill (install it too, or work from this section). It is written for app screens:
  say the evidence is a video's sheets and measures.

## 7. Tooling traps

- Remotion's bundled ffmpeg (inside `node_modules`, under the `@remotion/compositor-*` package for
  your platform, with `DYLD_LIBRARY_PATH` set to its folder on macOS) has no `select`, `hstack`,
  `volumedetect` or rawvideo. Grab frames with `-ss <t> -frames:v 1` in parallel; build grids with
  Pillow. An `.m4a` output needs `-f mp4`. Or install a full ffmpeg.
- `durationInFrames` must be positive: a short section broke a music fade.
- Inside a `<Sequence>`, `useVideoConfig().durationInFrames` is the Sequence's length.
- zsh does not split words in `$var` (use a function or `${=var}`), and `echo ======` is an
  expansion error.
