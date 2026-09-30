# Writing shots that render

Read this before filling the `shots` of a plan. The compiler (`scripts/lib/compile.py`) turns the fields
into the final prompt; your job is the content of each field.

Adapted in part from Serge Shima's visual-skills (github.com/smixs/visual-skills, CC BY 4.0: the Details
Law, one camera move, the final-image rule, identity repetition) and from Google's Omni prompting guide
(single-take clause, simple negatives, edit phrasing, timing syntax).

## Contents
1. The fields, in the order the model weighs them
2. The Details Law (validator R9)
3. Camera and lens (R11)
4. Light, style, palette
5. Sound (R12)
6. Dialogue (R14)
7. Text on screen (R15)
8. Identity and continuity (R16)
9. Internal timing with beats
10. Words that do not render (R10)
11. Worked example

## 1. The fields, in the order the model weighs them

Early tokens carry more weight, so the compiler leads with `subject` + `action`, then identity, setting
and details, then camera, light and style, then the final image, sound, and negatives.

- `subject`: the visible thing with 2-3 concrete traits. "A hand", "The green Nativa can on the desk".
- `action`: ONE verb phrase whose grammatical subject is `subject`, so "subject action" reads as a
  sentence: "lets her head drop toward the keyboard, then snaps it back up". One beat per shot.
- `setting`: where, when, with what in frame.
- `final_image`: the exact frame the shot ends on. It is the cut point and the model's destination.

Write every prompt field in English, even for a Spanish ad (R13). The ad's language lives in `supers`,
the end card and any voiceover.

## 2. The Details Law (R9)

Every shot owns three concrete physical details. A shot without them is filler and renders as mush:

1. `details.environment`: an environmental pressure (steam, rain on glass, blinds striping the desk).
2. `details.micro_action`: a body or object micro-action (fingers go limp, a droplet runs down the label).
3. `details.motif`: a sound or visual motif (the tss of the can, the clock at 3:00).

Emotions do not render; bodies do. "She is exhausted" -> "her head drops, eyelids flutter, fingers go
limp". Two to four observable cues per emotional change; more reads as overacting.

Consequence prompting: describe what the action causes ("the tab cracks and mist curls out"), not only
the action. A broken cause-effect chain is also an easy QC tell.

## 3. Camera and lens (R11)

One primary move per shot (push-in, pull-back, pan, tracking, static). A subtle secondary (slight
handheld) is fine; three moves in 4 seconds is chaos. State shot size and lens: 24mm wide, 35mm
documentary, 50mm human, 85mm portrait, 100mm macro for texture and product detail. Put a plan-wide lens
in `style.lens` and override per shot in `camera`.

Motivate the camera: a push-in when something matters, static when the action should read, a pull-back
to reveal context.

## 4. Light, style, palette

`light` per shot, `style.look` and `style.palette` once for the whole plan (repeated by the compiler in
every prompt, so separate generations match). Light carries the story too: cool, flat light in the
problem shot, warm side light after the product arrives.

## 5. Sound (R12)

Omni generates audio. Without direction it invents a generic score. Direct it:
- `audio`: named foreground sounds ("sharp can-opening hiss", "keyboard clicks on the beat").
- `style.audio_bed`: the music for the whole ad; `music` on a shot replaces it ("no music").
- If you will mix a recorded voiceover or licensed track in assembly, direct sparse SFX with no music,
  so the mix stays clean.

## 6. Dialogue (R14)

Put spoken lines in `dialogue` with a `speaker` from `characters` and a `delivery` ("muttering",
"whispers, trying not to laugh"). Keep lines at 4-10 words, max ~2.5 words per second of shot. Spanish or
other non-English speech is not evaluated by Google: test it in draft, or record a voiceover and mix it with
`assemble.py --voiceover`. Lock the camera on speaking shots.

## 7. Text on screen (R15)

Two channels:
- `supers` (default): exact copy overlaid in assembly, any language, inside each placement's safe area.
  The compiler tells Omni to leave negative space where the super goes and to render no text itself.
- `native_text`: text the model renders inside the scene (a sign, a label) as part of the image. English
  only, short, quoted exactly: `A neon sign above the bar reads "OPEN LATE"`. Blocked for non-English ads.

## 8. Identity and continuity (R16)

Omni has no memory between separate generations. For anyone who appears in more than one shot:
- Define them once in `characters` with a full `identity` block (face shape, skin, hair, facial hair,
  exact wardrobe, accessories). The compiler repeats it in every shot that lists the character.
- Strongest lock: continue the take with `extend` (same generation context).
- Next best: a reference still in `ref_image`, passed in each shot's `image_refs` with a label.
- In the EEA/UK a reference photo of a real, recognizable person is blocked (R8). Use a generated person.
- No photo of anyone (the common case: the user sends only a product shot): keep the person inside one
  extend chain; in other segments show only hands, a silhouette or the back of the head; or generate a
  first shot of the person, approve it, and use a frame from it as the `ref_image` for later shots.

For the product: a real photo as `first_frame` keeps the pack exact; `image_refs` with label "the
product" is looser but lets the scene move freely.

## 9. Internal timing with beats

For a 5-10 s shot with more than one beat, add `beats`: `[{"t": "0-2s", "what": "..."}, ...]`. They
compile to Omni's timecode syntax (`[0-2s] ...`). In an extension, 0s is the start of the new part.
Keep one change of state per beat, and keep `single_take: true` unless you want the model to cut.

## 10. Words that do not render (R10)

cinematic, stunning, masterpiece, epic, high quality, 4k, beautiful, amazing, professional, powerful,
intense, dynamic camera. Replace each with a physical fact: not "beautiful light", but "low sun through
blinds throws stripes across the desk".

## 11. Worked example

Weak: `subject: "woman tired at work"`, `action: "she is exhausted"`, `camera: "cinematic"`.

Strong:
```json
{"subject": "The woman at her open-plan office desk",
 "action": "lets her head drop slowly toward the keyboard, then snaps it back up, eyelids fluttering",
 "details": {"environment": "flat grey afternoon light through blinds stripes the desk",
             "micro_action": "her fingers go limp on the trackpad",
             "motif": "the wall clock behind her reads 3:00"},
 "camera": "static medium close-up at eye level",
 "light": "cool overcast window light, slightly underexposed",
 "audio": "muffled keyboard clatter, a long exhale, air-conditioning hum", "music": "no music",
 "final_image": "her eyes snapping wide open, startled"}
```
