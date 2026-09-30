# Lessons: what has and has not worked

These are the seed lessons. `scripts/review.py lessons` prints them together with the lessons your runs
have added (stored in ~/.omni-video-ads/LESSONS.md, or LESSONS_PATH). After each QC pass, add one lesson
per real failure or surprise with `scripts/review.py lesson ...`. A lesson is a general cause -> effect rule, not
a description of one clip.

Bad: "the can looked wrong in s2".
Good: "first_frame from a product photo with a busy background makes Omni animate the background
instead of the product; cut the product out onto a plain backdrop first".

Do not delete seed lessons. If a run contradicts one, add a new lesson that supersedes it and say so.

## Seed lessons (from Google's Omni guide and prior multi-model QC; not yet verified by runs of this skill)

- Omni cuts to several shots by default. "Single continuous shot, no scene cuts." keeps one take (the
  compiler adds it while `single_take` is true).
- Edit prompts work when they are short and end with "Keep everything else the same." Descriptive
  edit prompts change unrelated parts of the scene.
- With no audio direction, the model writes its own generic score. Name the sound sources ("one sharp
  can hiss") and say "no music" where silence helps.
- Name the sound source precisely: "fat crackle, one tong clink" beats "sizzle".
- One style anchor beats many: several stacked references cancel each other out.
- Remove one demand before adding three. Failed clips are more often over-specified than under-specified.
- Negatives work better written as positives: "hands resting on the desk" beats "no weird hands".
- Give every reference a job ("<IMAGE_REF_0> is the product"); an unlabelled reference is read as a mood board.
- Model-rendered text is reliable in English only; for other languages overlay supers in assembly.

