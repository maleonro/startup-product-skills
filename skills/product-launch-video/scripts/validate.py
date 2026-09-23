#!/usr/bin/env python3
"""Validate a launch-video storyboard.json before building it.

Usage: validate.py <storyboard.json> [--skip-files]

Exit 0 when there are no errors (warnings are printed but do not fail).
--skip-files skips the checks that need the asset files (existence, real size, duration).

Schema (all times in seconds, all rects [x, y, w, h] in SOURCE pixels of the asset):

{
  "fps": 30,
  "formats": ["16x9", "1x1"],                    # any of 16x9, 1x1, 9x16
  "productBox": {"16x9": [1600, 1000]},          # optional; defaults below
  "languages": ["en"],                           # every text field is keyed by language
  "cta": {"en": "Start free at example.com"},
  "bannedPhrases": ["nothing sends without"],     # optional, product-specific
  "assets": {
    "<id>": {
      "kind": "image" | "video" | "recreation",
      "path": "public/assets/x.png",             # relative to storyboard.json; not for recreation
      "width": 2880, "height": 1800,             # recreation: its design canvas size
      "duration": 12.4, "fps": 30,               # video only
      "builtFrom": "<image asset id>"            # recreation only; must be a real screenshot
    }
  },
  "scenes": [                                    # contiguous, in order
    {
      "id": "hook", "start": 0, "duration": 3,
      "mode": "screenshot" | "recording" | "recreation" | "card" | "endcard",
      "asset": "<asset id>",                     # not for card / endcard
      "text": {"en": "Your headline here"},           # optional headline
      "textHold": 3,                             # optional; seconds on screen, default = duration
      "focus": [{"at": 0, "rect": [0, 0, 2880, 1800]}],
      "focusByFormat": {"9x16": [{"at": 0, "rect": [...]}]},   # optional override
      "highlights": [[x, y, w, h]], "blur": [[x, y, w, h]],
      "startFrom": 0, "playbackRate": 1,         # recording only
      "speedLabel": {"en": "sped up 4x"}         # required when playbackRate > 1
    }
  ]
}
"""
import json
import os
import re
import shutil
import subprocess
import sys

DEFAULT_BOX = {"16x9": (1600, 1000), "1x1": (960, 720), "9x16": (960, 1200)}
PRODUCT_MODES = {"screenshot", "recording", "recreation"}
MODE_KIND = {"screenshot": "image", "recording": "video", "recreation": "recreation"}

# Generic banned on-screen text. Product-specific phrases go in storyboard.json as
# "bannedPhrases": [...] (copy them from references/products/<product>.md). Lower-case substrings.
BANNED = [
    "—",
    "unlock",
    "seamless",
    "supercharge",
    "ai-powered",
    "at scale",
]
EMOJI = re.compile("[\U0001F300-\U0001FAFF\U00002600-\U000027BF\U0001F000-\U0001F2FF️]")
X_NOT_Y = re.compile(r"\b\w+, not \w+", re.IGNORECASE)

errors, warnings = [], []


def err(where, msg):
    errors.append(f"{where}: {msg}")


def warn(where, msg):
    warnings.append(f"{where}: {msg}")


def inside(rect, w, h):
    x, y, rw, rh = rect
    return x >= 0 and y >= 0 and rw > 0 and rh > 0 and x + rw <= w and y + rh <= h


def ffprobe_cmd(cwd):
    if shutil.which("ffprobe"):
        return ["ffprobe"]
    if shutil.which("npx") and os.path.isdir(os.path.join(cwd, "node_modules", "@remotion")):
        return ["npx", "--no-install", "remotion", "ffprobe"]
    return None


def probe(cmd, path, cwd):
    out = subprocess.run(
        cmd + ["-v", "error", "-select_streams", "v:0",
               "-show_entries", "stream=width,height,r_frame_rate,avg_frame_rate,codec_name:format=duration",
               "-of", "json", path],
        cwd=cwd, capture_output=True, text=True,
    )
    if out.returncode != 0:
        return None
    data = json.loads(out.stdout or "{}")
    stream = (data.get("streams") or [{}])[0]
    fmt = data.get("format") or {}
    return {**stream, "duration": float(fmt["duration"]) if fmt.get("duration") else None}


def rate(r):
    if not r or r == "0/0":
        return 0.0
    n, d = r.split("/")
    return float(n) / float(d) if float(d) else 0.0


def texts(sb, value):
    """All language strings of a text field."""
    if value is None:
        return []
    if isinstance(value, str):
        return [value]
    return [value.get(lang, "") for lang in sb.get("languages", ["en"])]


def check_text(where, s):
    low = s.lower()
    for phrase in BANNED:
        if phrase in low:
            err(where, f"banned phrase {phrase!r} in {s!r}")
    if EMOJI.search(s):
        err(where, f"emoji in {s!r}")
    if X_NOT_Y.search(s):
        warn(where, f"possible 'X, not Y' construction in {s!r}")


def main():
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    skip_files = "--skip-files" in sys.argv
    if len(args) != 1:
        print(__doc__)
        sys.exit(2)
    path = os.path.abspath(args[0])
    base = os.path.dirname(path)
    with open(path) as f:
        sb = json.load(f)

    BANNED.extend(p.lower() for p in sb.get("bannedPhrases", []))
    langs = sb.get("languages", ["en"])
    formats = sb.get("formats", ["16x9", "1x1"])
    boxes = {k: tuple(v) for k, v in {**DEFAULT_BOX, **sb.get("productBox", {})}.items()}
    assets = sb.get("assets", {})
    scenes = sb.get("scenes", [])
    if not scenes:
        err("storyboard", "no scenes")

    for fmt in formats:
        if fmt not in DEFAULT_BOX:
            err("formats", f"unknown format {fmt!r}")

    # ---- assets
    cmd = None if skip_files else ffprobe_cmd(base)
    if not skip_files and cmd is None:
        warn("assets", "no ffprobe and no local Remotion install; real sizes not checked")
    for aid, a in assets.items():
        where = f"asset {aid}"
        kind = a.get("kind")
        if kind not in ("image", "video", "recreation"):
            err(where, f"kind must be image, video or recreation, got {kind!r}")
            continue
        if kind == "recreation":
            src = assets.get(a.get("builtFrom", ""))
            if not src or src.get("kind") != "image":
                err(where, "a recreation must name the real screenshot it was built from (builtFrom)")
            continue
        if skip_files:
            continue
        full = os.path.join(base, a.get("path", ""))
        if not a.get("path") or not os.path.isfile(full):
            err(where, f"file not found: {a.get('path')}")
            continue
        if cmd is None:
            continue
        p = probe(cmd, full, base)
        if not p:
            err(where, "ffprobe could not read the file")
            continue
        if (p.get("width"), p.get("height")) != (a.get("width"), a.get("height")):
            err(where, f"declared {a.get('width')}x{a.get('height')}, real {p.get('width')}x{p.get('height')}")
        if kind == "video":
            if p.get("duration") and abs(p["duration"] - a.get("duration", 0)) > 0.1:
                err(where, f"declared duration {a.get('duration')}, real {p['duration']:.2f}")
            r, avg = rate(p.get("r_frame_rate")), rate(p.get("avg_frame_rate"))
            if avg and avg < 24:
                err(where, f"{avg:.1f}fps is under 24fps")
            if r and avg and abs(r - avg) > 0.5:
                err(where, f"variable frame rate ({r:.2f} vs {avg:.2f}); transcode with -r 30")
            if p.get("codec_name") in ("hevc", "prores"):
                err(where, f"{p['codec_name']} codec; transcode to h264")

    # ---- scenes
    t = 0.0
    total = 0.0
    first_product = None
    for i, s in enumerate(scenes):
        where = f"scene {s.get('id', i)}"
        start, dur, mode = s.get("start", 0), s.get("duration", 0), s.get("mode")
        if abs(start - t) > 0.01:
            err(where, f"starts at {start}s, expected {t:.2f}s (scenes must be contiguous)")
        t = start + dur
        total = t
        if mode not in PRODUCT_MODES | {"card", "endcard"}:
            err(where, f"unknown mode {mode!r}")
            continue
        if mode == "endcard":
            if dur < 2:
                err(where, f"end card is {dur}s; needs at least 2s")
            if i != len(scenes) - 1:
                err(where, "the end card must be the last scene")
            for lang in langs:
                cta = (sb.get("cta") or {}).get(lang)
                body = " ".join(texts(sb, s.get("text")) + texts(sb, s.get("cta")))
                if not cta:
                    err("cta", f"no CTA for language {lang}")
                elif cta not in body:
                    err(where, f"end card does not contain the exact CTA {cta!r} ({lang})")
        elif not 1.5 <= dur <= 8:
            err(where, f"{dur}s is outside 1.5-8s")
        elif not 2 <= dur <= 6:
            warn(where, f"{dur}s is outside the ideal 2-6s")
        if mode == "card" and dur >= 3:
            err(where, f"a card must be under 3s, got {dur}s")

        # text
        hold = s.get("textHold", dur)
        if hold > dur:
            err(where, f"textHold {hold}s is longer than the scene ({dur}s)")
        for lang in langs:
            txt = (s.get("text") or {}).get(lang) if isinstance(s.get("text"), dict) else s.get("text")
            if s.get("text") is not None and not txt:
                err(where, f"missing text for language {lang}")
                continue
            if not txt:
                continue
            check_text(where, txt)
            words = len(txt.split())
            if mode != "endcard" and words > 7:
                err(where, f"headline has {words} words (max 7): {txt!r} ({lang})")
            need = words / 3 + 1
            if hold + 1e-6 < need:
                err(where, f"headline needs {need:.1f}s on screen, gets {hold}s ({lang})")
        for txt in texts(sb, s.get("speedLabel")):
            check_text(where, txt)

        if mode in PRODUCT_MODES:
            if first_product is None:
                first_product = start
            a = assets.get(s.get("asset", ""))
            if not a:
                err(where, f"asset {s.get('asset')!r} is not declared")
                continue
            if a.get("kind") != MODE_KIND[mode]:
                err(where, f"mode {mode} needs a {MODE_KIND[mode]} asset, got {a.get('kind')}")
            aw, ah = a.get("width", 0), a.get("height", 0)
            for rect in s.get("highlights", []) + s.get("blur", []):
                if not inside(rect, aw, ah):
                    err(where, f"rect {rect} is outside the asset ({aw}x{ah})")
            for fmt in formats:
                keys = (s.get("focusByFormat") or {}).get(fmt) or s.get("focus") or [
                    {"at": 0, "rect": [0, 0, aw, ah]}]
                bw, bh = boxes[fmt]
                for k in keys:
                    rect = k.get("rect")
                    if not rect or not inside(rect, aw, ah):
                        err(where, f"{fmt}: focus rect {rect} is outside the asset ({aw}x{ah})")
                        continue
                    if not 0 <= k.get("at", 0) <= dur:
                        err(where, f"{fmt}: focus keyframe at {k.get('at')}s is outside the scene")
                    if mode != "recreation" and rect[2] < bw:
                        err(where, f"{fmt}: focus rect is {rect[2]}px wide, box is {bw}px: that upscales")
                    if fmt == "9x16" and mode != "recreation" and aw > ah and rect[2] / rect[3] > 0.8 + 1e-6:
                        err(where, "9x16: horizontal asset needs a focus rect of 4:5 or taller, or a recreation")
            if mode == "recording":
                rate_ = s.get("playbackRate", 1)
                need = s.get("startFrom", 0) + dur * rate_
                if a.get("duration") is not None and need > a["duration"] + 1e-6:
                    err(where, f"needs {need:.2f}s of recording, asset has {a['duration']}s")
                if rate_ > 1:
                    labels = texts(sb, s.get("speedLabel"))
                    if not labels or not all(re.search(r"\d", x) for x in labels):
                        err(where, f"playbackRate {rate_} needs a speedLabel like 'sped up {rate_:g}x'")

    if first_product is None:
        err("storyboard", "no scene shows the product")
    elif first_product > 0:
        if first_product >= 3:
            err("storyboard", f"product first appears at {first_product}s; must be before 3s")
        else:
            warn("storyboard", f"frame 0 is not the product (it appears at {first_product}s); frame 0 is the thumbnail")
    if total > 60:
        err("storyboard", f"total is {total:.1f}s; max 60s")
    if not scenes or scenes[-1].get("mode") != "endcard":
        err("storyboard", "the last scene must be an endcard")

    for w in warnings:
        print(f"WARN  {w}")
    for e in errors:
        print(f"ERROR {e}")
    print(f"{len(errors)} error(s), {len(warnings)} warning(s), {total:.1f}s total")
    sys.exit(1 if errors else 0)


if __name__ == "__main__":
    main()
