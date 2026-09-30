"""Shared helpers for the omni-video-ads scripts. Standard library only."""
from __future__ import annotations

import json
import os
import re
import shutil
import subprocess
import sys
from functools import lru_cache
from pathlib import Path

SKILL_DIR = Path(__file__).resolve().parents[2]
ASSETS = SKILL_DIR / "assets"

VALID_ASPECTS = ("9:16", "16:9")
VALID_RESOLUTIONS = ("360p", "720p", "1080p", "4k")
# Omni generates 3-10 s per call (Gemini API docs, Omni 1.1, Aug 2026).
MIN_SHOT_S, MAX_SHOT_S = 3, 10
# Extensions add up to 10 s per turn, cumulative cap 40 s.
MAX_CHAIN_S = 40
MAX_IMAGE_REFS = 6
MAX_VIDEO_REFS = 3
MAX_VIDEO_REF_S = 3.0
MAX_UPLOAD_VIDEO_S = 10.0

# `recorded` = an existing clip cut in as-is (no generation, no spend).
MODES = ("text_to_video", "first_frame", "first_last", "reference", "extend", "edit", "recorded")
GENERATED_MODES = MODES[:-1]
ROLES = ("hook", "problem", "setup", "reveal", "macro", "use", "reaction", "proof", "hero", "transition")
# Regions where Omni refuses uploaded-video edit/extend and uploads of recognizable people.
RESTRICTED_REGIONS = ("eu", "eea", "uk", "ch")


def load_json(path: str | Path) -> dict | list:
    with open(path, encoding="utf-8") as fh:
        return json.load(fh)


def load_or_exit(path: str | Path, what: str, hint: str = "") -> dict | list:
    """Load JSON for a CLI; print a one-line reason and exit 2 instead of a traceback."""
    p = Path(path)
    if not p.exists():
        sys.exit(f"ERROR: {what} not found: {p}" + (f". {hint}" if hint else ""))
    try:
        return load_json(p)
    except json.JSONDecodeError as e:
        sys.exit(f"ERROR: {what} is not valid JSON ({p}, line {e.lineno}, col {e.colno}): {e.msg}")


def save_json(path: str | Path, data) -> None:
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", encoding="utf-8") as fh:
        json.dump(data, fh, ensure_ascii=False, indent=2)
        fh.write("\n")


def placements() -> dict:
    data = load_json(ASSETS / "placements.json")
    return {k: v for k, v in data.items() if not k.startswith("_")}


def resolve(plan_path: str | Path, maybe_rel: str | None) -> Path | None:
    """Resolve a media path in a plan relative to the plan file's folder."""
    if not maybe_rel:
        return None
    p = Path(maybe_rel)
    return p if p.is_absolute() else (Path(plan_path).resolve().parent / p)


def words(text: str | None) -> int:
    return len(re.findall(r"\S+", text or ""))


def shot_index(plan: dict) -> dict:
    return {s["id"]: s for s in plan.get("shots", []) if isinstance(s, dict) and "id" in s}


def chain_of(plan: dict, shot_id: str) -> list[str]:
    """Return the chain ending at shot_id, root first, following `continues` links."""
    idx = shot_index(plan)
    chain, seen, cur = [], set(), shot_id
    while cur and cur in idx and cur not in seen:
        seen.add(cur)
        chain.append(cur)
        s = idx[cur]
        cur = s.get("continues") if s.get("mode") == "extend" else None
    return list(reversed(chain))


def attach_path(plan: dict, plan_path: str | Path) -> dict:
    """Remember where the plan lives so media paths and source durations resolve."""
    plan["__path__"] = str(Path(plan_path).resolve())
    return plan


@lru_cache(maxsize=64)
def _media_seconds(path: str) -> float:
    try:
        return probe(path)["duration"] if Path(path).exists() and which("ffprobe") else 0.0
    except RuntimeError:
        return 0.0


def source_seconds(plan: dict, shot: dict) -> float:
    """Length of the uploaded or recorded clip a shot starts from (after `trim`)."""
    if not shot.get("source_video"):
        return 0.0
    trim = shot.get("trim")
    if trim and len(trim) == 2:
        return max(0.0, float(trim[1]) - float(trim[0]))
    base = plan.get("__path__")
    p = resolve(base, shot["source_video"]) if base else Path(shot["source_video"])
    return _media_seconds(str(p))


def own_segment(shot: dict) -> bool:
    """Edit shots replace their target, except an edit of an uploaded clip, which
    stands on the timeline by itself."""
    return not (shot.get("mode") == "edit" and shot.get("edits"))


def shot_seconds(plan: dict, shot: dict) -> float:
    """Seconds this shot occupies on the cut."""
    mode = shot.get("mode", "text_to_video")
    if mode == "recorded":
        return source_seconds(plan, shot)
    if mode == "edit":
        return source_seconds(plan, shot) if shot.get("source_video") and not shot.get("edits") else 0.0
    secs = float(shot.get("duration", 0) or 0)
    if mode == "extend" and shot.get("source_video") and not shot.get("continues"):
        secs += source_seconds(plan, shot)
    return secs


def chains(plan: dict) -> list[list[str]]:
    """Group shots into timeline segments. An extend shot joins the chain it continues;
    an edit shot replaces its target and is not a segment of its own."""
    idx = shot_index(plan)
    continued = {s.get("continues") for s in idx.values() if s.get("mode") == "extend"}
    out = []
    for sid, s in idx.items():
        if not own_segment(s):
            continue
        if sid in continued:
            continue  # not the tail of its chain
        out.append(chain_of(plan, sid))
    # keep plan order by the chain root
    order = {sid: i for i, sid in enumerate(idx)}
    out.sort(key=lambda c: order[c[0]])
    return out


def segments(plan: dict) -> list[dict]:
    """Timeline segments of the final cut, in order. Each segment is one chain; its
    clip comes from the chain tail's output, or from the last edit shot that targets
    that tail. Returns [{"shots": [...], "source": shot_id, "planned": s}]."""
    idx = shot_index(plan)
    out = []
    for chain in chains(plan):
        src = chain[-1]
        # follow edits of edits: s1 <- e1 <- e2
        changed = True
        while changed:
            changed = False
            for sid, s in idx.items():
                if s.get("mode") == "edit" and s.get("edits") == src:
                    src, changed = sid, True
                    break
        out.append({"shots": chain, "source": src,
                    "planned": sum(shot_seconds(plan, idx[c]) for c in chain)})
    return out


def timeline(plan: dict) -> list[dict]:
    """Planned timeline: one entry per shot with its start offset in the final cut."""
    idx = shot_index(plan)
    t, out = 0.0, []
    for chain in chains(plan):
        for sid in chain:
            d = shot_seconds(plan, idx[sid])
            out.append({"id": sid, "start": t, "end": t + d})
            t += d
    return out


def planned_seconds(plan: dict) -> float:
    tl = timeline(plan)
    body = tl[-1]["end"] if tl else 0.0
    return body + float((plan.get("end_card") or {}).get("duration", 0))


def which(tool: str) -> bool:
    return shutil.which(tool) is not None


def need(tool: str) -> None:
    if not which(tool):
        sys.exit(f"ERROR: `{tool}` not found on PATH. Run scripts/check_env.sh for install hints.")


def run(cmd: list[str], quiet: bool = True) -> subprocess.CompletedProcess:
    res = subprocess.run(cmd, capture_output=True, text=True)
    if res.returncode != 0:
        tail = "\n".join(res.stderr.strip().splitlines()[-12:])
        raise RuntimeError(f"command failed: {' '.join(cmd[:6])} ...\n{tail}")
    return res


def probe(path: str | Path) -> dict:
    """Duration, size, fps and audio presence of a media file via ffprobe."""
    need("ffprobe")
    res = run(["ffprobe", "-v", "error", "-print_format", "json", "-show_streams", "-show_format", str(path)])
    data = json.loads(res.stdout)
    v = next((s for s in data.get("streams", []) if s.get("codec_type") == "video"), {})
    a = [s for s in data.get("streams", []) if s.get("codec_type") == "audio"]
    fps = 0.0
    if v.get("avg_frame_rate") and v["avg_frame_rate"] != "0/0":
        n, d = v["avg_frame_rate"].split("/")
        fps = float(n) / float(d) if float(d) else 0.0
    return {
        "duration": float(data.get("format", {}).get("duration", 0) or 0),
        "width": int(v.get("width", 0) or 0),
        "height": int(v.get("height", 0) or 0),
        "fps": round(fps, 3),
        "has_audio": bool(a),
    }


def aspect_of(w: int, h: int) -> str:
    if not w or not h:
        return "?"
    r = w / h
    if abs(r - 9 / 16) < 0.02:
        return "9:16"
    if abs(r - 16 / 9) < 0.02:
        return "16:9"
    if abs(r - 1) < 0.02:
        return "1:1"
    if abs(r - 4 / 5) < 0.02:
        return "4:5"
    return f"{w}x{h}"


def region() -> str:
    return (os.environ.get("OMNI_REGION") or "").strip().lower()
