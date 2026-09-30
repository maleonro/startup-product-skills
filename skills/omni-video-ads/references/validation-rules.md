# Validation rules and why each threshold exists

`validate_plan.py` runs these before any spend; `build_jobs.py` refuses to build while any ERROR remains.
WARNs are judgment calls: fix them or tell the user why you kept them.

| ID | Level | Rule | Why this threshold |
|---|---|---|---|
| R1 | E | Required top-level fields; unique shot ids | Everything downstream keys on ids |
| R2 | E | Master 9:16/16:9; valid resolutions; placement fits master | Omni renders only 9:16 and 16:9; 9:16 from 16:9 keeps ~32% of the frame |
| R3 | E/W | Known mode; standard role | Roles drive hook/product checks |
| R4 | E | Integer duration 3-10 s | Omni's per-call range |
| R5 | E/W | Mode inputs present; extend/edit targets exist, earlier, no forks, not recorded; no edit mid-chain; valid `trim`; edit prompt < 25 words | A chain is linear; an extend output already contains the earlier clip, so editing a mid-chain shot would be discarded. A recorded clip never went through Omni, so it has no interaction to continue. Google: short edits change less |
| R6 | E/W | <= 6 image refs, <= 3 video refs; refs labelled; video refs ~3 s; uploads <= 10 s | Omni limits (API docs); unlabelled refs are read as a moodboard |
| R7 | E | Media files exist and are readable | Fails before the File API upload, not after |
| R8 | E | EEA/CH/UK: no uploaded-video edit/extend, no recognizable-people uploads (images, source or reference videos); recorded shots exempt | Omni regional restriction; the call returns empty otherwise. Recorded clips are never sent to Omni |
| R9 | E/W | subject, action, 3 details; final image (warn) | Details Law: thin shots render as mush; the final image is the cut point |
| R10 | W | Filler words | They do not change the render and crowd out physical detail |
| R11 | E/W | Camera required; > 2 moves warns | One primary move per shot; stacked moves read as chaos in 3-10 s |
| R12 | E | Audio direction present | Without it Omni invents a generic score |
| R13 | W | Prompt fields look non-English (> 6% Spanish/Portuguese function words) | Omni is evaluated in English only; 6% catches a Spanish sentence without flagging brand names |
| R14 | E/W | Dialogue <= 2.5 words/s; non-English speech warns; speaker defined | 2.5 words/s is a comfortable ad read; faster lines get clipped or rushed |
| R15 | E/W | Supers inside the shot's real length (recorded and uploaded clips included), valid position, <= 3 words/s, no overlap; native text only in English ads | ~3 words/s is a sound-off reading speed; the model garbles non-English text |
| R16 | E/W | Characters defined with identity; a character in more than one segment without a reference warns; unused ref warns | No memory between generations; identity drifts without a reference or an extend chain |
| R17 | E | Extend chain <= 40 s | Omni's cumulative extension cap |
| R18 | E/W | First shot is the hook; hook <= 5 s; first super by 1 s and <= 7 words; a product shot exists | Scroll decision in ~2 s, mostly muted; an ad without the product on screen is brand-blind |
| R19 | E/W | End card 1-4 s with CTA; placeholder-looking end-card text warns; cut length vs placement best length | Every ad needs an action; best lengths from placement guidance |
| R20 | E/W | Claims have substantiation; no political category; realistic people need the AI label; a real person needs `likeness_consent` | Platform ad policies and the EU AI Act (compliance.md) |
