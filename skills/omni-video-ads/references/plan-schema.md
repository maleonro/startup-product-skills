# adplan.json fields

Start from `assets/example/plan.json`. Paths are relative to the plan file.

## Top level

| Field | Req | Meaning |
|---|---|---|
| `id` | - | short slug, used in output file names |
| `brand` | yes | `name`, `product`, colours `primary`, `on_primary`, `accent`, `on_accent`, `super_bg`, `super_fg` (hex), `logo` (png), `font` (.ttf/.otf path or family name) |
| `brief` | yes | `audience`, `offer`, `angle`, `cta`, `claims` [{`text`, `substantiation`}], optional `category`, `real_person_likeness`, `likeness_consent` (true once written consent exists) |
| `language` | yes | ISO code of the ad copy (`es`, `en`, `pt`); prompt fields stay English |
| `region` | - | `eu`/`eea`/`uk`/`ch` turns on regional upload checks (or env `OMNI_REGION`) |
| `placements` | yes | keys of assets/placements.json |
| `master_aspect` | yes | `9:16` or `16:9` |
| `draft_resolution` / `final_resolution` | - | default `360p` / `720p` |
| `crop_anchor` | - | 0-1 vertical position of the 4:5/1:1 crop window (default 0.5) |
| `style` | yes | `look`, `palette`, `lens`, `audio_bed` (repeated in every prompt) |
| `characters` | - | [{`id`, `name`, `identity`, `realistic` (default true), `ref_image`}] |
| `shots` | yes | ordered list, see below; order = cut order |
| `end_card` | yes | `duration` 1-4, `headline`, `cta`, `url`, `logo`, `bg`, `fg` |
| `disclosure` | - | `ai_label` (text on end card), `overlay` (label over the whole cut), `text` |

## Shot

| Field | Req | Meaning |
|---|---|---|
| `id` | yes | unique |
| `role` | yes | hook, problem, setup, reveal, macro, use, reaction, proof, hero, transition |
| `mode` | yes | text_to_video, first_frame, first_last, reference, extend, edit, recorded |
| `duration` | yes* | integer 3-10 (*not for edit or recorded) |
| `subject`, `action` | yes* | lead sentence: "subject action" must read as one sentence (*generated shots) |
| `setting` | - | place and props |
| `details` | yes | `environment`, `micro_action`, `motif` |
| `camera` | yes | shot size, lens, one move |
| `light` | - | per-shot light |
| `audio` / `music` | yes (one of audio, music, style.audio_bed) | foreground sound / replaces the bed |
| `final_image` | - (warned) | the frame the shot ends on |
| `characters` | - | ids from `characters` (identity block is inserted) |
| `dialogue` | - | {`speaker`, `line`, `delivery`} |
| `beats` | - | [{`t`: "0-2s", `what`}] internal timecodes |
| `supers` | - | [{`text`, `start`, `end`, `position`: top/center/lower}] seconds within the shot |
| `native_text` | - | English sentences describing text inside the scene |
| `avoid` | - | extra negatives ("No people in frame.") |
| `single_take` | - | default true |
| `first_frame`, `last_frame` | mode | image paths; `first_frame_contains_people` for R8 |
| `image_refs` / `video_refs` | mode | [{`path`, `label`, `contains_people`}] |
| `continues` | extend | id of the earlier shot to extend |
| `edits` + `edit_prompt` | edit | id of the shot (chain tail) to edit, short instruction |
| `source_video` | extend/edit/recorded | extend/edit: clip uploaded to Omni, <= 10 s (blocked in EEA/CH/UK). recorded: clip cut in unchanged, any length, any region |
| `trim` | - | recorded: [start_s, end_s] of the source to use |
| `source_contains_people` | - | true when `source_video` shows a recognizable real person (R8, R20) |

## Timeline rules

- Shots play in list order. An `extend` shot follows the shot it continues on the same take; the
  segment's clip is the chain's last output (cumulative).
- An `edit` shot is not a new segment: it replaces the clip of the shot it edits (chains of edits
  are allowed: e2 edits e1 edits s4).
- A `recorded` shot is its own segment; its length is the clip (or `trim`). It cannot be extended or
  edited by later shots: to change real video with Omni, put it in that shot's `source_video` instead.
- An `extend` shot whose chain starts from a `source_video` occupies source length + `duration`; an
  `edit` of a `source_video` (no `edits`) is its own segment with the source's length.
- Planned length = the sum of those segment lengths + end card.
