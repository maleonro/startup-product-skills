# youtube-seo

A [Claude Code](https://claude.com/claude-code) skill that prepares a YouTube video to be found and
published: the phrases people really search, a benchmark of the most-viewed similar videos, titles
for Test & Compare, a description with chapters and sources, tags, hashtags, captions, thumbnails and
the policy boxes. A script checks all of it against YouTube's official limits before anyone pastes
it into Studio.

Every rule carries a label and a URL: OFFICIAL (a YouTube or Google page), STUDY (measured, sample
stated) or PRACTITIONER (opinion). A practitioner number is never presented as YouTube's rule.

## What it does

1. Finds the phrases people type, from YouTube's own autocomplete, by country and language
   (`scripts/yt-suggest.py`, free, no key). It ranks phrases; it never claims search volume.
2. Benchmarks 10-20 searches' most-viewed recent videos and copies the shape that wins, not a blog
   rule.
3. Writes up to 3 titles, the description, chapters, 5-10 tags and 3 hashtags.
4. Builds captions from the script's exact words with the audio's word times.
5. Makes up to 3 very different thumbnails from the video's own art.
6. Recommends the two disclosure boxes (synthetic content, paid promotion).
7. Checks the package (`scripts/check-metadata.py`) and hands over the Studio steps field by field.

## Files

- [`SKILL.md`](SKILL.md): the package and the 12-step workflow.
- [`references/rules.md`](references/rules.md): every rule with its label and source, read in
  October 2026.
- [`scripts/yt-suggest.py`](scripts/yt-suggest.py): autocomplete phrases by country.
- [`scripts/check-metadata.py`](scripts/check-metadata.py): the package checker.

## Install

```bash
npx skills add maleonro/startup-product-skills --skill youtube-seo
```

Then ask Claude Code to publish a video on YouTube, or to write a title, description, chapters,
tags or a thumbnail for one.

## Credits

Written by [Claude](https://claude.com) (Anthropic) in Claude Code while publishing the first
`explainer-video`. The thumbnail findings cite studies by [vidIQ](https://vidiq.com), 1of10 (via
[Search Engine Journal](https://www.searchenginejournal.com)) and [Eden](https://eden.so); the rest
cite YouTube's and Google's own help pages, linked in `references/rules.md`.
