# Adding a mascot

A mascot earns its place by doing a job the UI can't: pointing the eye, reacting to what just happened, giving the page a face. If it only decorates, cut it. Kairon's mascot ("Robotito") started in every section and ended only in the fold, after a review found the other renders decorated without explaining.

## Two kinds of art

**1. The interactive bust (sprite sheets).** A small head that turns and reacts. Built on [page-mascot](https://github.com/nilbuild/page-mascot) by Kamran Ahmed (MIT; keep its license header in the adapted file). It needs two images:

- **Directions sheet:** a 3x3 grid of the head looking up-left, up, up-right, left, center, right, down-left, down, down-right.
- **Reactions sheet:** a 3x3 grid of expressions. Kairon's: blink, heart, linkedin, surprised, starstruck, bashful, email, dizzy, delighted.

Same framing, same scale and same anchor point in every cell, so switching cells never makes the head jump. With `background-size: 300%` each cell is a clean 0/50/100% step on both axes. Export as WEBP.

**2. Scene renders.** Full illustrations of the character doing something (at the desk, at an event booth, on a call, celebrating). If you commission them, from a 3D artist or an image model, give them the brief below, or they come back as portraits you can only place next to the text.

## What the component does

Adapt page-mascot so the page, not only the pointer, can drive it:

- `look`: where the head points while the pointer is idle (the part of the demo that is happening).
- `mood`: an expression held while a beat of the demo lasts, then back to neutral.
- The pointer wins when it moves, but only while it is over a chosen element (Kairon: the product window), so nothing moves near the CTA. After a moment of stillness the head goes back to `look`.
- A click "boops" it (squash and bounce, per-keyframe easing so the bounce isn't front-loaded).
- A decorative mode: same box and layers, never focusable, clickable or announced.
- Direction from the pointer: nearest 45° sector, a dead zone near the centre, and hysteresis so it doesn't flicker on a sector edge.
- `prefers-reduced-motion`: no ducking, no timed expressions.

Test it: direction math, the dead zone, the hysteresis, and that the decorative mode is not focusable.

## Kairon's fold pattern: the bust peeking over the product

The bust sits **behind** the product window, so only its head shows above the window's top edge (the edge cuts it at the collar). It looks down into the demo.

- **One motion event per chapter.** When the demo moves to a new chapter, the head ducks behind the edge, moves over that chapter's tab and comes back up.
- **One expression per step, timed.** A list appears: surprised (0.7 s). A message is drafted: heart (1.1 s). The campaign goes live: the LinkedIn badge (1.6 s).
- **It says nothing.** The words belong to the product and to the headline. On a phone the window's own caption row carries the story.
- **At the end it turns toward the trial button.** The last thing it does is point the eye at the one action.
- **Measure positions from the product window,** never from the band around it, or another element in the band pushes the head off the edge at one width and not at another. Re-measure on resize and on every step.

## Reuse its visual language

Anything else in the mascot's band should look like it belongs to the character. Kairon's label over the window's thread title is a die-cut sticker drawn like the badges on the reactions sheet (white panel, thick black outline, white keyline), one size up, with a spike instead of a speech lobe, so it reads as a label on the control rather than the mascot talking. It uses neutrals only: the surface's one accent color belongs to the CTA.

## Render brief (for scene art)

Kairon's first set failed because every render was composed as a portrait: character centered, whole scene visible, square frame. The one that worked bled edge to edge with an empty, dark left third where the headline could sit. The brief that came out of it:

1. **Wide, not square.** 16:9, at least 3200 x 1800 px. A square forces a column; a 16:9 can be the background.
2. **One empty third, always on the same side.** The left 35% has nothing that matters (background, wall, shadow, blur); the character and the action live in the right 65%. Ask for mirrored versions for rows that alternate sides.
3. **Measured background luminance.** The render must melt into the page band behind it. Give targets in OKLCH lightness of the background (not the character): Kairon used 0.95–0.97 for light bands, 0.17–0.22 for dark bands, 0.10–0.14 for the darkest. No strong light source in the empty third: one sunset window lifted a render from 0.12 to 0.44.
4. **Zero legible text, zero other brands.** Text in one language looks wrong on the other language's page, and generated text comes out warped. Remove third-party logos from clothes and props; use your own mark. Suggest interfaces with shapes and color only.
5. **Same lens in every render.** One camera height (chest height), one lens (about 50 mm, no wide-angle distortion), the same depth of field. Otherwise the set reads as unrelated stock images.

Also ask for: one full-body "stand" pose with a transparent background and no shadow; uncompressed PNG or WEBP originals (you do the crops, compression and masks yourself); and a table of what each render shows and which band it sits on.

## Where the mascot does NOT go

- On a block whose job is a number or a proof. The number carries it.
- Next to the product UI and an accent-colored surface at the same time: one or the other.
- Anywhere it would be the second accent on a surface.
- In the words: it never speaks the value proposition.
