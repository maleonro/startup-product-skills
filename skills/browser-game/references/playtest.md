# The version loop (step 7)

Each version answers one question, such as "do they understand the story?" or "do they get past
room 3?". The loop: evidence, a PRD, a judge and a synthetic player, the build in parallel, the same
measures before and after, and the owner plays.

## Evidence, strongest first

1. **Real players.** Watch them, or read what they send. One outside player wrote "I didn't
   understand what the goal was" after reading the whole intro. Analytics showed every dialogue
   read to its last line: people pass the text, but it does not stick.
2. **Analytics** on the live game (see [launch.md](launch.md)). Get the base rate before you call
   something broken: with 12 visitors a week, one odd session is not a pattern.
3. **A synthetic player** (below).
4. **The design judge** ([judge.md](judge.md)).
5. **Theory**, as lenses to look through, never as proof.

Tag every claim in every report: `[player]`, `[owner]`, `[analytics]`, `[script]`, `[synthetic]`,
`[theory]`, `[code]`, `[played]` (seen in a bot run, with a photo) or `[opinion]`.

## The theory file

Write `ref/theory.md` once and give each playtest agent its part. The first game's:

- **Part 0, for everyone:** the game and its player; the bar (Poki: plays over 3 minutes); Schell's
  interest curve (a hook early, rising peaks and valleys, a climax; fractal: game, floor, room);
  how to propose a change (the smallest change that tests the idea, one variable at a time, the
  biggest risk first, done = played and measured); the limits, ethics included (Nir Eyal's
  manipulation matrix: no streaks, no daily rewards, no email before the score).
- **Part A, arriving and learning** (link to room 6): Celia Hodent, *The Gamer's Brain*:
  players see what they expect, do not read during action, forget fast, and learn by doing at the
  moment they need it. Schell's lenses of goals and curiosity. Eyal's trigger and action: does the
  game keep the promise of the link, and how many seconds until the fun?
- **Part B, feel and finish** (room 7 to the end, music): Steve Swink, *Game Feel* (is moving fun
  with no goal?); Schell on challenge, flow, reward, punishment, meaningful choices, juiciness and
  the climax; Winifred Phillips on music in layers; Eyal's variable reward and investment; the
  Wordle share grid (90 players on 1 Nov 2021, over 300,000 on 2 Jan 2022; the grid came on
  16 Dec).

Each part ends with questions the agent answers while playing, such as "how many seconds from the
first tap to the first move?" and "what does someone see who opens the link with the phone
upright?".

## Playtest agents

Two agents, one per part, play the local build with a bot through the debug hooks. They only
report; they do not touch `src/`. Each returns up to 8 improvements, ranked by how many players
each one saves: the problem with its evidence and a photo, the lens that shows it, the smallest
change, effort and risk, and how we will know it worked. Plus the interest curve of its stretch,
0-10.

## The synthetic player

A fresh agent with a persona from the real audience (a founder from another country in the same
language). It reads the script extracted from the code, never a summary, and photos of each moment.
At 4 checkpoints (after the intro, at room 4, mid-game, after the end) it answers:

1. Who am I? 2. What is the goal? 3. How am I doing? 4. What did I learn? 5. How much do I want to
go on, 0-10?

It marks each answer `[sure]` (read with the game paused) or `[guess]`, lists every line it did not
understand (the exact line, where, why), says where it would quit, and names the 3 changes that
would help most. **Never reuse a synthetic player:** it remembers. Use its answers as a done
condition: the first game's story pass required naming the product and the customer in 3 of 4
checkpoints; it started at 1 of 4.

## The PRD

One file per version in `ref/`, answer first:

- **The answer** in 1-2 sentences, then **1 to 3 actions** that do not overlap.
- Each action: **what we do**, with the exact new texts, and **why**, each fact with its tag.
- **Done:** the condition the build must meet (tests, the synthetic player's score).
- **Listen, not target:** what to ask 3 real people ("what were you selling, and to whom?").
- **One metric:** today, a ceiling, a floor, and when it can be read (at how many players).
- **Out of scope**, with why. **How we build:** branch, agents, files, word budget. **Risks.**

Then a judge stands in for the owner (a strong model playing the owner, max 3 rounds). On the first
game it said "approved with changes, 6/10", and its fixes went in. If it does not approve, the real
owner decides.

## What the first game learned about story and teaching

- **Say what you sell and to whom in the first lines.** The synthetic player could not tell if it
  received the messages or sold the tool that answers them.
- **One goal line, always on screen.** A reminder in place beats an explanation at the start.
- **Explain an idea just before you ask for it.** A player failed a question twice, about 8 seconds
  each, with the definition written in it; the dialogue that explained it rang 46 seconds later.
- **Say how they did after each room**, in one line for 2 seconds at the door, never while they
  walk. A rank says its place: "Saturated Inbox, 6 of 7; the best is Ghost Prospect".
- **Dialogues that freeze the first rooms make people leave.** Move them to a strip over the game.
- **Inside jokes and local slang** read as "not for me" to players from elsewhere. Keep the voice;
  cut what needs a footnote.
