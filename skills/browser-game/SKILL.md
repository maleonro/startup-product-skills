---
name: browser-game
description: Builds a short browser game (any genre, 5-15 minutes, phone first) from brief to launch with coding agents - a one-line essential experience, a sourced cheatsheet, an engine-agnostic core that a script can drive and finish, a renderer with keyboard and touch, generated art under a cost cap, playtests by real people, a synthetic player and a game-design judge, a measured version loop, a funnel in analytics, a static deploy, a share card, and a trailer cut from the game itself - with the rules learned on the first one. Use when the user wants to make a web or browser game, a branded or marketing game, a playable prototype, a game "like" a classic, to playtest or improve a game so people finish it, or to launch, measure or make a trailer for one.
---

# Browser game

The bar: a stranger who opens a link on their phone understands the goal in the first minute,
plays past the first 3 minutes, finishes, and shares how they did. The first game made this way (a
PS1-style stealth game for a B2B startup) went from brief to version 23 in about 4.5 days. Every
rule here is a correction its owner had to make on it.

## Hard rules

1. **Mechanics yes, assets no.** Recreate how a classic plays, never its code, art, music, text,
   names or logos. Read a public decompilation only in a clean room: one agent writes the techniques
   in prose, another builds from that note. References stay out of the build (`scripts/check-dist.mjs`).
2. **The agent cannot play: it drives and measures.** The game has a deterministic step, a text dump
   of its state and debug hooks, and a script finishes it. Every claim is a test, a number or a photo
   of the real build. See [references/build.md](references/build.md).
3. **The phone is the main device, and it opens in portrait.** 6 of 6 phones in the first funnel
   opened upright. Landscape, touch controls and a portrait screen that sells the game are day-1 work.
4. **Plain words, explained just before they are needed.** Nobody reads while moving. No analogies
   and no parody brands: the owner played and wanted to buy the parodies instead of the real
   product. The goal stays on screen.
5. **Money, publishing and the owner's data stay with the owner.** Quote generated art and get an OK
   on the number. The owner runs the deploy and DNS. Agents never open the live game: their visits
   pollute the funnel.
6. **The strongest model directs, cheaper ones execute** (Claude Opus and Sonnet on the first game):
   worktrees with disjoint files, a written contract between them, one port each, never the owner's
   port. At most 2 long agents at once. You review every diff and every photo.

## Workflow

Copy this checklist into your reply and tick it off. Every step marked `$` can spend money: quote
it, then get the owner's OK on that number (rule 5).

```
- [ ] 1. Brief: essential experience in one sentence, the player and their device, the owner's
         goal, the legal lines, the bar                                               (brief.md)
- [ ] 2. Research before code: a sourced cheatsheet for the genre; a clean-room note if a
         classic is the model                                                          (brief.md)
- [ ] 3. Engine-agnostic core: deterministic step, debug hooks, an autopilot that finishes it  (build.md)
- [ ] 4. Renderer and controls: keyboard and touch, landscape phone, prewarmed first frame (build.md)
- [ ] 5. $ Look: one reference era, an audit of defects with photos, generated assets under a cap
                                                                                         (art.md)
- [ ] 6. Analytics funnel and a private build the owner plays; 3 real people play     (launch.md)
- [ ] 7. Version loop: PRD with sources -> design judge + synthetic player -> build in parallel
         -> measure before/after -> the owner plays                   (playtest.md, judge.md)
- [ ] 8. Launch: the owner deploys; share card; a result grid to share                (launch.md)
- [ ] 9. Trailer cut from the game itself, to the beat, judged until 8/10             (trailer.md)
- [ ] 10. Read the funnel 48 h after each push of traffic; the next PRD starts there  (launch.md)
```

Read each reference at the step that needs it: [brief.md](references/brief.md) (1-2),
[build.md](references/build.md) (3-4), [art.md](references/art.md) (5),
[playtest.md](references/playtest.md) and [judge.md](references/judge.md) (7),
[launch.md](references/launch.md) (6, 8, 10), [trailer.md](references/trailer.md) (9).

## If you did it again

The launch post of the first game listed four things to do differently, after 23 versions:

- **3 people play before the code.** A real player failed a question twice with its definition on
  screen. Watching that on day 1 would have changed the first plan.
- **Landscape phone from day 1.** Full-screen landscape and touch controls came in version 16.
- **Runs of 5 minutes.** A full run took about 10. An outside player quit at minute 17, in room 9
  of 12.
- **Zero analogies.** Say what it is.

## The project folder

`<game>/`: `src/core/` (rules, no renderer), `src/render/`, `tests/` and `tests/e2e/`, `tools/`
(autopilot, photo scripts, playtest bots), `ref/` (references, research, PRDs, playtest reports;
never shipped), `art-src/` (raw generated art; never shipped), `share/` (the share card),
`trailer/`, `README.md` (how to run, the debug hooks, one "Fix pass N" section per pass) and
`HANDOFF.md` (state and next step, for the next session).

**Make it a git repo on the first day and push after every pass.** Keep each version the owner
played (`dist-v<n>/`) so you can go back to it.

## Working with the owner

- The owner plays a local build on a fixed port. Tell them the version and what changed.
- Taste calls go as photos of the real game, never as a sketch or ASCII. The first owner approved a
  button layout from one photo and could not judge it from a drawing.
- Send photos and videos through a drive (rclone or similar), not attachments to a chat or mail tool.
- One question at a time. Merge only on an explicit "merge"; deploy only when the owner runs it.

## Related

Skills from the same repo (`maleonro/startup-product-skills`); install the ones you use.

- `landing-page`: `JUAN.md` and `JUAN-PROMPT.md`, the design judge used on the trailer. Optional.
- `product-launch-video`: Remotion and the motion measures. Optional, for step 9.
- `build-feature` and `review-loop`: the PR discipline, if the game lives in a product repo.
