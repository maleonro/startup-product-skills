# Script and sources

The script is the backbone (Kurzgesagt's own words). It took 11 versions on the first video. Each
version came from the editor subagent ([editor.md](editor.md)), and each was then checked by hand
against the sources sheet.

## 1. The sources sheet comes first

`sources.md`, built before the first script line. For each study:

- the full citation with its DOI or URL, and whether it is a working paper or the published version;
- the exact numbers the script may use, with the page or table;
- **"Do not say"**: what the study does not show (other country, other job, no replication);
- the studies you dropped, and why.

If the video uses your own company's data (a client funnel, rates by message length), it gets the
same treatment: the query, the date, the base (for example "40 companies, 14,513 invitations,
measured 2026-10-17"), and "these are comparisons between campaigns, not experiments". Pool the rates;
do not average them. Say "it comes from forty real companies", never "the average of forty companies".
Leave your own account and test accounts out of the query.

## 2. Fact-check: trust nothing you did not read in the original

- Two research agents (the cheaper model) verify each study and write a report. Then you re-check the
  key numbers yourself: `pdftotext` on the PDF, or the abstract from OpenAlex, Crossref or PubMed
  when the publisher page is a login wall.
- **Viral numbers were false.** On the first video (sales outreach): candies 3 % / 14 %, the
  post-it 76 %, Schilke 16/18/20 %. None is in the papers. **Famous results fell:** Langer's empty
  "because" (Folkes 1985 did not replicate), "but you are free to say no" (null in low-bias studies,
  Fillon 2023), Ariely and Wertenbroch 2002 (Data Colada [138], 2026-08-31: evidence of fraud in
  Study 2).
- **The company's own beliefs did not all hold.** "42 % of replies come from follow-ups" measured
  23 %. "Visit the profile before inviting" did not change acceptance (34.9 % vs 34.9 %). Re-measure
  before you quote. Of 27 claims the company made, only 5 had a study, its own data and a product
  feature behind them: those 5 made the chapters.
- **Every editor round adds overstatements.** Examples caught: "they invented the profiles in 2022"
  (2022 was the invitations), "3 years ago" (the source says "at least 3"), "one or two follow-ups
  are enough" (the 2nd and 3rd follow-up rate the same, 5.8 %). Read every new line against the sheet.

## 3. The editor loop

Launch the editor subagent with the prompt in [editor.md](editor.md): the current script,
`sources.md`, the owner's notes file, the target length and the voice's pace. It writes
`review-<n>.md` (scores per chapter and problems) and `script-v<n>.md`, and never touches the
original. It never adds a number that is not in the sheet; it proposes new ones apart, marked
`[VERIFY]`. When the owner adds a rule ("the examples arrive way too late"), add it to `editor.md`
too.

Script format: one block per chapter with `**Voice**` (what is read) and `**Image**` (what is
shown). Extract the voice to time it:
`awk '/^\*\*Voice\*\*/{v=1;next} /^\*\*Image\*\*/{v=0} v' script-v<n>.md > voice.txt`

## 4. Time it with the real voice

Measure the chosen voice on a recorded take. The first video's voice (ElevenLabs v4, Spanish) read
about **132 words per minute**. The macOS `say` estimate at 155 came out more than a minute short in
ten. So 1,300 words made about 10 minutes. To gain time, cut before you compress.

## 5. The shape that worked

The first video taught sales outreach on LinkedIn and email. Its shape carries to any topic:

- **Hook: a study scene in the first 15 seconds.** Researchers made 408 fake LinkedIn profiles; one
  in four invitations was accepted, one in five replied (Evsyukova, Rusche and Mill 2025, QJE). Then
  the protagonist, also invented, and said so: "Martina does not exist. What happens to her does. It
  comes from forty real companies...", with her whole funnel spoken: 150 invitations, 50 accept, 14
  reply, 5 are interested. "What do those five have?"
- **One chapter per stage of the idea.** Each opens with its study scene and a bet for the viewer
  ("how many do you think..."), then the protagonist, then your own data, then what it means for you.
- **The model chapter** (weak ties): a question, a twist against what the viewer believes, a person
  with a name (Granovetter), the study as a scene, a memorable name for the idea, a modern
  confirmation (Rajkumar et al. 2022), and what it means for you.
- **One thread.** The protagonist writes to the same person across the chapters, tries, fails and
  learns. The close returns to the opening image.
- **The product block**, if any, comes last. Once the owner approves its sentences, they stay word
  for word in every later version.

## 6. What the owner rejected

Notes from the first video, translated.

| Note | Fix |
|---|---|
| "more educational, with academic sources, not just our own data" | Studies first, own data second |
| "some explanations are hard to understand" | The 15-year-old cousin test, one idea per sentence |
| "this word sounds like a literal translation" | Say the idea as people say it; the term goes in the on-screen citation |
| "our product does exactly this" (the lesson said X still costs effort; the product automates X) | Changed the big idea, not the product block |
| A hook about a grandmother's birthday | A study scene as the hook |
| "nobody sends 150 invitations on one Monday" | Realistic time: a week |
| "the academic examples arrive way too late" | The study scene opens the video and every chapter |
| "something odd between the 150 and the 40 companies" | "Martina does not exist. What happens to her does." and the whole funnel spoken |
