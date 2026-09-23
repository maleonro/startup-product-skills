# Remotion build, render and inspection

## Where the project lives

Outside the product's repo, so it never touches its lockfile or git hooks: e.g.
`~/<product>-videos/<slug>/`. Ask the user before moving it into the repo.

```
npx create-video@latest --blank <slug>     # npm, not pnpm
cd <slug> && npm i @remotion/fonts playwright
```
Keep every `remotion` and `@remotion/*` package on the same exact version.

**License**: Remotion is free for individuals and companies with up to 3 employees. Above that it
needs a company license. Ask the user once if you do not know the headcount.

```
<slug>/
  storyboard.json        # the single source; validated by scripts/validate.py
  public/
    assets/              # captured and transcoded files, blur already applied
    fonts/               # the brand's woff2 files (from the site)
    brand/               # logo, mascot sprites
    audio/               # music + SFX, with LICENSES.md
  src/
    Root.tsx             # one <Composition> per format, all reading storyboard.json
    Video.tsx            # maps scenes to <Sequence>s
    Camera.tsx
    Highlight.tsx
    Caption.tsx
    EndCard.tsx
    recreations/         # one file per recreation, named after its source screenshot
    tokens.ts            # colors and easing copied from the brand manual
  capture/               # Playwright scripts that produced public/assets
```

## Formats

| id | size | product box (default) | text safe area |
| --- | --- | --- | --- |
| `16x9` | 1920x1080 | 1000x500 plate, text column on the left | 96px margin all sides |
| `1x1` | 1080x1080 | 1080x540 full-bleed band | 72px margin; the master for X and LinkedIn (phones) |
| `9x16` | 1080x1920 | 960x1200 | x 64-1016, y 240-1440 (platform UI covers the rest) |

The box sizes live in `storyboard.json` (`productBox`), so change them there, not in code.
30fps unless every recording is 60fps.

## Components

- **Fonts**: `loadFont({family, url: staticFile('fonts/…woff2'), weight, style})` from
  `@remotion/fonts`, awaited before render (it handles `delayRender`).
- **Camera**: takes the scene's focus keyframes `{at, rect:[x,y,w,h]}` in source pixels and
  interpolates between them with an in-out curve (`Easing.bezier(0.45, 0, 0.55, 1)`); the house
  ease `bezier(0.23, 1, 0.32, 1)` is for arrivals only. Prefer holds joined by short moves over
  one long move. It computes
  `scale = box.w / rect.w` and translates so the rect fills the product box. Clamp scale so it
  never exceeds `box.w / rect.w` for the smallest rect; the validator already refuses upscaling.
- **Recording**: `<OffthreadVideo>` (never `<Video>` for rendering), with `startFrom` in frames and
  `playbackRate` from the scene. When `playbackRate > 1`, render the scene's `speedLabel` in
  JetBrains Mono in a corner.
- **Highlight**: dims everything outside a rect with `--ink` at about 55% opacity, and draws a
  1px `--flare` outline on the rect. That outline is the frame's one flare use.
- **Caption**: headlines in Space Grotesk 500 (never Spectral), labels in JetBrains Mono.
  Always inside the format's safe area. Enter with opacity and 4px of translate, 240ms, house
  ease; a line that did not change from the previous scene does not arrive again.
- **EndCard**: logo, the value proposition verbatim, the exact CTA text and URL. At least 2s.

## Blurring personal data

Blur in the **source file**, before import, never with CSS `backdrop-filter` (unreliable in
headless render, and the unblurred pixels are still in the asset).
- Image: Python with PIL, `ImageFilter.GaussianBlur(24)` on each box, or a solid `--linen` box.
- Recording, static box:
  ```
  ffmpeg -i in.mp4 -filter_complex "[0]crop=w:h:x:y,boxblur=20[b];[0][b]overlay=x:y" -c:v libx264 -pix_fmt yuv420p -crf 18 out.mp4
  ```
- Recording where the content scrolls or moves: do not chase it with boxes. Re-capture on seeded
  data, or use a still.

## Rendering

```
npx remotion render <CompId> out/<id>.mp4 --codec=h264 --pixel-format=yuv420p --crf=18 \
  --concurrency=<≤ cores> [--scale=0.5 for drafts] \
  [--browser-executable="/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"]
npx remotion ffmpeg -i out/<id>.mp4 -c copy -movflags +faststart out/<id>.final.mp4
```
All the target channels (X, LinkedIn, Product Hunt via YouTube) take a 60s H.264 MP4 easily.
Keep each file under 50MB. Check the channel's current limits at upload time if the user asks.

## Inspecting frames

```
# one still, full size
npx remotion still <CompId> out/still-<frame>.png --frame=<n>

# one frame per second (Remotion's bundled ffmpeg rejects -vf filters: use -r),
# then tile them into a contact sheet with PIL
npx remotion ffmpeg -i out/<id>.mp4 -r 1 out/frames/%02d.png

# frames from a source recording, one every 2s (for the asset audit)
npx remotion ffmpeg -i public/assets/rec.mp4 -r 0.5 out/audit-%02d.png

# the output's real properties
npx remotion ffprobe -v error -show_entries stream=codec_name,pix_fmt,width,height,r_frame_rate,avg_frame_rate:format=duration,size -of compact out/<id>.final.mp4
```
Open each PNG with the Read tool. A contact sheet shows pacing; only full-size stills show clipped
text, fallback fonts and blurry zooms.

## Launch-grade builds (rebuilt, animated components)

Structure that worked:
- `kit.tsx`: brand tokens, easing helpers (`arrive` = brand ease for arrivals, `morph` = in-out for
  camera), `Words` (word-by-word headline with per-word start times, an accent word in italic, `|`
  for a forced line break), `Mono` labels, the logo, the mascot sprite (a 3x3 sheet: position the
  cell with `left: -(i % 3) * size, top: -floor(i / 3) * size`), a small icon set.
- One file per rebuilt surface (chat window, workflow graph, grid of units, list rows), each driven
  by a local time `t` and a script object (prompt, send time, streamed lines, counters).
- `Film.tsx`: the layout per format, a design stage (e.g. 1000x700) scaled into each format, the
  scene switch by time, headlines by time, full-frame layers for transitions, and the audio.
- `sound.ts`: the music (file, trim to its first downbeat, playbackRate to match the cut's BPM,
  volume, duck windows) and an SFX event list `{at, file, volume}` rendered as `<Sequence>` +
  `<Audio>`.
- Variants are props (`hook`, `music`) with one `<Composition>` per variant, so A/B renders share
  every frame except the one thing being compared.

Audio in Remotion 4: `<Audio src trimBefore={frames} playbackRate volume={(f) => …} />`
(`startFrom` is deprecated). A volume callback does fades and ducking.

## Mastering and measuring
Remotion's bundled ffmpeg rejects `-vf`/`-af` filters. Use a full ffmpeg (e.g. `pip install
imageio-ffmpeg` and call `imageio_ffmpeg.get_ffmpeg_exe()`):
```
ffmpeg -i raw.mp4 -c:v copy -af "loudnorm=I=-14:TP=-1:LRA=11" -c:a aac -b:a 192k -ar 48000 -movflags +faststart final.mp4
ffmpeg -i final.mp4 -af loudnorm=I=-14:TP=-1:print_format=summary -f null -   # verify
python3 scripts/motion.py final.mp4                                           # motion metrics
```
Check the loop: render frame 0 and the last frame as stills and diff them (PIL `ImageChops`).

## Gotchas
- A stage with `overflow: hidden` clips zooms: do zoom-through transitions in a full-frame layer.
- Objects scaled 20-50x reveal their neighbours; pick the scale from the object's position so it
  covers every frame edge in every format.
- Load every font style you use (italic is a separate file).
- Do not let a slow push-in grow a window into the lockup; compute its final bounds.
