# Craft: what separates a launch video from a walkthrough

Measured on 20 launch videos from 2025-26 (Granola, Notion, Cursor, Claude, Figma, Lovable, Attio,
ElevenLabs, Devin, Exa…) and on our own iterations (a silent screenshot pan scored 4/10; the
rebuilt, scored version 8/10). Numbers are targets, not laws.

## The measurements
Run `scripts/motion.py <mp4>` (10 fps, 64x36 grayscale, mean frame difference):

| metric | walkthrough (4/10) | launch-grade target |
|---|---|---|
| meanDiff | 0.24 | ≥ 2 (calm pros: Cursor, Granola); 5-6 is lively |
| static frames | 80% | under ~50% (a deliberately calm hook may push it up) |
| longest hold | 4.8 s | under 1.5 s, except the end card, which should hold |
| audio | none | 18 of 20 top videos have music; loudness -14 LUFS |

Typing at small size reads as "static" to the metric but not to the eye; do not chase the number
past what a viewer would feel.

## Ranked techniques
1. **Sound.** One licensed track with a clear pulse (116-124 BPM), every state change on the beat
   grid, and quiet SFX on real UI events (key tick, click, pop, whoosh, ding, one hit on the payoff).
   Duck the music ~4 dB under typing runs so ticks carry. Master to -14 LUFS / -1 dBTP. Must still
   work muted: every beat also has on-screen type. Taste matters: "inspiring corporate" stock reads
   as an old video; minimal house / UK garage / minimal techno read as 2026.
2. **The product does something.** Rebuild the key screens as components and animate their real
   states: a prompt typing, a tool call chip, lines streaming, a counter ticking, a graph walked
   step by step, a line writing itself, rows arriving. A panned screenshot proves less than a
   rebuilt screen that moves; keep one real screenshot as a 1 s "receipt".
3. **Always moving, one mover at a time.** No still shot over ~1.5 s: a slow push-in (1.00 to 1.05)
   during holds. But never two independent movers at once, and never a headline arriving while
   the stage moves fast.
4. **The hook.** Frame 0 is the thumbnail and must be complete as a still. One sentence, one object,
   the headline as the brightest element, at most ~7 new words per second, one motion vector.
   Diagnose chaos by counting: objects on screen, moving words, repeats, speed (text over ~300 px/s
   is unreadable), bright area. A conveyor of 16 chips in 4 accelerating lanes failed every count.
5. **One recurring device.** Pick one object that means the product's unit (here: a square is a
   person). Open on it (128 dark squares, "0 written to"), go *through* it (zoom into one square
   that becomes the next scene's canvas), pay off on it (36 turn the accent color). Hook and payoff
   then rhyme.
6. **A mascot, if the brand has one, is the agent doing the work**: it looks at the prompt, hops on
   send, walks the workflow, reacts to the result. Real sprite cells only, never redrawn.
7. **Words on the beat.** Headlines arrive word by word on 8th or quarter notes; counters flip on
   downbeats. Big type (≈7-8% of frame height on 1x1).
8. **Zoom-through transitions** in a full-frame layer (not clipped to the stage), with the object
   blending into the next scene's background color (blend in OKLCH to avoid muddy mid-tones).
9. **The climax inside the tool the viewer already uses** (e.g. the chat window answering "how is it
   doing?" with the real numbers), then the CTA.
10. **A looping end card**: the last 0.5 s resolves into frame 0 exactly (verify with a pixel diff).
11. **Pain-first hook over result-first**: a result number in frame 0 is a strong thumbnail but
    spends the payoff early. Put the number in the middle, where it is proof.

## Camera and easing
- Arrivals: the brand's ease (a strong ease-out), 240 ms, 4 px fade-up.
- Camera moves and morphs: an in-out curve (e.g. `bezier(0.45, 0, 0.55, 1)`). A strong ease-out on
  a long pan puts ~68% of the travel in the first 20% of the time: a whip, then a freeze.
- Prefer holds joined by short moves over one long move.

## Type and layout
- 1x1 is the master: headline zone on top, stage below, lockup in a fixed corner.
- 16x9: headline column left (~660-720 px), stage right; set explicit line breaks so no line ends
  with one orphan word.
- Legibility on a phone: UI text lands at ≥ ~24 px in the 1080 frame; rebuilt components are
  designed small and scaled up, or text is enlarged, until it does.

## Copy
- Specific, checkable, the number carries its base ("36 of 128 invited").
- Name the reader's pain in their own words (the ICP's quote), then show the product answering it.
- Truth-check each line against the data (SKILL.md, honesty rule 8).
