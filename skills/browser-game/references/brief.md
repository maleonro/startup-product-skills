# Brief and research (steps 1-2)

The brief is one page. Write it before any code, and get the owner's yes on it.

## The five lines

1. **Essential experience, in one sentence** (Jesse Schell's lens). The first game: "you are the
   founder who reaches the CEO slowly, by reading and by signals, and laughs at the stack of tools
   you pay for." Every later decision is judged against this line.
2. **The player.** Where they come from, on what device, with how much time. The first game: a link
   from a colleague in WhatsApp or LinkedIn, almost always on a phone, two free minutes, one play.
3. **The owner's goal.** For a branded game: that people finish, share, and remember one idea.
   Score what the owner values, never activity. The first game scored positive replies, never
   messages sent.
4. **The legal lines** (below).
5. **The bar.** Poki's player fit test is a good default for a web game: the average play lasts
   over 3 minutes and 25% of plays last over 3 minutes. A strong game averages over 5. Poki also
   advises skipping title screens, teaching with pictures and not killing the player early.

## Confirm the reference with a picture

If the owner names a classic, get a screenshot of the exact look before any code. The first brief
said "like Metal Gear". The team started a 2D game after the 1987 original. The owner meant the 1998
3D one. The brief got 7 additions before the look was settled. One screenshot on day 1 would have
saved most of them.

## A branded game: map each idea to a mechanic

Each idea the game teaches is the tool that gets the player through a room. The first game:

| Product idea | In the game |
|---|---|
| Platform limits punish volume | Guards see you when you run, not when you walk |
| A reason to write today (a signal) | The keycard that opens the next lift |
| Reading the profile first | You become invisible to the CEO's security |
| A stack of tools at its monthly price | The boss: a machine made of those tools, price tag on it |
| Account health | Your life bar |

Name things by their category ("emails in bulk", "contact data"), never with a parody brand. The
first game's parody tool names made the owner want to buy the parodies.

## Legal lines

- **Mechanics, structure and feel can be recreated. Code, art, music, sound, text, names and logos
  cannot.** The first owner asked to port a classic; the agent declined and recreated it instead.
  A title close to the classic's is a small risk: say so, and let the owner decide.
- **Decompilations only in a clean room.** One agent reads the public decompilation and writes the
  techniques in prose (camera angles, timings, how vision cones work). Another agent builds from
  that note and never sees the code.
- **Third-party assets:** CC0 first (Kenney, Quaternius, Poly Haven). No runtime GPL code. A repo
  with no license is not usable. `CREDITS.md` lists every library and asset with its license.
- **Screenshots of other games are look references only.** They live in `ref/`, never in the build:
  `scripts/check-dist.mjs` fails the build if one ships, even renamed.
- **Real people and brands** in easter eggs need their OK. Ask the owner to get it.

## The cheatsheet (step 2)

Before code, one agent researches the genre and writes `ref/cheatsheet.md`: only tips with a source,
each with its link, and a "not verified" list at the end. The first game's cheatsheet, all from
public sources, held these:

- **Fixed timestep with an accumulator** (Glenn Fiedler, "Fix your timestep"), and the game loop
  pattern (Robert Nystrom, *Game Programming Patterns*).
- **One mechanic per pull request**, in the order movement, dangers, score, polish. A huge PR broke
  staging for a developer who then shipped 1,700 small ones.
- **Juice**, in moderation (Jonasson and Purho, "Juice it or lose it"; Jan Willem Nijman, "The art
  of screenshake"). Juice that fights the art style breaks it.
- **Stealth:** a cone plus a peripheral zone and a small rear zone, raycast for cover, an awareness
  meter that fills slower with distance (Game Maker's Toolkit, "School of Stealth"); three guard
  states with a visible timer; show sound rings before the player acts (*Mark of the Ninja*).
- **Drive the game from a test:** `window.render_game_to_text()` and `window.advanceTime(ms)`, so a
  browser test can play, photograph and read state. See [build.md](build.md).
- **Prewarm the first frame:** shaders compile on first draw, so draw one real frame behind the
  loading screen. One developer measured the first frames go from about 60 ms to under 1 ms.
- **Object pools** for bullets and particles; nothing allocated in the update loop.

## Brief template

```markdown
# Brief: <game>
Essential experience: <one sentence>
Player: <where from>, <device>, <time>, <plays once or returns>
Owner's goal: <finish / share / remember X>. Score = <what the owner values>
Reference: <game or era> + screenshot in ref/. Mechanics only, no assets.
Idea -> mechanic map: <table, branded games only>
Bar: average play > 3 min, 25% of plays > 3 min
Out of scope for v1: <list>
```
