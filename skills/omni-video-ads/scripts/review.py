#!/usr/bin/env python3
"""Quality control for generated clips and finished cuts, plus the lessons log.

Usage:
  review.py clips   out/adplan/draft               # contact sheet + probe + qc.json per shot
  review.py cut     out/adplan/draft               # per placement: safe-zone frames + automatic checks
  review.py compare out/adplan/draft out/adplan/final     # draft vs final similarity (after promote)
  review.py lessons                         # print seed + accumulated lessons (step 2)
  review.py lesson  --category hook --lesson "..." --evidence "..." [--score 3] [--model ...]

Lessons accumulate in $LESSONS_PATH, default ~/.omni-video-ads/LESSONS.md (outside the skill, which
may be read-only); the skill's own LESSONS.md holds the seed lessons.

`clips` and `cut` write images for you to LOOK at (Read the .jpg files) and a qc.json
to fill in. Scores are yours; the script only checks what is measurable.
"""
from __future__ import annotations

import argparse
import datetime as dt
import os
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from PIL import Image, ImageDraw, ImageFont  # noqa: E402

from lib.common import SKILL_DIR, aspect_of, load_json, load_or_exit, need, probe, run, save_json  # noqa: E402
from lib.render import font_path, safe_guide  # noqa: E402

HOOK_TIMES = (0.0, 0.5, 1.0, 2.0)  # what a scroller sees before deciding (~2 s)
SPREAD = 6  # evenly spaced frames after the hook: one every ~0.5-1.7 s for 3-10 s clips
DURATION_TOL_CLIP = 1.0  # s; Omni rounds clip length, a >1 s miss means the request was ignored
DURATION_TOL_CUT = 0.5   # s; assembled cuts are deterministic, so anything beyond encoder padding is a bug
LUFS_WINDOW = (-17, -11)  # +-3 LU around the -14 target; platforms re-normalise outside this
BLACK_MIN_S, BLACK_PIX = 0.3, 0.08  # a black gap under 0.3 s reads as a cut; 8% luma = near-black
# Mean 32x32 grey similarity. Not yet calibrated on real Omni re-rolls: set conservatively so a
# re-roll is flagged; adjust after the first promote runs and log the value in LESSONS.md.
SAME_TAKE = 0.85
SCORE_KEYS = ["prompt_fidelity", "hook_strength", "product_fidelity", "subject_consistency",
              "motion_quality", "audio_match", "overall"]


def grab(clip: str, t: float, dst: Path, width: int = 360) -> Path:
    run(["ffmpeg", "-y", "-v", "error", "-ss", f"{t:.3f}", "-i", clip, "-frames:v", "1",
         "-vf", f"scale={width}:-2", str(dst)])
    return dst


def sheet(frames: list[tuple[float, Path]], dst: Path, cols: int = 5, title: str = "") -> Path:
    imgs = [(t, Image.open(p).convert("RGB")) for t, p in frames if p.exists()]
    if not imgs:
        raise RuntimeError("no frames extracted")
    w, h = imgs[0][1].size
    rows = (len(imgs) + cols - 1) // cols
    head = 36
    canvas = Image.new("RGB", (cols * w, rows * (h + 24) + head), (20, 20, 20))
    d = ImageDraw.Draw(canvas)
    f = ImageFont.truetype(font_path(), 18)
    d.text((8, 8), title, font=f, fill=(255, 255, 255))
    for i, (t, im) in enumerate(imgs):
        x, y = (i % cols) * w, head + (i // cols) * (h + 24)
        canvas.paste(im.resize((w, h)), (x, y))
        d.text((x + 6, y + h + 2), f"{t:.1f}s", font=f, fill=(230, 230, 230))
    canvas.save(dst, quality=88)
    return dst


def cmd_clips(a) -> int:
    need("ffmpeg")
    work = Path(a.workdir)
    log = load_or_exit(work / "runlog.json", "runlog", "Run generate.py first").get("shots", {})
    jobs = {j["shot"]: j for j in load_or_exit(work / "jobs.json", "jobs file")["jobs"]}
    out_all = []
    for sid, e in log.items():
        if e.get("status") != "ok":
            continue
        clip = e["output"]
        info = probe(clip)
        d = work / "qc" / sid
        d.mkdir(parents=True, exist_ok=True)
        dur = info["duration"]
        job = jobs.get(sid, {})
        # An extension clip also holds the earlier shots: sample only its new part.
        new_from = max(0.0, dur - float(job.get("duration") or dur)) if job.get("mode") == "extend" else 0.0
        hook = {round(min(new_from + t, max(dur - 0.05, 0)), 2) for t in HOOK_TIMES}
        spread = {round(new_from + (dur - new_from) * (k + 0.5) / SPREAD, 2) for k in range(SPREAD)}
        times = sorted(hook | spread)
        frames = [(t, grab(clip, t, d / f"frame_{t:05.2f}.jpg")) for t in times]
        cs = sheet(frames, d / "contact_sheet.jpg", title=f"{sid} | {e.get('mode')} | {info['width']}x{info['height']} | {dur:.1f}s")
        checks, notes = [], []
        req = job.get("duration")
        if job.get("mode") == "extend":
            notes.append(f"extension clip is {dur:.1f}s including earlier shots; sheet samples the new part from {new_from:.1f}s")
        elif req and abs(dur - req) > DURATION_TOL_CLIP:
            checks.append(f"duration {dur:.1f}s vs requested {req}s")
        if job.get("aspect_ratio") and aspect_of(info["width"], info["height"]) != job["aspect_ratio"]:
            checks.append(f"aspect {aspect_of(info['width'], info['height'])} vs requested {job['aspect_ratio']}")
        if not info["has_audio"]:
            checks.append("no audio track")
        qc_path = d / "qc.json"
        prev = load_json(qc_path) if qc_path.exists() else {}
        qc = {"shot": sid, "clip": clip, "interaction_id": e.get("interaction_id"), "probe": info,
              "auto_checks": checks, "info": notes, "contact_sheet": str(cs),
              "scores": prev.get("scores") or {k: None for k in SCORE_KEYS},
              "failure_modes": prev.get("failure_modes", []), "notes": prev.get("notes", ""),
              "prompt": job.get("prompt")}
        save_json(qc_path, qc)
        out_all.append((sid, cs, checks))
    for sid, cs, checks in out_all:
        flag = "; ".join(checks) if checks else "auto checks ok"
        print(f"[{sid}] {cs} :: {flag}")
    print("Now Read each contact_sheet.jpg, score it in qc.json (1-5), and log one lesson per failure.")
    return 0


def loudness(path: str) -> float | None:
    res = run(["ffmpeg", "-hide_banner", "-nostats", "-i", path, "-af", "ebur128", "-f", "null", "-"])
    m = re.findall(r"I:\s+(-?[\d.]+) LUFS", res.stderr)
    return float(m[-1]) if m else None


def black_segments(path: str) -> list[tuple[float, float]]:
    res = run(["ffmpeg", "-hide_banner", "-nostats", "-i", path, "-vf", f"blackdetect=d={BLACK_MIN_S}:pix_th={BLACK_PIX}",
               "-an", "-f", "null", "-"])
    return [(float(s), float(e)) for s, e in re.findall(r"black_start:([\d.]+) black_end:([\d.]+)", res.stderr)]


def inside(box, rect) -> bool:
    return box[0] >= rect[0] and box[1] >= rect[1] and box[2] <= rect[2] and box[3] <= rect[3]


def cmd_cut(a) -> int:
    need("ffmpeg")
    work = Path(a.workdir)
    man = load_or_exit(work / "deliverables" / "manifest.json", "manifest", "Run assemble.py first")
    worst = 0
    report = {}
    for pname, m in man["placements"].items():
        d = work / "qc" / "cut" / pname
        d.mkdir(parents=True, exist_ok=True)
        w, h = m["width"], m["height"]
        s = m["safe"]
        rect = (int(w * s["left"]), int(h * s["top"]), int(w * (1 - s["right"])), int(h * (1 - s["bottom"])))
        issues = []
        for su in m["supers"]:
            if not inside(su["box"], rect):
                issues.append(f"super '{su['text'][:30]}' box {su['box']} leaves the safe area {rect}")
        # hook frames, every super, the middle of every segment (so product shots are always
        # seen), and the end card
        times = [0.0, 1.0] + [round((su["start"] + su["end"]) / 2, 2) for su in m["supers"]]
        t0 = 0.0
        for seg in man.get("segments", []):
            times.append(round(t0 + seg["actual"] / 2, 2))
            t0 += seg["actual"]
        times += [max(m["duration"] - 0.5, 0)]
        frames = []
        for t in sorted(set(times)):
            raw = grab(m["file"], t, d / f"raw_{t:05.2f}.jpg", width=w)
            g = safe_guide(Image.open(raw), s)
            g.thumbnail((360, 640 if h > w else 360))
            p = d / f"guide_{t:05.2f}.jpg"
            g.save(p, quality=88)
            raw.unlink()
            frames.append((t, p))
        cs = sheet(frames, d / "safe_zone_sheet.jpg", cols=6, title=f"{pname} {w}x{h} {m['duration']:.1f}s (red = platform UI)")
        lufs = loudness(m["file"])
        if lufs is not None and not (LUFS_WINDOW[0] <= lufs <= LUFS_WINDOW[1]):
            issues.append(f"integrated loudness {lufs:.1f} LUFS (target -14)")
        blacks = [b for b in black_segments(m["file"]) if b[0] > 0.05]
        if blacks:
            issues.append(f"black frames at {', '.join(f'{b0:.1f}-{b1:.1f}s' for b0, b1 in blacks)}")
        expected = man["body_seconds"] + m.get("end_card_seconds", 0)
        if abs(m["duration"] - expected) > DURATION_TOL_CUT:
            issues.append(f"duration {m['duration']:.1f}s vs expected {expected:.1f}s")
        if (w, h) != tuple(plan_size(pname)):
            issues.append(f"size {w}x{h} does not match the placement spec")
        report[pname] = {"file": m["file"], "sheet": str(cs), "lufs": lufs, "issues": issues}
        worst = max(worst, len(issues))
        print(f"[{pname}] {cs} :: {'; '.join(issues) if issues else 'auto checks ok'}")
    save_json(work / "qc" / "cut" / "qc_cut.json", report)
    print("Read every safe_zone_sheet.jpg: hook readable at 0-1s, product visible, no text under red UI areas.")
    return 1 if worst else 0


def plan_size(pname: str):
    from lib.common import placements
    return placements()[pname]["size"]


def cmd_compare(a) -> int:
    need("ffmpeg")
    dlog = load_or_exit(Path(a.draft) / "runlog.json", "draft runlog")["shots"]
    flog = load_or_exit(Path(a.final) / "runlog.json", "final runlog")["shots"]
    d = Path(a.final) / "qc" / "compare"
    d.mkdir(parents=True, exist_ok=True)
    rc = 0
    for sid, fe in flog.items():
        de = dlog.get(sid)
        if not de or fe.get("status") != "ok":
            continue
        dur = min(probe(de["output"])["duration"], probe(fe["output"])["duration"])
        diffs = []
        for k in range(5):
            t = dur * (k + 0.5) / 5
            x = Image.open(grab(de["output"], t, d / f"{sid}_d{k}.jpg", 64)).convert("L").resize((32, 32))
            y = Image.open(grab(fe["output"], t, d / f"{sid}_f{k}.jpg", 64)).convert("L").resize((32, 32))
            diffs.append(sum(abs(p - q) for p, q in zip(x.getdata(), y.getdata())) / (32 * 32 * 255))
        sim = round(1 - sum(diffs) / len(diffs), 3)
        verdict = "same take" if sim >= SAME_TAKE else "DIFFERENT take"
        if sim < SAME_TAKE:
            rc = 1
        print(f"[{sid}] similarity {sim} -> {verdict}")
    return rc


def lessons_path() -> Path:
    return Path(os.environ.get("LESSONS_PATH") or Path.home() / ".omni-video-ads" / "LESSONS.md")


def cmd_lessons(a) -> int:
    print((SKILL_DIR / "LESSONS.md").read_text(encoding="utf-8"))
    p = lessons_path()
    if p.exists():
        print(f"\n## Your accumulated lessons ({p})\n")
        print(p.read_text(encoding="utf-8"))
    else:
        print(f"\n(no accumulated lessons yet; they will be written to {p})")
    return 0


def cmd_lesson(a) -> int:
    path = lessons_path()
    if a.score is not None and not (1 <= a.score <= 5):
        print("score must be 1-5")
        return 1
    if len(a.lesson.split()) < 6:
        print("A lesson is a generalizable cause -> effect rule; write a full sentence.")
        return 1
    day = dt.date.today().isoformat()
    score = f" · overall {a.score}/5" if a.score is not None else ""
    path.parent.mkdir(parents=True, exist_ok=True)
    if not path.exists():
        path.write_text("# Accumulated lessons (omni-video-ads)\n", encoding="utf-8")
    entry = (f"\n- {day} · {a.model} · {a.category}{score}\n"
             f"  LESSON: {a.lesson.strip()}\n  EVIDENCE: {a.evidence.strip()}\n")
    with open(path, "a", encoding="utf-8") as fh:
        fh.write(entry)
    print(f"Appended to {path}")
    return 0


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)
    p = sub.add_parser("clips")
    p.add_argument("workdir")
    p = sub.add_parser("cut")
    p.add_argument("workdir")
    p = sub.add_parser("compare")
    p.add_argument("draft")
    p.add_argument("final")
    sub.add_parser("lessons")
    p = sub.add_parser("lesson")
    p.add_argument("--model", default="gemini-omni-1.1-flash")
    p.add_argument("--category", required=True)
    p.add_argument("--score", type=int, default=None, help="1-5 overall score of the clip, if the lesson is about one")
    p.add_argument("--lesson", required=True)
    p.add_argument("--evidence", required=True)
    a = ap.parse_args()
    return {"clips": cmd_clips, "cut": cmd_cut, "compare": cmd_compare, "lesson": cmd_lesson, "lessons": cmd_lessons}[a.cmd](a)


if __name__ == "__main__":
    sys.exit(main())
