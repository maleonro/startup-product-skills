# explainer-video

A [Claude Code](https://claude.com/claude-code) skill that builds an educational explainer video in
the style of [Kurzgesagt – In a Nutshell](https://kurzgesagt.org): about 8-10 minutes, paper-collage
art, a calm voice, and one idea the viewer can retell the next day. It works for any topic and any
language.

It is not an ad maker. A company can make the video, but its product appears once, in a closing
block like Kurzgesagt's sponsor segment. Every number on screen comes from a sources sheet that was
checked against the original papers.

## Example

[![The first video made with this skill](examples/first-video-thumbnail.jpg)](https://youtu.be/pio_TsNUXNQ)

[Prospección de clientes en LinkedIn: a quién escribirle y cuántas veces insistir](https://youtu.be/pio_TsNUXNQ)
(8:51, Spanish), made for [Kairon](https://heykairon.com) in three days in October 2026 (click to
watch). It teaches who to write to and how many times to follow up, from field studies plus the
pooled data of 40 real companies. The protagonist is invented, and the video says so in the hook.
It took 11 script versions and 4 cuts. Every rule in the skill is a correction made on this video:

| | First cut | Final |
|---|---|---|
| Length | 9:35 | 8:51, same voice and same images |
| Silence at a chapter join | 4.1-6.8 s | 1.6 s |
| Frozen frames | 46.7 % | 1.9 % |
| Design judge's score | 5/10 | 7/10 (the owner approved it there) |

## The thesis

A good explainer is a good script, with pictures that show the mechanism. Four things made the
first one work, and each one came from a mistake:

- **The study scene comes first.** The video opens with a real experiment told as a scene, with a
  bet for the viewer ("how many do you think replied?"). Each chapter opens the same way. Early
  drafts brought the studies in late, and the owner said: "the academic examples arrive way too
  late".
- **Trust nothing you did not read in the original.** Three viral numbers on the topic were not in
  the papers they cite. Three famous results did not hold up: one did not replicate, one was null in
  later studies, and one came from a study that Data Colada later found evidence of fraud in. Two of the company's own
  beliefs failed when measured again. The sources sheet, with its "Do not say" column, is the
  first file, not the last.
- **Pay once.** Sketch every shot at no extra cost, let the owner pick, then pay for one final per
  shot. Draw anything countable or textual in code: image models cannot count, and they misspell.
- **Measure what you cannot perceive.** The agent cannot hear the mix or watch the cut. Every audio
  and visual call is a measurement (frozen frames, silences, music level, peaks) plus the owner's
  eye and ear on 3 samples.

## What it does

1. **Sources first**: a sheet with every number the script may use and what each study does *not*
   show, checked against the paper.
2. **Script in rounds**: an editor subagent with 20 rules scores and rewrites. The rules include one
   idea per chapter, the study scene first, the 15-year-old cousin test and no selling. You check
   every new line against the sheet, because each round adds overstatements.
3. **Images at the lowest cost**:
   - Anything countable or textual is drawn in code.
   - Sketches come from what the owner already pays for: an image agent such as xAI's Grok Build
     CLI, or the images in their ChatGPT, Gemini or Grok subscription.
   - A paid API like Higgsfield is used for the masters and their edits only when the free sources
     do not pass.
4. **Voice and music**, each chosen from 3 samples. One music piece per chapter, levelled 14 dB
   under the voice, silent on the key numbers.
5. **Edit in Remotion** to measured targets: joins under 2 s, frozen frames under 15 %, burned-in
   subtitles, paper sounds inside the components.
6. **A design judge** scores contact sheets and measures, round after round, until 8/10.
7. **Publish** with the `youtube-seo` skill, after a benchmark of the most-viewed similar videos.

No paid step runs without the owner's OK on the exact cost.

## What you get

- The video, with subtitles burned in, and the same subtitles as an `.srt`.
- `sources.md`: every study and number, with what not to say, plus a sources page at the end of the
  video.
- Every script version and every editor review, so the next video starts from the rules, not from
  zero.
- The YouTube package: titles, description with chapters and sources, tags and 3 thumbnails, checked
  against YouTube's limits.

## What it costs

On the first video, the paid generation came to about 170 Higgsfield credits (roughly US$8.50 at
about US$0.05 a credit), for 55-84 images, the voice and 9 music pieces (42.30 credits of the 170). The sketches cost
no credits: they came from a subscription the owner already had. The real cost is time: 11 script
versions and 4 cuts, and a full render takes 16-20 minutes.

With your own image agent or LLM subscription for sketches and finals, and code for everything
exact, the image bill can drop close to zero. Voice and music remain.

## Requirements

- Claude Code, or another agent that runs skills and subagents. The strongest model directs; a
  cheaper one runs the long jobs.
- Node.js and [Remotion](https://www.remotion.dev) 4. Remotion is free for individuals and companies
  with up to 3 employees; larger companies need a company license.
- Python 3 with Pillow and numpy, and ffmpeg, for measures and contact sheets.
- Whisper for word times: `mlx-whisper` on Apple silicon, `openai-whisper` or `faster-whisper`
  elsewhere.
- A voice (an ElevenLabs plan, or an API that offers it) and a music source (an AI music model or a
  royalty-free library).
- Optional: an image agent or LLM subscription with images, and a paid image API. On a Mac, Apple's
  Vision framework cuts the characters out; elsewhere, use any background-removal model.

## Files

- [`SKILL.md`](SKILL.md): hard rules and the 11-step checklist.
- [`examples/first-video-thumbnail.jpg`](examples/first-video-thumbnail.jpg): the first video's
  published thumbnail, made in code from the video's own art.
- [`references/script.md`](references/script.md): the sources sheet, fact-checking, timing, the
  shape that worked, what the owner rejected.
- [`references/editor.md`](references/editor.md): the script editor's prompt and its 20 rules.
- [`references/images.md`](references/images.md): picking the image source, cost plan, sketches,
  finals, cutouts.
- [`references/sound.md`](references/sound.md): voice, word times, music, paper sounds, measuring
  audio.
- [`references/edit.md`](references/edit.md): Remotion structure, rhythm targets, visual rules,
  subtitles, review, the design judge.

## Install

```bash
npx skills add maleonro/startup-product-skills --skill explainer-video
npx skills add maleonro/startup-product-skills --skill youtube-seo
# optional: the full design-judge pattern, and Remotion notes plus a motion meter
npx skills add maleonro/startup-product-skills --skill landing-page
npx skills add maleonro/startup-product-skills --skill product-launch-video
```

Then ask Claude Code for an explainer video, "a video like Kurzgesagt", or a YouTube video that
teaches.

## Credits

- **[Kurzgesagt – In a Nutshell](https://kurzgesagt.org)** set the bar, and the editor quotes their
  published notes on their own craft. This skill is not affiliated with or endorsed by Kurzgesagt;
  their name only describes the style. Do not copy their art, characters or brand.
- **[Claude](https://claude.com)** by Anthropic made the first video in
  [Claude Code](https://claude.com/claude-code), with Claude Opus directing and Claude Sonnet
  executing, and wrote this skill from that work.
- **Research behind the editor's rules**: Richard E. Mayer's multimedia learning principles
  (coherence, segmenting, pre-training, personalization, redundancy), from *The Cambridge Handbook of
  Multimedia Learning*; Michael F. Dahlstrom, "Using narratives and storytelling to communicate
  science with nonexpert audiences", *PNAS* 2014.
- **Tools used on the first video**:
  - [Remotion](https://www.remotion.dev) for the edit. It is free for individuals and companies
    with up to 3 employees; larger companies need a [company license](https://www.remotion.dev/license).
  - [Higgsfield](https://higgsfield.ai) as one API for the finals (Google's Nano Banana Pro and
    ByteDance's Seedream), the voice and the music (the `sonilo_music` model on Higgsfield).
  - [ElevenLabs](https://elevenlabs.io) v4 for the voice.
  - [Grok](https://x.ai) by xAI, through its Grok Build CLI, for the sketches.
  - [Whisper](https://github.com/openai/whisper) by OpenAI, run with
    [mlx-whisper](https://github.com/ml-explore/mlx-examples) on Apple MLX, for word times.
  - Apple's Vision framework for the cutouts.
  - [Kenney](https://kenney.nl)'s CC0 sound packs for the paper sounds.
  - [FFmpeg](https://ffmpeg.org) and [Pillow](https://python-pillow.org) for measures and contact
    sheets.
  - Poppler's `pdftotext`, [OpenAlex](https://openalex.org), [Crossref](https://www.crossref.org)
    and [PubMed](https://pubmed.ncbi.nlm.nih.gov) for fact-checking.
- The design-judge loop comes from this repo's `landing-page` skill.
