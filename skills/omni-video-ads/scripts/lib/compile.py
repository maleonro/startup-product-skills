"""Compile one shot of an ad plan into a provider-agnostic generation job.

The prompt layout follows Google's Omni prompting guide (single-take clause, role tags,
"Sound design:" audio line, simple negatives) with the ad craft rules from
references/prompt-craft.md (subject+action first, three concrete details, one camera
move, named final image, repeated identity block).
"""
from __future__ import annotations

import mimetypes
import re

from .common import placements, resolve, shot_index, source_seconds

IMAGE_EXT = {".png", ".jpg", ".jpeg", ".webp"}


def _mime(path: str) -> str:
    m, _ = mimetypes.guess_type(path)
    return m or ("video/mp4" if path.lower().endswith((".mp4", ".mov")) else "image/png")


def _sentence(text: str | None) -> str:
    text = (text or "").strip()
    if not text:
        return ""
    text = text[0].upper() + text[1:]
    return text if text[-1] in ".!?\"'" else text + "."


def keep_fraction(plan: dict) -> float | None:
    """Fraction of the master frame height that survives the tightest crop placement."""
    master = plan.get("master_aspect", "9:16")
    pl = placements()
    mw, mh = (1080, 1920) if master == "9:16" else (1920, 1080)
    fracs = []
    for name in plan.get("placements", []):
        p = pl.get(name)
        if not p:
            continue
        w, h = p["size"]
        # scale placement to master width (vertical master) or height (landscape master)
        if master == "9:16":
            fracs.append(min(1.0, (mw * h / w) / mh))
        else:
            fracs.append(min(1.0, (mh * w / h) / mw))
    f = min(fracs) if fracs else 1.0
    return None if f >= 0.99 else f


SUPER_ZONE = {"top": "upper third", "center": "center", "lower": "lower third"}


def compile_prompt(plan: dict, shot: dict) -> str:
    """Build the English prompt text for a generating shot (not edit)."""
    style = plan.get("style", {})
    chars = {c["id"]: c for c in plan.get("characters", [])}
    det = shot.get("details", {})
    lines: list[str] = []

    if shot.get("mode") == "extend":
        lines.append("Extend this video. The scene continues.")
    if shot.get("single_take", True):
        lines.append("Single continuous shot, no scene cuts.")

    # Weight-at-start: subject + action lead. `action` is a verb phrase whose grammatical
    # subject is `subject` ("The woman at her desk" + "lets her head drop ...").
    lead = " ".join(x.strip().rstrip(".") for x in (shot.get("subject"), shot.get("action")) if x)
    if lead:
        lines.append(_sentence(lead))
    for cid in shot.get("characters", []):
        c = chars.get(cid)
        if c and c.get("identity"):
            lines.append(_sentence(f"{c.get('name', cid)}: {c['identity']}"))

    beats = shot.get("beats") or []
    for b in beats:
        lines.append(f"[{b['t']}] {_sentence(b['what'])}")

    setting = "; ".join(x for x in (shot.get("setting"), det.get("environment")) if x)
    if setting:
        lines.append(_sentence(f"Setting: {setting}"))
    for key in ("micro_action", "motif"):
        if det.get(key):
            lines.append(_sentence(det[key]))
    # The plan-wide lens applies only when the shot names no lens of its own.
    lens = style.get("lens") if not re.search(r"\d+\s?mm|macro|fisheye|anamorphic", shot.get("camera", ""), re.I) else None
    if shot.get("camera") or lens:
        cam = "; ".join(x for x in (shot.get("camera"), lens) if x)
        lines.append(_sentence(f"Camera: {cam}"))
    if shot.get("light"):
        lines.append(_sentence(f"Lighting: {shot['light']}"))
    look = "; ".join(x for x in (style.get("look"), style.get("palette")) if x)
    if look:
        lines.append(_sentence(f"Style: {look}"))

    kf = keep_fraction(plan)
    if kf:
        lines.append(f"Keep the subject and product inside the central {int(kf * 100)}% of the frame height.")
    zones = sorted({SUPER_ZONE.get(s.get("position", "center"), "center") for s in shot.get("supers", [])})
    if zones:
        lines.append(f"Leave clean, uncluttered negative space in the {' and '.join(zones)} of the frame.")

    for t in shot.get("native_text", []):
        lines.append(_sentence(t))
    if shot.get("final_image"):
        lines.append(_sentence(f"The shot ends on {shot['final_image']}"))

    # `music` on a shot replaces the plan-wide bed for that shot ("no music", "the beat drops").
    bed = shot["music"] if "music" in shot else style.get("audio_bed")
    audio = "; ".join(x for x in (shot.get("audio"), bed) if x)
    if audio:
        lines.append(_sentence(f"Sound design: {audio}"))
    dl = shot.get("dialogue")
    if dl and dl.get("line"):
        who = chars.get(dl.get("speaker"), {}).get("name", dl.get("speaker", "The character"))
        how = f", {dl['delivery']}" if dl.get("delivery") else ""
        lines.append(f'{who} says{how}: "{dl["line"]}"')

    negatives = []
    if not (dl and dl.get("line")):
        negatives.append("No dialogue.")
    if not shot.get("native_text"):
        negatives.append("No on-screen text, captions, subtitles or logos.")
    negatives += [_sentence(a) for a in shot.get("avoid", [])]
    lines += negatives
    return " ".join(x for x in lines if x)


def _article(label: str | None) -> str:
    """'product' -> 'the product'; 'the product' / 'a reference' stay as written."""
    label = (label or "a reference").strip().rstrip(".")
    return label if re.match(r"(the|a|an|her|his|their|our)\s", label, re.I) else f"the {label}"


def _tagged(prompt: str, images: list[dict], videos: list[dict], shot: dict) -> str:
    """Prefix role declarations the way the Gemini Omni guide specifies."""
    first = [i for i in images if i["role"] == "first_frame"]
    last = [i for i in images if i["role"] == "last_frame"]
    refs = [i for i in images if i["role"] == "image_ref"]
    vrefs = [v for v in videos if v["role"] == "video_ref"]
    src_vid = [v for v in videos if v["role"] == "source_video"]

    sources, references, guide = [], [], []
    for i in first:
        sources.append(f"<FIRST_FRAME>@Image{i['n']}")
    for i in last:
        sources.append(f"<LAST_FRAME>@Image{i['n']}")
    for v in src_vid:
        sources.append(f"<VIDEO_0>@Video{v['n']}")
    for k, i in enumerate(refs):
        references.append(f"<IMAGE_REF_{k}>@Image{i['n']}")
        guide.append(f"<IMAGE_REF_{k}> is {_article(i.get('label'))}.")
    for k, v in enumerate(vrefs):
        references.append(f"<VIDEO_REF_{k}>@Video{v['n']}")
        guide.append(f"<VIDEO_REF_{k}> is {_article(v.get('label'))}.")

    simple = not refs and not vrefs and not src_vid
    if simple and first and last:
        return f"<FIRST_FRAME> <LAST_FRAME> {prompt}"
    if simple and first:
        return f"<FIRST_FRAME> {prompt}"
    head = ""
    if sources:
        head += f"[# Sources {' '.join(sources)}] "
    if references:
        head += f"[# References {' '.join(references)}] "
    tail = []
    if first:
        tail.append(f"Use Image{first[0]['n']} as the starting frame.")
    if last:
        tail.append(f"Use Image{last[0]['n']} as the final frame.")
    if refs:
        tail.append("Use the given image(s) as references for video generation. "
                    "The images should not be used as literal initial frames.")
    if vrefs:
        tail.append("Use the given video(s) as references. Do not use them as a source for video editing.")
    return (head + " ".join(guide) + " " + prompt + " " + " ".join(tail)).strip()


def build_job(plan_path: str, plan: dict, shot: dict, pass_name: str, out_dir: str) -> dict:
    """Return a provider-agnostic job for one shot."""
    res = plan.get("draft_resolution", "360p") if pass_name == "draft" else plan.get("final_resolution", "720p")
    mode = shot.get("mode", "text_to_video")
    images: list[dict] = []
    videos: list[dict] = []
    n_img = n_vid = 0

    def add_img(path, role, label=None):
        # Each role gets its own input part (a loop sends the same file twice, as
        # Google's reference script does); providers upload a given path only once.
        nonlocal n_img
        p = str(resolve(plan_path, path))
        n_img += 1
        images.append({"kind": "image", "role": role, "path": p, "mime_type": _mime(p), "n": n_img, "label": label})

    def add_vid(path, role, label=None):
        nonlocal n_vid
        p = str(resolve(plan_path, path))
        n_vid += 1
        videos.append({"kind": "video", "role": role, "path": p, "mime_type": _mime(p), "n": n_vid, "label": label})

    if shot.get("first_frame"):
        add_img(shot["first_frame"], "first_frame")
    if shot.get("last_frame"):
        add_img(shot["last_frame"], "last_frame")
    for r in shot.get("image_refs", []):
        add_img(r["path"], "image_ref", r.get("label"))
    if shot.get("source_video"):
        add_vid(shot["source_video"], "source_video")
    for r in shot.get("video_refs", []):
        add_vid(r["path"], "video_ref", r.get("label"))

    previous = None
    if mode == "extend" and shot.get("continues"):
        previous = shot["continues"]
    if mode == "edit" and shot.get("edits"):
        previous = shot["edits"]

    if mode == "edit":
        text = (shot.get("edit_prompt") or "").strip()
        if "keep everything else the same" not in text.lower():
            text = (_sentence(text) + " Keep everything else the same.").strip()
        prompt = text
    else:
        prompt = _tagged(compile_prompt(plan, shot), images, videos, shot)

    # Input part order: images (Image1..N) then videos (Video1..M), matching the tags.
    uploads = [{k: v for k, v in x.items() if k != "label"} for x in images + videos]

    return {
        "shot": shot["id"],
        "role": shot.get("role"),
        "mode": mode,
        "pass": pass_name,
        "prompt": prompt,
        "duration": int(shot.get("duration", 5)) if mode != "edit" else None,
        "aspect_ratio": plan.get("master_aspect", "9:16"),
        "resolution": res,
        "inputs": uploads,
        "previous_shot": previous,
        # Length of an uploaded clip this shot extends or edits: the cost and mock use it.
        "source_seconds": round(source_seconds(plan, shot), 3) if shot.get("source_video") else 0.0,
        "output": f"{out_dir}/{pass_name}/{shot['id']}.mp4",
    }


def ordered_shots(plan: dict) -> list[dict]:
    """Shots in dependency order (a shot after the one it extends or edits)."""
    idx = shot_index(plan)
    done, out = set(), []

    def visit(sid, stack=()):
        if sid in done or sid not in idx or sid in stack:
            return
        s = idx[sid]
        dep = s.get("continues") if s.get("mode") == "extend" else s.get("edits") if s.get("mode") == "edit" else None
        if dep:
            visit(dep, stack + (sid,))
        done.add(sid)
        out.append(s)

    for sid in idx:
        visit(sid)
    return out
