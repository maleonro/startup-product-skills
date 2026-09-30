#!/usr/bin/env python3
"""Assemble generated clips into finished ads, one file per placement.

Usage:
  assemble.py adplan.json --pass draft|final [--out out/<plan name>] [--voiceover vo.wav] [--music bed.mp3]

For each timeline segment it takes the chain tail (or its latest edit), detects whether
extensions came back cumulative, normalises every clip to the master frame, cuts them
together, then per placement: crops, overlays the supers inside that placement's safe
area, appends the end card, adds the AI disclosure if set, mixes audio and loudness-
normalises to -14 LUFS. Writes <out>/<pass>/deliverables/*.mp4 and manifest.json.
"""
from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from lib.common import attach_path, load_json, load_or_exit, need, resolve, shot_seconds, placements, probe, run, save_json, segments, shot_index  # noqa: E402
from lib.render import render_disclosure, render_end_card, render_super  # noqa: E402


def main() -> int:
    try:
        return _main()
    except RuntimeError as e:  # ffmpeg failures and missing fonts arrive here
        print(f"ERROR: {e}")
        return 1

# 30 fps: accepted by every placement; Omni's 24 fps clips convert without visible judder.
FPS = 30
# An extension output >= 80% of the planned chain length already contains the earlier shots
# (Omni retouches a few frames at the join, so exact equality never holds).
CUMULATIVE_RATIO = 0.8
# -14 LUFS integrated / -1.5 dBTP: what Meta, TikTok and YouTube normalise to, so ads are not
# turned down (too loud) or sound weak (too quiet) next to organic content.
LOUDNESS = "loudnorm=I=-14:TP=-1.5:LRA=11"
# Intermediate encodes are near-lossless (CRF 16) because they are re-encoded once more;
# deliverables at CRF 17 stay visually lossless while keeping files well under platform caps.
CRF_WORK, CRF_DELIVER = "16", "17"
AUDIO_BITRATE = "192k"  # AAC stereo 192k: transparent for speech and music, accepted everywhere
# When a voiceover or music is mixed in, Omni's own audio drops to 35% (about -9 dB) so SFX stay
# audible under the voice; music beds sit at 50% (about -6 dB) under a voiceover.
MODEL_AUDIO_GAIN, MUSIC_GAIN, VOICE_GAIN = 0.35, 0.5, 1.0


def slug(text: str) -> str:
    return re.sub(r"[^a-z0-9]+", "-", text.lower()).strip("-") or "ad"


def master_size(plan: dict) -> tuple[int, int]:
    return (1080, 1920) if plan.get("master_aspect", "9:16") == "9:16" else (1920, 1080)


def normalise(src: str, dst: Path, size: tuple[int, int], trim: list | None = None) -> float:
    """Scale/pad to the master frame at FPS with a stereo 48 kHz track (silence if none).
    `trim` = [start_s, end_s] cuts a recorded clip first."""
    w, h = size
    info = probe(src)
    vf = (f"scale={w}:{h}:force_original_aspect_ratio=decrease,pad={w}:{h}:(ow-iw)/2:(oh-ih)/2:black,"
          f"setsar=1,fps={FPS},format=yuv420p")
    cut = ["-ss", str(trim[0]), "-to", str(trim[1])] if trim else []
    cmd = ["ffmpeg", "-y", "-v", "error", *cut, "-i", src]
    if not info["has_audio"]:
        cmd += ["-f", "lavfi", "-i", "anullsrc=channel_layout=stereo:sample_rate=48000"]
        amap = ["-map", "0:v", "-map", "1:a", "-shortest"]
    else:
        amap = ["-map", "0:v", "-map", "0:a"]
    cmd += ["-vf", vf, *amap, "-c:v", "libx264", "-preset", "veryfast", "-crf", CRF_WORK,
            "-c:a", "aac", "-ar", "48000", "-ac", "2", "-b:a", AUDIO_BITRATE, str(dst)]
    run(cmd)
    return probe(dst)["duration"]


def concat(files: list[Path], dst: Path) -> None:
    lst = dst.with_suffix(".txt")
    lst.write_text("".join(f"file '{f.resolve()}'\n" for f in files))
    run(["ffmpeg", "-y", "-v", "error", "-f", "concat", "-safe", "0", "-i", str(lst),
         "-c:v", "libx264", "-preset", "veryfast", "-crf", CRF_WORK, "-c:a", "aac", "-b:a", AUDIO_BITRATE, str(dst)])
    lst.unlink()


def crop_filter(master: tuple[int, int], target: tuple[int, int], anchor: float) -> str:
    mw, mh = master
    tw, th = target
    if (tw, th) == (mw, mh):
        return "null"
    # crop the largest target-aspect window, then scale to target
    if tw / th < mw / mh:  # target narrower than master: crop width
        cw, ch = int(mh * tw / th) // 2 * 2, mh
        x, y = f"(iw-{cw})*{anchor}", "0"
    else:  # target shorter: crop height
        cw, ch = mw, int(mw * th / tw) // 2 * 2
        x, y = "0", f"(ih-{ch})*{anchor}"
    return f"crop={cw}:{ch}:{x}:{y},scale={tw}:{th}"


def _main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("plan")
    ap.add_argument("--pass", dest="pass_name", choices=("draft", "final"), required=True)
    ap.add_argument("--out", default=None, help="output folder (default: out/<plan file name>)")
    ap.add_argument("--voiceover", help="recorded or TTS voiceover to mix over the cut (starts at 0s)")
    ap.add_argument("--music", help="music bed to mix under the cut")
    ap.add_argument("--keep-model-audio", type=float, default=None,
                    help=f"model audio gain 0-1 when a voiceover/music is mixed (default {MODEL_AUDIO_GAIN})")
    ap.add_argument("--only", default="", help="comma-separated placements")
    a = ap.parse_args()
    need("ffmpeg")

    plan_path = Path(a.plan).resolve()
    plan = attach_path(load_or_exit(plan_path, "plan"), plan_path)
    a.out = a.out or str(Path("out") / plan_path.stem)
    work = Path(a.out) / a.pass_name
    log = load_json(work / "runlog.json").get("shots", {}) if (work / "runlog.json").exists() else {}
    idx = shot_index(plan)
    size = master_size(plan)
    tmp = work / "assembly"
    tmp.mkdir(parents=True, exist_ok=True)

    # 1. Resolve the clip for each segment
    seg_files, seg_info, problems = [], [], []
    for n, seg in enumerate(segments(plan)):
        src = seg["source"]
        if idx[src].get("mode") == "recorded":  # a real clip, cut in unchanged
            rec = resolve(plan_path, idx[src].get("source_video"))
            if not rec or not rec.exists():
                problems.append(f"segment {n + 1}: recorded clip not found: {idx[src].get('source_video')}")
                continue
            dst = tmp / f"seg{n:02d}_0.mp4"
            normalise(str(rec), dst, size, idx[src].get("trim"))
            seg_files.append(dst)
            seg_info.append({**seg, "file": str(dst), "actual": probe(dst)["duration"], "extend_output": "recorded"})
            continue
        e = log.get(src, {})
        if e.get("status") != "ok" or not Path(e.get("output", "")).exists():
            problems.append(f"segment {n + 1} needs shot `{src}` (status: {e.get('status', 'not generated')})")
            continue
        files = [e["output"]]
        mode = "single"
        if len(seg["shots"]) > 1 and src == seg["shots"][-1]:
            dur = probe(e["output"])["duration"]
            if dur >= CUMULATIVE_RATIO * seg["planned"]:
                mode = "cumulative"
            else:  # provider returned only the new part: stitch the chain
                mode = "incremental"
                files = [log[s]["output"] for s in seg["shots"] if log.get(s, {}).get("status") == "ok"]
        parts = []
        for k, f in enumerate(files):
            dst = tmp / f"seg{n:02d}_{k}.mp4"
            normalise(f, dst, size)
            parts.append(dst)
        if len(parts) > 1:
            joined = tmp / f"seg{n:02d}.mp4"
            concat(parts, joined)
        else:
            joined = parts[0]
        seg_files.append(joined)
        seg_info.append({**seg, "file": str(joined), "actual": probe(joined)["duration"], "extend_output": mode})
    if problems:
        for p in problems:
            print(f"ERROR {p}")
        print("Generate the missing shots first (generate.py run).")
        return 1

    body = tmp / "body.mp4"
    concat(seg_files, body)
    body_dur = probe(body)["duration"]

    # 2. Actual start of every shot on the cut, for super timing
    starts, t = {}, 0.0
    for seg in seg_info:
        off = 0.0
        scale = seg["actual"] / seg["planned"] if seg["planned"] else 1.0
        for sid in seg["shots"]:
            starts[sid] = t + off * scale
            off += shot_seconds(plan, idx[sid])
        t += seg["actual"]

    brand = plan.get("brand", {})
    ec = plan.get("end_card", {})
    disc = plan.get("disclosure", {})
    disc_text = disc.get("text") if disc.get("overlay") else None
    anchor = float(plan.get("crop_anchor", 0.5))
    pls = placements()
    wanted = [p for p in plan.get("placements", []) if not a.only or p in a.only.split(",")]
    deliver = work / "deliverables"
    deliver.mkdir(parents=True, exist_ok=True)
    manifest = {"plan": str(plan_path), "pass": a.pass_name, "body_seconds": round(body_dur, 2),
                "segments": [{k: v for k, v in s.items() if k != "file"} for s in seg_info], "placements": {}}
    name = slug(f"{brand.get('name', 'brand')}-{plan.get('id') or brand.get('product', 'ad')}")

    for pname in wanted:
        p = pls[pname]
        pw, ph = p["size"]
        pdir = tmp / pname
        pdir.mkdir(exist_ok=True)
        overlays, supers_meta = [], []
        for sid, s in idx.items():
            for k, su in enumerate(s.get("supers", [])):
                if sid not in starts:
                    continue
                png = pdir / f"super_{sid}_{k}.png"
                emph = s.get("role") == "hook" and k == 0
                meta = render_super(su["text"], (pw, ph), p["safe"], su.get("position", "center"), brand, emph, png)
                a0 = round(starts[sid] + float(su["start"]), 3)
                a1 = round(min(starts[sid] + float(su["end"]), body_dur), 3)
                overlays.append((png, a0, a1))
                supers_meta.append({"shot": sid, "text": su["text"], "start": a0, "end": a1, **meta})
        if disc_text:
            dpng = pdir / "disclosure.png"
            render_disclosure(disc_text, (pw, ph), p["safe"], brand, dpng)
            overlays.append((dpng, 0.0, round(body_dur, 3)))

        # body with crop + overlays
        inputs = ["-i", str(body)]
        for png, _, _ in overlays:
            inputs += ["-i", str(png)]
        chain = [f"[0:v]{crop_filter(size, (pw, ph), anchor)},setsar=1[v0]"]
        last = "v0"
        for i, (_, a0, a1) in enumerate(overlays, start=1):
            chain.append(f"[{last}][{i}:v]overlay=0:0:enable='between(t,{a0},{a1})'[v{i}]")
            last = f"v{i}"
        body_p = pdir / "body.mp4"
        run(["ffmpeg", "-y", "-v", "error", *inputs, "-filter_complex", ";".join(chain),
             "-map", f"[{last}]", "-map", "0:a", "-c:v", "libx264", "-preset", "veryfast", "-crf", CRF_DELIVER,
             "-c:a", "copy", str(body_p)])

        # end card
        parts = [body_p]
        if ec.get("duration"):
            card_png = pdir / "end_card.png"
            render_end_card((pw, ph), p["safe"], ec, brand, disc.get("text") if disc.get("ai_label") else None,
                            plan_path.parent, card_png)
            card_mp4 = pdir / "end_card.mp4"
            run(["ffmpeg", "-y", "-v", "error", "-loop", "1", "-i", str(card_png),
                 "-f", "lavfi", "-i", "anullsrc=channel_layout=stereo:sample_rate=48000",
                 "-t", str(ec["duration"]), "-vf", f"fps={FPS},format=yuv420p,setsar=1",
                 "-c:v", "libx264", "-preset", "veryfast", "-crf", CRF_DELIVER, "-c:a", "aac", "-ar", "48000",
                 "-ac", "2", "-b:a", AUDIO_BITRATE, str(card_mp4)])
            parts.append(card_mp4)
        cut = pdir / "cut.mp4"
        concat(parts, cut)

        # audio: optional voiceover / music, then loudness
        final = deliver / f"{name}_{pname}_{a.pass_name}.mp4"
        extra = [x for x in (a.voiceover, a.music) if x]
        if extra:
            gain = a.keep_model_audio if a.keep_model_audio is not None else MODEL_AUDIO_GAIN
            ins = ["-i", str(cut)] + sum((["-i", x] for x in extra), [])
            mix = [f"[0:a]volume={gain}[m0]"]
            labels = ["[m0]"]
            for i, x in enumerate(extra, start=1):
                vol = VOICE_GAIN if x == a.voiceover else MUSIC_GAIN
                mix.append(f"[{i}:a]volume={vol},apad[m{i}]")
                labels.append(f"[m{i}]")
            mix.append(f"{''.join(labels)}amix=inputs={len(labels)}:duration=first:normalize=0,{LOUDNESS}[aout]")
            run(["ffmpeg", "-y", "-v", "error", *ins, "-filter_complex", ";".join(mix), "-map", "0:v",
                 "-map", "[aout]", "-c:v", "copy", "-c:a", "aac", "-b:a", AUDIO_BITRATE, "-ar", "48000",
                 "-movflags", "+faststart", str(final)])
        else:
            run(["ffmpeg", "-y", "-v", "error", "-i", str(cut), "-af", LOUDNESS, "-c:v", "copy",
                 "-c:a", "aac", "-b:a", AUDIO_BITRATE, "-ar", "48000", "-movflags", "+faststart", str(final)])
        info = probe(final)
        manifest["placements"][pname] = {"file": str(final), **info, "safe": p["safe"], "supers": supers_meta,
                                         "end_card_seconds": ec.get("duration", 0)}
        print(f"[{pname}] {final} ({info['duration']:.1f}s {info['width']}x{info['height']})")

    save_json(deliver / "manifest.json", manifest)
    print(f"Manifest: {deliver / 'manifest.json'}")
    for seg in seg_info:
        if seg["extend_output"] in ("cumulative", "incremental"):
            print(f"Info (expected, not an error): chain {'>'.join(seg['shots'])} came back {seg['extend_output']}.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
