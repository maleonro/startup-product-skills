# Build (steps 3-4)

You cannot play the game, feel the controls or hear the music. So the game must be drivable by a
script, and every claim must be a test, a number or a photo of the real build.

## Core first, renderer second

Put the rules in `src/core/`, with no renderer dependency: level data, guard or enemy state
machines, vision, movement rules, items, dialogue scripts, the game state machine up to the ending,
and a deterministic `step(dtMs)`. Unit tests prove the game can be finished from start to end.

The first game's look changed from 2D to 3D after the core existed. The rules survived because no
rule knew how it was drawn. A static `dist/` that runs from any static server is the target (Vite
plus TypeScript worked; three.js for 3D).

## The debug hooks

Expose these on `window` from the first build. Every test, playtest bot, photo and trailer shot
uses them.

| Hook | What it does |
|---|---|
| `advanceTime(ms)` | Steps the game deterministically and draws a frame. Tests never sleep. |
| `render_game_to_text()` | The whole state as JSON: room, actors, mode, objective, timers. |
| `__GAME.view()`, `events()` | Read state; read the event log since the last call. |
| `__GAME.press(a)`, `hold({...})` | Input through the same path as the keyboard. |
| `__GAME.warpTo(room)`, `give(item)`, `ghost(on)` | Set up a scene. Never used in "by hand" tests. |
| `__GAME.debugWin()` | The autopilot plays the real rules to the ending, enemies active. |
| `__GAME.camera()`, `project(points)` | Where things are on screen, through the renderer's own camera. |
| `__GAME.footprints(boxes)` | Redraws the frame with each actor hidden and counts its pixels under the HUD boxes. |
| `__GAME_READY` | True after fonts, shader prewarm and the first frame. |

Add URL flags to compare variants without a rebuild: `?cam=far`, `?look=old`, `?analytics=1`.

## The tests that earn their place

1. **The autopilot finishes the game** with enemies active, and a "ghost" run proves the route
   exists. After one tuning pass, the autopilot ran out of time in one room: the test caught the
   balance problem before any person did.
2. **A first-timer by hand:** real key events only, walking only, no warp, no autopilot. The route
   is computed from the level data. It must reach room 4 within N attempts, read every call, and
   never see an enemy hidden under the HUD.
3. **The pauses pause:** while a dialogue is open, nothing in the world moves.
4. **Touch:** a tap starts the game, the stick moves the player, the close button closes.
5. **Photos of the real build**, taken only when the camera has settled, with checks on what the
   renderer drew. Open them and look. "Compiled but invisible" passes every other test.

Run all four checks before each hand-off: type check, unit tests, build, browser tests. Write a
"Fix pass N" section in the README: what changed, and what was NOT verified (the first game's audio
was listed as "nobody has heard it").

## Measure what the player would feel

Pick the measures before the change and run the same bot before and after. The first game's
"arrival" pass, measured with one bot on the old and new build:

| Measure | Before | After |
|---|---|---|
| Taps to reach room 4 | 17 | 11 |
| Dialogues that freeze the game before room 4 | 4 | 2 |
| Texts on screen at the first control | 8 | 5 |
| Seconds frozen by dialogues up to room 6 | 4.1 | 2.7 |

Other useful ones: seconds to the first control and to the first moment of tension, the player's
height as a share of the screen, input-to-response time (under ~100 ms feels instant), and the
number of texts on screen at once.

## Phone

- Render width from the screen size; full screen in landscape; a floating stick on the left and
  the actions in an arc on the right.
- Draw the button icons as glyphs of the game's font, so every text shows the button on touch and
  the key on a keyboard. No text on touch names a key.
- The portrait screen sells the game: logo, name, the goal in one line, a rotating phone, and "no
  rotation? turn off the rotation lock". A tap asks for full screen. Count how many see it.
- Keep the main bundle small. The first game's grew from 300 to 416 KB gzip when 3D models went in
  as JSON: load them lazily.

## Agents in parallel

- One worktree and branch per agent, with **disjoint files**. Write the contract between them first
  (for example the pose type the core gives the renderer). On the first game, merges only clashed
  in the README and the photos.
- Each agent gets a closed brief: the files it owns, its ports (dev and browser tests), the checks,
  what "done" means, and a spend cap if it can spend.
- **Ports:** each agent has its own; nobody touches the port the owner plays on. Serve on
  127.0.0.1, never on all interfaces.
- Agents test the local build. They never open the live game.
- **The bill is re-reading context.** On the first game, 97% of 1,444 M tokens were context read
  again; output was 9 M. What you re-read is what you pay: keep briefs closed and sessions short.
