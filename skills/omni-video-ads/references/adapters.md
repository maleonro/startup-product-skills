# Adding another video model

The pipeline is provider-agnostic: plans, validation, assembly and QC do not change. A provider only
turns a compiled job into a request and a video file.

## Contents
1. The interface
2. Steps
3. Mapping notes for likely next providers

## 1. The interface (`scripts/lib/providers/base.py`)

```python
class Provider:
    name: str
    modes: tuple            # which plan modes it can run (build_jobs refuses others)
    resolutions: tuple
    price_per_second: dict  # by resolution, for the budget guard
    extend_is_cumulative: bool
    def preflight(self): ...                          # raise ProviderError early (no key, no SDK)
    def build_request(self, job, previous_id): ...    # pure, JSON-serialisable (used by --dry-run)
    def execute(self, request, output_path): ...      # -> {"interaction_id": ..., "output": path}
```

A job carries: `prompt` (already tagged for Omni), `mode`, `duration`, `aspect_ratio`, `resolution`,
`inputs` (ordered image/video parts with `role`: first_frame, last_frame, image_ref, source_video,
video_ref), and `previous_shot`.

## 2. Steps

1. Create `scripts/lib/providers/<name>.py` subclassing `Provider`.
2. In `build_request`, rewrite the prompt for that model if its syntax differs: strip Omni's
   `[# Sources ...]` / `<IMAGE_REF_n>` tags and map `inputs` roles to the model's own fields.
3. If the model has no stateful turns, set `modes` without `extend`/`edit`, or emulate extension by
   passing the last frame of the previous output as the new first frame (then `extend_is_cumulative = False`;
   assembly stitches automatically).
4. Register it in `providers/__init__.py` and run with `build_jobs.py --provider <name>`.
5. Add a provider test to `tests/run_tests.py` (dry-run payload shape at minimum).
6. Log the first real runs in LESSONS.md with the model name, so prompting lessons stay per model.

## 3. Mapping notes

- fal / Replicate gateways (Veo, Kling, Seedance): queue APIs; first frame -> `image_url`/`image`,
  last frame -> `end_image_url`/`last_frame_image`, references -> `reference_images` (Seedance allows
  more than Omni). Fetch the model's input schema at build time rather than hard-coding field names.
- Veo 3.1: 16:9 and 9:16, native audio, no stateful edit; extension is a separate operation.
- Seedance 2.x: multi-shot inside one clip with "Cut to", `@img1`-style references; the smixs
  visual-skills `seedance.md` is the best syntax reference.
