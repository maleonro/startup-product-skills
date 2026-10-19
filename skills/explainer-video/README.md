# explainer-video

A [Claude Code](https://claude.com/claude-code) skill that builds an educational explainer video in
the style of [Kurzgesagt – In a Nutshell](https://kurzgesagt.org): about 8-10 minutes, paper-collage
art, a calm voice, one idea the viewer can retell the next day. Any topic, any language.

It is not an ad maker. A company can make the video, but its product appears once, in a closing
block like Kurzgesagt's sponsor segment, and every number on screen comes from a sources sheet that
was checked against the original papers.

## Example

[Prospección de clientes en LinkedIn: a quién escribirle y cuántas veces insistir](https://youtu.be/pio_TsNUXNQ)
(8:51, Spanish), made with this process for [Kairon](https://heykairon.com) in October 2026. It took
11 script versions, 4 cuts and about 170 Higgsfield credits of paid generation. Every rule in the skill is a
correction made on it.

## What it does

1. **Sources first**: a sheet with every number the script may use and what each study does *not*
   show. Viral numbers get checked against the paper; on the first video several were false.
2. **Script in rounds**: an editor subagent with 20 rules (one idea per chapter, the study scene
   first, the 15-year-old cousin test, no selling) scores and rewrites; you check every new line.
3. **Images at the lowest cost**: draw anything countable or textual in code; sketch with what the
   owner already pays for (an image agent such as xAI's Grok Build CLI, or the images in their
   ChatGPT, Gemini or Grok subscription); pay an API like Higgsfield only for the masters and their
   edits when the free sources do not pass.
4. **Voice and music** chosen from 3 samples each, one music piece per chapter, levelled 14 dB
   under the voice.
5. **Edit in Remotion** to measured targets: joins under 2 s, frozen frames under 15 %, burned-in
   subtitles.
6. **A design judge** scores contact sheets and measures until 8/10.
7. **Publish** with the `youtube-seo` skill, after a benchmark of the most-viewed similar videos.

No paid step runs without the owner's OK on the exact cost.

## Files

- [`SKILL.md`](SKILL.md): hard rules and the 11-step checklist.
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
