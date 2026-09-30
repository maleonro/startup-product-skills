#!/usr/bin/env python3
"""Validate an ad plan (adplan.json) before any generation is paid for.

Usage:
  validate_plan.py adplan.json [--region eu] [--json]

Exit code 0 = no ERRORs (WARNs allowed), 1 = at least one ERROR, 2 = unreadable plan.
Every rule has an ID so fixes can be discussed precisely; the full list with the
reasoning behind each threshold is in references/validation-rules.md.
"""
from __future__ import annotations

import argparse
import json
import os
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from lib.common import (MAX_CHAIN_S, MAX_IMAGE_REFS, MAX_SHOT_S, MAX_VIDEO_REF_S, MAX_VIDEO_REFS,  # noqa: E402
                        MAX_UPLOAD_VIDEO_S, MIN_SHOT_S, MODES, RESTRICTED_REGIONS, ROLES, VALID_ASPECTS,
                        VALID_RESOLUTIONS, chain_of, load_json, placements, planned_seconds, probe,
                        region, resolve, shot_index, which, words, attach_path, chains, shot_seconds, source_seconds)

FILLER = ["cinematic", "stunning", "masterpiece", "epic", "high quality", "high-quality", "4k", "8k",
          "beautiful", "amazing", "breathtaking", "professional", "award-winning", "hyperrealistic",
          "ultra realistic", "dynamic camera", "intense", "powerful"]
CAMERA_MOVES = ["dolly", "push-in", "push in", "pull-back", "pull back", "pan ", "panning", "tilt", "tracking",
                "crane", "orbit", "zoom", "handheld", "whip", "arc shot", "truck", "pedestal", "drone"]
# Words that suggest a prompt field was written in Spanish/Portuguese instead of English.
NON_EN = {"el", "la", "los", "las", "una", "con", "del", "que", "por", "para", "sobre", "mientras",
          "cámara", "luz", "mujer", "hombre", "producto", "sonido", "fondo", "uma", "com", "não"}
PROMPT_FIELDS = ("subject", "action", "setting", "camera", "light", "final_image", "audio")
SPEECH_WPS = 2.5      # comfortable spoken words per second in an ad
READ_WPS = 3.0        # max on-screen words per second a sound-off viewer can read
HOOK_SUPER_WORDS = 7  # first-frame super must be glanceable
EDIT_PROMPT_WORDS = 25  # Google: short edit prompts; longer ones rewrite unrelated parts of the scene
NON_EN_RATIO = 0.06  # share of Spanish/Portuguese function words that marks a non-English field
FILE_SLACK_S = 0.05  # container durations overshoot by a frame or two


class Report:
    def __init__(self):
        self.items: list[dict] = []

    def err(self, rule, where, msg):
        self.items.append({"level": "ERROR", "rule": rule, "where": where, "msg": msg})

    def warn(self, rule, where, msg):
        self.items.append({"level": "WARN", "rule": rule, "where": where, "msg": msg})

    @property
    def errors(self):
        return [i for i in self.items if i["level"] == "ERROR"]


def _text_of(shot: dict) -> str:
    det = shot.get("details", {})
    return " ".join(str(shot.get(f, "")) for f in PROMPT_FIELDS) + " " + " ".join(str(v) for v in det.values())


def validate(plan: dict, plan_path: str, reg: str = "") -> Report:
    r = Report()
    attach_path(plan, plan_path)
    pl = placements()
    reg = (reg or plan.get("region") or region() or "").lower()
    restricted = reg in RESTRICTED_REGIONS

    # R1 structure
    for key in ("brand", "brief", "language", "placements", "master_aspect", "style", "shots", "end_card"):
        if key not in plan:
            r.err("R1", "plan", f"missing top-level field `{key}`")
    shots = plan.get("shots", [])
    if not isinstance(shots, list) or not shots:
        r.err("R1", "plan", "`shots` must be a non-empty list")
        return r
    ids = [s.get("id") for s in shots]
    dup = {i for i in ids if ids.count(i) > 1}
    if dup or None in ids:
        r.err("R1", "shots", f"every shot needs a unique id (duplicates/missing: {sorted(map(str, dup)) or 'id'})")
    idx = shot_index(plan)

    # R2 master aspect, resolutions, placements
    master = plan.get("master_aspect")
    if master not in VALID_ASPECTS:
        r.err("R2", "master_aspect", f"Omni renders only {VALID_ASPECTS}; got {master!r}")
    for k in ("draft_resolution", "final_resolution"):
        if plan.get(k) and plan[k] not in VALID_RESOLUTIONS:
            r.err("R2", k, f"must be one of {VALID_RESOLUTIONS}")
    for name in plan.get("placements", []):
        p = pl.get(name)
        if not p:
            r.err("R2", "placements", f"unknown placement `{name}`; known: {', '.join(pl)}")
        elif p["master_aspect"] not in ("any", master):
            r.err("R2", "placements", f"`{name}` needs a {p['master_aspect']} master; this plan is {master}. "
                                      "Make a second plan with the other master instead of cropping it.")

    chars = {c.get("id"): c for c in plan.get("characters", [])}
    lang = (plan.get("language") or "en").lower()
    continued_by: dict[str, list[str]] = {}

    for s in shots:
        sid = s.get("id", "?")
        mode = s.get("mode", "text_to_video")
        where = f"shot {sid}"
        if mode not in MODES:
            r.err("R3", where, f"mode must be one of {MODES}")
            continue
        if s.get("role") and s["role"] not in ROLES:
            r.warn("R3", where, f"role `{s['role']}` is not a standard role {ROLES}")

        # R4 duration
        if mode == "recorded":
            if not s.get("source_video"):
                r.err("R5", where, "mode recorded needs `source_video` (the clip to cut in)")
            trim = s.get("trim")
            if trim is not None and (len(trim) != 2 or not 0 <= float(trim[0]) < float(trim[1])):
                r.err("R5", where, "`trim` must be [start_s, end_s] with start < end")
            if s.get("duration") is not None:
                r.warn("R4", where, "`duration` is ignored for recorded shots; length comes from the clip/`trim`")
        elif mode != "edit":
            d = s.get("duration")
            if not isinstance(d, int) or not (MIN_SHOT_S <= d <= MAX_SHOT_S):
                r.err("R4", where, f"duration must be an integer {MIN_SHOT_S}-{MAX_SHOT_S} s per Omni call (got {d!r})")

        # R5 mode inputs
        if mode in ("first_frame", "first_last") and not s.get("first_frame"):
            r.err("R5", where, f"mode {mode} needs `first_frame`")
        if s.get("last_frame") and not s.get("first_frame"):
            r.err("R5", where, "`last_frame` only works together with `first_frame`")
        if mode == "first_last" and not s.get("last_frame"):
            r.err("R5", where, "mode first_last needs `last_frame`")
        if mode == "reference" and not (s.get("image_refs") or s.get("video_refs")):
            r.err("R5", where, "mode reference needs `image_refs` or `video_refs`")
        if mode == "extend":
            src = s.get("continues")
            if not src and not s.get("source_video"):
                r.err("R5", where, "extend needs `continues` (a generated shot) or `source_video`")
            elif src and src not in idx:
                r.err("R5", where, f"`continues` points to unknown shot `{src}`")
            elif src and idx[src].get("mode") == "recorded":
                r.err("R5", where, f"`{src}` is a recorded clip; to extend real video use `source_video` "
                                   "on this shot instead (blocked in EEA/CH/UK)")
            elif src and ids.index(src) > ids.index(sid):
                r.err("R5", where, f"`continues` must point to an earlier shot (`{src}` comes later)")
            if src:
                continued_by.setdefault(src, []).append(sid)
        if mode == "edit":
            tgt = s.get("edits")
            if not (tgt or s.get("source_video")):
                r.err("R5", where, "edit needs `edits` (a generated shot) or `source_video`")
            elif tgt and tgt not in idx:
                r.err("R5", where, f"`edits` points to unknown shot `{tgt}`")
            elif tgt and idx[tgt].get("mode") == "recorded":
                r.err("R5", where, f"`{tgt}` is a recorded clip; to edit real video use `source_video` on this shot")
            if not s.get("edit_prompt"):
                r.err("R5", where, "edit needs `edit_prompt`")
            elif words(s["edit_prompt"]) > EDIT_PROMPT_WORDS:
                r.warn("R5", where, "edit prompts work best short (<25 words); long edits change unintended things")

        # R6 reference limits and file checks
        imgs = s.get("image_refs", [])
        vids = s.get("video_refs", [])
        if len(imgs) > MAX_IMAGE_REFS:
            r.err("R6", where, f"{len(imgs)} image refs; Omni accepts at most {MAX_IMAGE_REFS}")
        if len(vids) > MAX_VIDEO_REFS:
            r.err("R6", where, f"{len(vids)} video refs; Omni accepts at most {MAX_VIDEO_REFS}")
        for ref in imgs + vids:
            if not ref.get("label"):
                r.warn("R6", where, f"reference {ref.get('path')} has no `label`; give each reference a job "
                                    "('the product', 'the hero's face') or the model treats it as a moodboard")
        media = [("first_frame", s.get("first_frame")), ("last_frame", s.get("last_frame")),
                 ("source_video", s.get("source_video"))]
        media += [("image_ref", x.get("path")) for x in imgs] + [("video_ref", x.get("path")) for x in vids]
        for kind, rel in media:
            if not rel:
                continue
            p = resolve(plan_path, rel)
            if not p.exists():
                r.err("R7", where, f"{kind} file not found: {rel}")
                continue
            if kind in ("video_ref", "source_video") and which("ffprobe"):
                try:
                    dur = probe(p)["duration"]
                except Exception:
                    r.err("R7", where, f"{kind} {rel} is not a readable video")
                    continue
                if kind == "video_ref" and dur > MAX_VIDEO_REF_S + FILE_SLACK_S:
                    r.warn("R6", where, f"video ref {rel} is {dur:.1f}s; refs work best at ~3s "
                                        "(trim: ffmpeg -t 3)")
                if kind == "source_video" and dur > MAX_UPLOAD_VIDEO_S + FILE_SLACK_S:
                    r.err("R6", where, f"source video {rel} is {dur:.1f}s; uploads for edit/extend must be <=10s")

        # R8 region (applies to media sent to Omni, not to recorded clips cut in as-is)
        if restricted and mode != "recorded" and s.get("source_video"):
            r.err("R8", where, f"region `{reg}`: Omni does not edit or extend uploaded videos in the EEA, "
                               "Switzerland or the UK. Generate the shot instead: from a product still with no "
                               "recognizable person, or with a described (generated) person; cut the real clip "
                               "in unchanged with mode `recorded`.")
        if restricted and mode != "recorded":
            people = [x for x in imgs + vids if x.get("contains_people")]
            if s.get("first_frame_contains_people") or s.get("source_contains_people") or people:
                r.err("R8", where, f"region `{reg}`: uploads of recognizable people are blocked; "
                                   "use a described (generated) person or a product-only still")

        # R15 supers apply to every shot kind, including recorded clips
        sup = sorted(s.get("supers", []), key=lambda x: x.get("start", 0))
        span = shot_seconds(plan, s)
        for i, su in enumerate(sup):
            a, b = float(su.get("start", 0)), float(su.get("end", 0))
            if not su.get("text"):
                r.err("R15", where, "super without text")
                continue
            if not (0 <= a < b <= span + FILE_SLACK_S):
                r.err("R15", where, f"super '{su['text'][:30]}' timing {a}-{b}s is outside the {span:.1f}s shot")
            if su.get("position", "center") not in ("top", "center", "lower"):
                r.err("R15", where, "super position must be top, center or lower")
            n = words(su["text"])
            if b > a and n / (b - a) > READ_WPS:
                r.warn("R15", where, f"super '{su['text'][:30]}' needs {n / (b - a):.1f} words/s; "
                                     f"sound-off readers manage ~{READ_WPS}")
            if i and a < float(sup[i - 1].get("end", 0)):
                r.warn("R15", where, "overlapping supers compete for the eye")

        if mode in ("edit", "recorded"):
            continue  # the rest concerns prompts for generated shots

        # R9 Details Law (three concrete details per shot)
        det = s.get("details", {})
        missing = [k for k in ("environment", "micro_action", "motif") if not str(det.get(k, "")).strip()]
        if missing:
            r.err("R9", where, f"missing concrete details: {', '.join(missing)} "
                               "(every shot needs an environmental pressure, a physical micro-action and a "
                               "sound/visual motif)")
        if not s.get("subject") or not s.get("action"):
            r.err("R9", where, "`subject` and `action` are required; they lead the prompt")
        if not s.get("final_image"):
            r.warn("R9", where, "no `final_image`; name the frame the shot ends on (it is the cut point)")

        text = _text_of(s).lower()
        # R10 filler words
        hits = sorted({f for f in FILLER if re.search(rf"\b{re.escape(f)}\b", text)})
        if hits:
            r.warn("R10", where, f"filler words that do not render: {', '.join(hits)}; replace with physical facts")
        # R11 one primary camera move
        moves = sorted({m.strip() for m in CAMERA_MOVES if m in f" {str(s.get('camera', '')).lower()} "})
        if not s.get("camera"):
            r.err("R11", where, "`camera` is required (shot size + lens or move)")
        elif len(moves) > 2:
            r.warn("R11", where, f"{len(moves)} camera moves ({', '.join(moves)}); keep one primary move per shot")
        # R12 audio direction
        if not (s.get("audio") or plan.get("style", {}).get("audio_bed")):
            r.err("R12", where, "no audio direction; Omni then invents a generic score. Set `audio` or style.audio_bed")
        # R13 English prompt fields
        toks = re.findall(r"[a-záéíóúñãõç]+", text)
        if toks and sum(t in NON_EN for t in toks) / len(toks) > NON_EN_RATIO:
            r.warn("R13", where, "prompt fields look non-English; Omni is only evaluated in English. "
                                 "Write prompt fields in English, keep the ad language in `supers`")
        # R14 dialogue
        dl = s.get("dialogue")
        if dl and dl.get("line"):
            n = words(dl["line"])
            if n > s.get("duration", 0) * SPEECH_WPS:
                r.err("R14", where, f"dialogue has {n} words for {s.get('duration')}s; max ~{SPEECH_WPS} words/s")
            if lang != "en":
                r.warn("R14", where, f"spoken `{lang}` dialogue is not evaluated by Google for Omni; "
                                     "test in draft, or use a recorded voiceover in assembly")
            if dl.get("speaker") and dl["speaker"] not in chars:
                r.err("R14", where, f"dialogue speaker `{dl['speaker']}` is not in `characters`")
        # R15 on-screen text
        if s.get("native_text") and lang != "en":
            r.err("R15", where, f"native_text asks the model to render text, but the ad language is `{lang}`. "
                                "Move it to `supers` (exact, overlaid in assembly)")
        # R16 characters
        for cid in s.get("characters", []):
            if cid not in chars:
                r.err("R16", where, f"character `{cid}` is not defined in `characters`")

    # R5 forks: one clip cannot be extended twice, and an edit cannot target mid-chain
    for src, kids in continued_by.items():
        if len(kids) > 1:
            r.err("R5", f"shot {src}", f"extended by several shots ({', '.join(kids)}); a chain cannot fork")
    edited_by: dict[str, list[str]] = {}
    for s in shots:
        if s.get("mode") == "edit" and s.get("edits"):
            edited_by.setdefault(s["edits"], []).append(s["id"])
            if s["edits"] in continued_by:
                r.err("R5", f"shot {s['id']}", f"edits `{s['edits']}`, which is extended later; edit the "
                                               "chain's last shot instead (its output holds the whole chain)")
    for tgt, kids in edited_by.items():
        if len(kids) > 1:
            r.err("R5", f"shot {tgt}", f"edited by several shots ({', '.join(kids)}); chain edits instead (e2 edits e1)")

    # R17 chain length
    for sid, s in idx.items():
        if s.get("mode") == "extend":
            chain = chain_of(plan, sid)
            total = sum(int(idx[c].get("duration", 0) or 0) for c in chain)
            if total > MAX_CHAIN_S:
                r.err("R17", f"shot {sid}", f"chain {'>'.join(chain)} is {total}s; Omni caps extensions at {MAX_CHAIN_S}s")

    # R16 identity drift
    for cid, c in chars.items():
        if not c.get("identity"):
            r.err("R16", f"character {cid}", "`identity` block is required (face, hair, wardrobe, accessories)")
        segs = [c_ for c_ in chains(plan) if any(cid in idx[x].get("characters", []) for x in c_)]
        if len(segs) > 1 and not c.get("ref_image"):
            r.warn("R16", f"character {cid}", f"appears in {len(segs)} separate generations with no `ref_image`; "
                                              "the face will drift between them. Keep the person inside one "
                                              "extend chain, show only hands/back in the other shot, or add a "
                                              "reference still of a generated person")
        if c.get("ref_image"):
            used_ref = any(any(x.get("path") == c["ref_image"] for x in s.get("image_refs", [])) or
                           s.get("first_frame") == c["ref_image"] for s in shots)
            if not used_ref:
                r.warn("R16", f"character {cid}", "`ref_image` is declared but no shot passes it as a reference")

    # R18 hook
    first = shots[0]
    if first.get("role") != "hook":
        r.err("R18", f"shot {first.get('id')}", "the first shot must have role `hook` (the scroll stop)")
    if shot_seconds(plan, first) > 5:
        r.warn("R18", f"shot {first.get('id')}", "hook shot is longer than 5s; make sure the stop lands in ~2s")
    fsup = sorted(first.get("supers", []), key=lambda x: x.get("start", 0))
    if fsup and float(fsup[0].get("start", 0)) > 1.0:
        r.warn("R18", f"shot {first.get('id')}", "first super starts after 1s; sound-off viewers need the hook text immediately")
    if fsup and words(fsup[0].get("text")) > HOOK_SUPER_WORDS:
        r.warn("R18", f"shot {first.get('id')}", f"hook super has {words(fsup[0].get('text'))} words; keep it <= {HOOK_SUPER_WORDS}")
    if not any(s.get("role") in ("reveal", "hero", "use", "macro") for s in shots):
        r.err("R18", "shots", "no shot shows the product (role reveal/hero/use/macro)")

    # R19 end card and length per placement
    ec = plan.get("end_card", {})
    if not ec.get("cta"):
        r.err("R19", "end_card", "`cta` is required")
    if not (1 <= float(ec.get("duration", 0) or 0) <= 4):
        r.err("R19", "end_card", "`duration` must be 1-4 s")
    for k in ("headline", "cta", "url"):
        if re.search(r"\.example\b|\bTBD\b|\bXXX\b|lorem|placeholder|<[^>]+>", str(ec.get(k, "")), re.I):
            r.warn("R19", "end_card", f"`{k}` looks like a placeholder ('{ec[k]}'); get the real value before a live final")
    total = planned_seconds(plan)
    for name in plan.get("placements", []):
        p = pl.get(name)
        if p and total > p["max_seconds"]:
            r.warn("R19", "placements", f"cut is {total:.0f}s; `{name}` performs best at <= {p['max_seconds']}s")

    # R20 compliance
    brief = plan.get("brief", {})
    for c in brief.get("claims", []):
        if isinstance(c, str) or not c.get("substantiation"):
            txt = c if isinstance(c, str) else c.get("text")
            r.warn("R20", "brief.claims", f"claim '{str(txt)[:40]}' has no `substantiation`; ad review may reject it")
    if brief.get("category") in ("political", "social_issue", "elections"):
        r.err("R20", "brief", "political/social-issue ads need platform authorization and special AI "
                              "disclosure; out of scope for this skill")
    realistic_people = any(c.get("realistic", True) for c in chars.values()) or any(s.get("dialogue") for s in shots)
    disc = plan.get("disclosure", {})
    if realistic_people and not disc.get("ai_label"):
        r.warn("R20", "disclosure", "realistic generated people: TikTok and YouTube require an AI label and Meta "
                                    "may auto-label. Set disclosure.ai_label true and tick the platform toggle")
    real_media = [s["id"] for s in shots if s.get("source_contains_people") or s.get("first_frame_contains_people")
                  or any(x.get("contains_people") for x in s.get("image_refs", []) + s.get("video_refs", []))]
    if brief.get("real_person_likeness") or real_media:
        who = f" (shots {', '.join(real_media)})" if real_media else ""
        if not brief.get("likeness_consent"):
            r.err("R20", "brief", f"a real, identifiable person appears{who}. Get their written consent for this "
                                  "use, then set brief.likeness_consent: true")
        else:
            r.warn("R20", "brief", f"real person{who}: consent recorded; keep the signed release on file")
    return r


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("plan")
    ap.add_argument("--region", default="", help="eu/eea/uk/ch enable regional upload checks (or OMNI_REGION)")
    ap.add_argument("--json", action="store_true")
    a = ap.parse_args()
    try:
        plan = load_json(a.plan)
    except Exception as e:  # noqa: BLE001
        print(f"ERROR: cannot read plan: {e}")
        return 2
    rep = validate(plan, a.plan, a.region)
    if a.json:
        print(json.dumps({"errors": len(rep.errors), "items": rep.items}, ensure_ascii=False, indent=2))
    else:
        for i in rep.items:
            print(f"{i['level']:5} {i['rule']:4} {i['where']}: {i['msg']}")
        n_w = len(rep.items) - len(rep.errors)
        secs = planned_seconds(plan)
        print(f"\n{len(rep.errors)} error(s), {n_w} warning(s). Planned cut: {secs:.0f}s.")
        print("PASS: build jobs next." if not rep.errors else "FAIL: fix every ERROR before building jobs.")
    return 1 if rep.errors else 0


if __name__ == "__main__":
    sys.exit(main())
