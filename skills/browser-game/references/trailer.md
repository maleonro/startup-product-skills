# Trailer (step 9)

A 30-45 second trailer cut from the game itself, to the beat of one famous piece of music. The
first one ran 40 seconds and was judged 6, 7, then 8/10 over three rounds.

## Capture from the game, not from a screen recorder

The debug hooks make every shot repeatable. One script per scene (`trailer/capture/scene-*.mjs`)
opens the local build in a headless browser, sets the scene, and steps time frame by frame:

```js
const s = await open();                       // local build, fixed viewport, analytics off
await s.toControl();                          // past the title and the intro
await s.warp('lobby', ['weapon']);            // room + items, through __GAME.warpTo / give
await s.ev(() => window.__GAME.ghost(true));  // enemies blind while you frame the shot
await s.at(7, 2.4, -Math.PI / 2);             // place and turn the hero
s.start('shoot');                             // frames go to frames/shoot/0001.jpg ...
await s.play(1.2);                            // advanceTime(1000/30) + screenshot, 36 times
await s.press('use');                         // the action, through the real input path
await s.play(2.0);
```

Show the verbs the player will use. The first owner asked for exactly that: put a guard to sleep,
shoot, the joke hat you get for losing twice. "Everything on the grill."

## Music: famous, and free to use

Two rights are separate: **the composition** and **the recording**.

- The composition must be in the public domain **in every country you publish to**. Sibelius'
  *Finlandia* is free in the US and protected in Argentina and the EU until the end of 2027.
  Orff's *O Fortuna* is protected until 2052. Check each one.
- The recording needs its own free license. Wikimedia Commons has full orchestral recordings under
  CC BY. CC BY means a credit on screen and in `CREDITS.md`: title, composer, performer, license,
  source URL and what you changed.
- Try the edit on two or three pieces before polishing one. The first try (*Ride of the
  Valkyries*) did not fit the cuts; the second (*Russian Dance* from *The Nutcracker*, about 146
  BPM) did, and the owner loved it.

## Cut to a beat grid

- Write the beats to a JSON file and build every shot on it: a shot lasts N beats and starts on a
  beat. At 146 BPM and 30 fps a beat is about 12.3 frames.
- **Readable text, frantic image.** The image may cut on every beat. A caption stays still for at
  least 0.3 s per word plus 0.8 s. A check script fails the build if a caption is shorter or a cut
  falls off the grid.
- Captions in the game's own font, few words each, with a shadow. Check the font has every glyph
  you use (the first one had no « »).
- End on the piece's real final chord. X loops video: over the last 2 seconds, fade in the music
  that comes just before your excerpt, so the loop back to frame 0 has no silence.
- Master to -16 LUFS with the true peak at or below -1 dBFS. Export a main file and a small one.

## Judge it with evidence

You cannot watch it. Build the evidence, then give it to a design judge (the `landing-page`
skill's Juan is one) until 8/10:

- frames decoded to images, and a contact sheet of every 4th frame per scene;
- a strip of the frames on each side of every cut;
- a timeline of the audio level, the beats and the cuts.

Each round, list what changed as claims to verify, and give the judge its previous verdict. The
first trailer's last fix was a single frame: two shots moved one frame later.

Keep only the latest version in the shared drive. Delete the old ones when the owner approves.
