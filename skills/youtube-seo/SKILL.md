---
name: youtube-seo
description: Prepares a YouTube video to be found and published - the phrases people really search (from YouTube's own autocomplete, by country), a benchmark of the most-viewed similar videos, up to 3 title variants for Test & Compare, a description with chapters, sources and disclosure, tags, hashtags, a captions file, thumbnails, and the two policy boxes - and checks all of it against YouTube's official limits with a script. Every rule is labelled OFFICIAL, STUDY or PRACTITIONER with its URL. Use when publishing a video on YouTube, writing or fixing a YouTube title, description, chapters, tags or hashtags, making a thumbnail or subtitles for YouTube, or when the user says "YouTube SEO", "descripción para YouTube", "título del video" or "subir el video".
---

# YouTube SEO

YouTube ranks search results by relevance (title, description, tags and the video itself against the
query), engagement and quality, and says the title, thumbnail and description matter most; tags play
"a minimal role". So the job is three things: use the words people actually search, promise only what
the video delivers, and make the first lines useful. Every rule below, with its source, is in
[references/rules.md](references/rules.md). Never present a PRACTITIONER number as YouTube's rule.

## The output: a publish package

A folder `youtube/` next to the video, with what a person pastes into YouTube Studio. The
`scripts/` paths below are in this skill's folder; give the package folder as a full path.

| File | What |
|---|---|
| `title.txt` | 1 to 3 titles, one per line. The first is the one to publish; all three go to Test & Compare |
| `description.txt` | the description exactly as it goes into Studio: plain text, bare links, no Markdown |
| `tags.txt` | 5 to 10 tags, comma-separated |
| `<video>.srt` | captions, from the script, not from automatic transcription |
| `thumbnail-a.png` ... | 1 to 3 thumbnails, 1920x1080, under 2 MB |
| `benchmark.md` | the similar videos you measured (step 2), with links and the table of what they do |
| `notes.md` | the searched phrases with date and countries, the choices made, the boxes a person must tick |

## Workflow

1. **Find the phrases people search.** Run, for the video's topics, in the audience's language and
   countries (for example `--hl en --gl US,GB,CA`, or `--hl es --gl AR,MX,CO,ES`):
   `python3 scripts/yt-suggest.py "seed 1" "seed 2" --hl <lang> --gl <countries> --expand`
   It takes about 11 seconds per seed per country, so run it in the background. A phrase that returns
   for many expansions and every country is typed by many people. Autocomplete shows *that* people
   search a phrase, never *how many*: rank phrases, never quote them as volume. Choose 1 main phrase
   that matches what the video teaches (not the most popular one) and 2 or 3 secondary ones. Write
   them in `notes.md` with the date. Measure again before publishing, with more seeds: on the first
   video the main phrase changed after a re-run ("prospección de clientes" came up 73 times, the first
   pick 18). If you have the channel, also look at Studio > Analytics > Inspiration (its name changes
   with rollouts) for searches with few good videos.
   - Spanish videos: people search in neutral Spanish ("cómo conseguir clientes"), even where they
     speak with voseo. Keep the phrase neutral in the title; the voice and the hook can keep voseo.
     It is an inference, not data (`references/rules.md`, section 8): check it in autocomplete.
2. **Benchmark the most-viewed similar videos.** Before writing the description or the thumbnails,
   copy the shape of what already wins, not a blog rule: a user rejected a description built from
   blog rules and accepted one built from peers. Search 10-20 of the phrases, sorted by views and
   uploaded this year (`&sp=CAMSAggF`), and by relevance this year (`&sp=EgIIBQ%3D%3D`). Keep videos
   of the last 6 months, over 3 minutes, on topic, with more than 20,000 views. Read each full
   description from its page (`ytInitialPlayerResponse.videoDetails.shortDescription`) and count how
   they open, list, link and close. Write `benchmark.md` with the links, and say its limit: it is a
   correlation, not an experiment. For thumbnails, put 30 real result thumbnails on one sheet.
3. **Title.** At most 100 characters (OFFICIAL). Put the main phrase in the first ~60, since search
   cuts around 60-70 (PRACTITIONER). It must promise only what the video delivers: YouTube calls a
   high click rate with a short view time clickbait, and misleading titles break the spam policy.
   Write 3 variants that differ in one idea each (the phrase first, the hook first, the question).
   Test & Compare picks the one with the most watch time, not the most clicks.
4. **Description.**
   - Line 1, under ~100 characters so it reads whole on a phone: the problem and a number from the
     video. Line 2: the question the video answers, with the main phrase. Only the first lines show
     before "more".
   - Then follow the benchmark's shape (the B2B sales example is in `references/rules.md`, section 3).
   - Name the secondary phrases in normal sentences. Never a list of keywords or tags, never a
     repeated sentence: both break the spam policy.
   - Say who made the video, in plain words, before the chapters.
   - Chapters (step 5), then sources with links, then 3 hashtags at the end.
   - Plain text: YouTube shows `**` and `[text](url)` raw. `*bold*` works; links go bare.
5. **Chapters.** First at `0:00`, at least 3, each at least 10 seconds, in order (OFFICIAL). Take the
   times from the rendered video, not from the plan. Name what each chapter teaches, not "Chapter 2":
   Google shows these names as key moments in its results. A last chapter under 10 s fails: merge it.
6. **Tags and hashtags.** Tags: the main phrase, its common misspellings (in Spanish, without the
   accents: "prospeccion"), the English term if people use it ("cold email"), 5 to 10 in all. Hashtags: 3, all about the topic;
   only 3 show above the title, and over 60 make YouTube ignore all of them.
7. **Captions.** Upload your own `.srt` (SubRip, UTF-8): automatic captions misspell names and brands.
   Build it from the exact text the voice read, with the word times of the audio (for example from
   local Whisper), never from Whisper's own text. Max 2 lines of 42 characters; never split a number
   from its unit; the first time is never negative (YouTube rejects the file). YouTube says captions
   reach a larger audience; it never says they help ranking, so do not claim it. Set the video
   language in Studio.
8. **Thumbnail.** 16:9, JPG or PNG, at least 1280x720 or Test & Compare shrinks it to 480p
   (OFFICIAL). Use 1920x1080 under 2 MB to be safe on every upload path (our reading of the page).
   Build it in code from the video's own art (a Remotion still): it costs nothing and it shows what
   the video shows.
   - Make 3 **very different** ideas, not 3 versions of one (a face, an object, a crowd): Test &
     Compare picks by watch time and needs a real difference (OFFICIAL).
   - 1 to 5 words, or none (STUDY). A face helps little, and less in business videos (STUDY): make it
     one of the three, not all. Colour and arrows showed no effect (STUDY): stand out from the sheet
     of step 2 instead.
   - Strong is fine, but only with numbers the video gives. Check each one small among the 30 real
     ones, at 320x180 and 168x94. Keep the bottom-right corner free: YouTube puts the duration there.
9. **Disclosures** (a person ticks the boxes; write your recommendation in `notes.md`):
   - *Altered or synthetic content*: required only if realistic content shows a real person saying or
     doing what they did not, alters a real event or place, invents a realistic scene, or the AI music
     is the main focus. A fully animated or clearly unreal video is exempt. A synthetic stock voice is
     not named either way: say so.
   - *Paid promotion*: for paid placements, sponsorships and endorsements. A company's own video about
     its own product is not named either way; saying plainly who made it covers the "not clear" case.
   - *Inauthentic content* (monetization): each video needs its own script and sources, not a template.
10. **Check.** `python3 scripts/check-metadata.py <video>/youtube --duration <seconds> --keyword "<main phrase>"`.
    `--duration` takes seconds (531.2, not 8:51). Fix every ERROR. Keep a WARN only with a reason in
    `notes.md`.
11. **Hand over** the Studio steps a person does, **field by field**. Give the title on its own line,
    apart from the description: a person once pasted two description lines into the title field (183
    of 100 characters). Then the description, the thumbnail, the `.srt`, the language, tags, the two
    boxes, end screen (last 5-20 seconds, up to 4 elements), a playlist, a pinned comment with a
    question, and Test & Compare with the 3 titles and thumbnails (computer only).
12. **After publishing,** look only after a few days and 100 views. Half of all videos have a click rate
    between 2% and 10% (OFFICIAL); a test takes up to 2 weeks. Compare by traffic source, and read how
    many viewers are still there at 30 seconds.

## Videos a company makes

The description follows the same data rule as the video: every number comes from the video's sources
sheet, and its "Do not say" rules apply. The company appears where the video shows it, with one link
that carries `utm_source=youtube`, and the description says who made the video. The whole video
workflow is the `explainer-video` skill.

## Do not

- Do not stuff tags, hashtags or keywords; do not paste a tag list in the description.
- Do not write "YouTube ranks by CTR" or "your own captions rank better": no official source says so.
- Do not quote a title or description length from a blog as YouTube's limit. Only 100 and 5,000 are.
