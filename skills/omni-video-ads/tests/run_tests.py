#!/usr/bin/env python3
"""Regression tests for omni-video-ads. No API key, no network, no spend.

  python3 tests/run_tests.py          # everything (about 2-3 minutes, mostly ffmpeg)
  python3 tests/run_tests.py --fast   # skip the ffmpeg pipeline tests
"""
from __future__ import annotations

import copy
import json
import os
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
SKILL = HERE.parent
FIX = HERE / "fixtures"
sys.path.insert(0, str(SKILL / "scripts"))

from lib.common import chains, probe, segments  # noqa: E402
from lib.compile import build_job, compile_prompt, keep_fraction  # noqa: E402
from lib.providers import get  # noqa: E402
from build_jobs import estimate  # noqa: E402
from validate_plan import validate  # noqa: E402

GOOD = json.loads((FIX / "good_plan.json").read_text())
PASSED, FAILED = [], []


def check(name, cond, detail=""):
    (PASSED if cond else FAILED).append(name)
    print(f"{'ok  ' if cond else 'FAIL'} {name}{'' if cond else ' :: ' + str(detail)}")


def rules(plan, region=""):
    rep = validate(plan, str(FIX / "good_plan.json"), region)
    return {(i["level"], i["rule"]) for i in rep.items}, rep


def mutate(fn):
    p = copy.deepcopy(GOOD)
    fn(p)
    return p


def sh(*args, ok=(0,), cwd=SKILL):
    res = subprocess.run([sys.executable, *map(str, args)], capture_output=True, text=True, cwd=cwd)
    if res.returncode not in ok:
        raise AssertionError(f"{args[0]} exit {res.returncode}\n{res.stdout[-800:]}\n{res.stderr[-800:]}")
    return res


# ---------------------------------------------------------------- validator
def test_validator():
    got, rep = rules(GOOD)
    check("good plan has no errors", not rep.errors, rep.errors)
    check("good plan warns face drift (R16)", ("WARN", "R16") in got)

    cases = {
        "R1 missing field": (lambda p: p.pop("end_card"), ("ERROR", "R1")),
        "R1 duplicate id": (lambda p: p["shots"][1].update(id="s1"), ("ERROR", "R1")),
        "R2 bad aspect": (lambda p: p.update(master_aspect="4:5"), ("ERROR", "R2")),
        "R2 placement needs other master": (lambda p: p["placements"].append("landscape_16x9"), ("ERROR", "R2")),
        "R2 unknown placement": (lambda p: p["placements"].append("snapchat"), ("ERROR", "R2")),
        "R3 bad mode": (lambda p: p["shots"][0].update(mode="animate"), ("ERROR", "R3")),
        "R4 duration too long": (lambda p: p["shots"][0].update(duration=12), ("ERROR", "R4")),
        "R4 duration float": (lambda p: p["shots"][0].update(duration=4.5), ("ERROR", "R4")),
        "R5 last without first": (lambda p: p["shots"][3].pop("first_frame"), ("ERROR", "R5")),
        "R5 extend unknown": (lambda p: p["shots"][2].update(continues="zz"), ("ERROR", "R5")),
        "R5 extend forward ref": (lambda p: p["shots"][2].update(continues="s4"), ("ERROR", "R5")),
        "R5 reference without refs": (lambda p: p["shots"][0].update(mode="reference"), ("ERROR", "R5")),
        "R5 edit mid-chain": (lambda p: p["shots"].append({"id": "e1", "mode": "edit", "edits": "s2",
                                                           "edit_prompt": "Warmer light"}), ("ERROR", "R5")),
        "R5 fork": (lambda p: p["shots"].append({**copy.deepcopy(p["shots"][2]), "id": "s3b"}), ("ERROR", "R5")),
        "R6 too many image refs": (lambda p: p["shots"][0].update(
            image_refs=[{"path": "product_still.png", "label": "x"}] * 7), ("ERROR", "R6")),
        "R6 unlabeled ref": (lambda p: p["shots"][0].update(image_refs=[{"path": "product_still.png"}]),
                             ("WARN", "R6")),
        "R7 missing file": (lambda p: p["shots"][1].update(first_frame="nope.png"), ("ERROR", "R7")),
        "R9 missing details": (lambda p: p["shots"][0]["details"].pop("motif"), ("ERROR", "R9")),
        "R9 no final image": (lambda p: p["shots"][0].pop("final_image"), ("WARN", "R9")),
        "R10 filler": (lambda p: p["shots"][0].update(light="stunning cinematic light"), ("WARN", "R10")),
        "R11 no camera": (lambda p: p["shots"][0].pop("camera"), ("ERROR", "R11")),
        "R11 camera salad": (lambda p: p["shots"][0].update(camera="dolly then pan then crane and zoom"),
                             ("WARN", "R11")),
        "R12 no audio": (lambda p: (p["shots"][0].pop("audio"), p["style"].pop("audio_bed")), ("ERROR", "R12")),
        "R13 spanish prompt": (lambda p: p["shots"][0].update(
            action="la mujer mira la cámara con el producto sobre la mesa"), ("WARN", "R13")),
        "R14 dialogue too long": (lambda p: p["shots"][0].update(dialogue={"speaker": "sofia",
            "line": "this is a very long line that cannot possibly fit into three seconds of speech"}),
            ("ERROR", "R14")),
        "R14 unknown speaker": (lambda p: p["shots"][0].update(dialogue={"speaker": "bob", "line": "Hi there"}),
                                ("ERROR", "R14")),
        "R15 native text in spanish ad": (lambda p: p["shots"][0].update(native_text=["A sign says 'Hola'"]),
                                          ("ERROR", "R15")),
        "R15 super outside shot": (lambda p: p["shots"][0]["supers"][0].update(end=5.0), ("ERROR", "R15")),
        "R15 super too fast": (lambda p: p["shots"][1]["supers"][0].update(
            text="uno dos tres cuatro cinco seis siete ocho nueve diez once doce"), ("WARN", "R15")),
        "R16 unknown character": (lambda p: p["shots"][0].update(characters=["ghost"]), ("ERROR", "R16")),
        "R17 chain too long": (lambda p: [p["shots"].insert(3 + k, {**copy.deepcopy(p["shots"][2]),
                                          "id": f"x{k}", "continues": ("s3" if k == 0 else f"x{k - 1}"),
                                          "duration": 10}) for k in range(4)], ("ERROR", "R17")),
        "R18 first shot not hook": (lambda p: p["shots"][0].update(role="setup"), ("ERROR", "R18")),
        "R18 late hook super": (lambda p: p["shots"][0]["supers"][0].update(start=1.5), ("WARN", "R18")),
        "R18 no product shot": (lambda p: [s.update(role="setup") for s in p["shots"][1:]], ("ERROR", "R18")),
        "R19 no cta": (lambda p: p["end_card"].pop("cta"), ("ERROR", "R19")),
        "R19 too long for reels": (lambda p: p["end_card"].update(duration=4) or p["shots"][0].update(duration=5),
                                   ("WARN", "R19")),
        "R20 unsubstantiated claim": (lambda p: p["brief"].update(claims=["Clinically proven"]), ("WARN", "R20")),
        "R20 political": (lambda p: p["brief"].update(category="political"), ("ERROR", "R20")),
        "R20 no ai label": (lambda p: p["disclosure"].update(ai_label=False), ("WARN", "R20")),
    }
    for name, (fn, want) in cases.items():
        got, _ = rules(mutate(fn))
        check(f"validator {name}", want in got, sorted(got))

    # region rules
    p = mutate(lambda p: p["shots"].__setitem__(2, {**p["shots"][2], "continues": None,
                                                    "source_video": "ugc_long.mp4"}))
    got, _ = rules(p, "eu")
    check("validator R8 uploaded video in EU", ("ERROR", "R8") in got, sorted(got))
    check("validator R6 upload longer than 10s ok for 6s clip", ("ERROR", "R6") not in got, sorted(got))
    got, _ = rules(p, "")
    check("validator R8 silent outside EU", ("ERROR", "R8") not in got)
    p = mutate(lambda p: p["shots"][0].update(image_refs=[{"path": "product_still.png", "label": "her face",
                                                           "contains_people": True}]))
    got, _ = rules(p, "uk")
    check("validator R8 people upload in UK", ("ERROR", "R8") in got)
    p = mutate(lambda p: p["shots"][0].update(video_refs=[{"path": "ugc_long.mp4", "label": "motion"}]))
    got, _ = rules(p)
    check("validator R6 long video ref warns", ("WARN", "R6") in got)


# ---------------------------------------------------------------- compiler
def test_compiler():
    plan = GOOD
    j = {s["id"]: build_job(str(FIX / "good_plan.json"), plan, s, "draft", "out") for s in plan["shots"]}
    check("compile first_last uses simple tags", j["s4"]["prompt"].startswith("<FIRST_FRAME> <LAST_FRAME> "))
    check("compile loop sends two image parts", len(j["s4"]["inputs"]) == 2 and j["s4"]["inputs"][0]["path"] ==
          j["s4"]["inputs"][1]["path"])
    check("compile first_frame tag", j["s2"]["prompt"].startswith("<FIRST_FRAME> Single continuous shot"))
    check("compile extend prefix + dependency", j["s3"]["prompt"].startswith("Extend this video.") and
          j["s3"]["previous_shot"] == "s2" and not j["s3"]["inputs"])
    check("compile draft resolution", j["s1"]["resolution"] == "360p")
    check("compile negatives when no text/dialogue", "No dialogue." in j["s1"]["prompt"] and
          "No on-screen text" in j["s1"]["prompt"])
    check("compile music override", "; no music." in j["s1"]["prompt"] and "lo-fi" not in j["s1"]["prompt"])
    check("compile negative space for supers", "negative space in the upper third" in j["s1"]["prompt"])
    check("compile identity block repeated", j["s1"]["prompt"].count("gold hoop") == 1 and
          "gold hoop" in j["s3"]["prompt"])
    check("compile keep fraction 4:5", keep_fraction(plan) and abs(keep_fraction(plan) - 0.703) < 0.01)
    sq = mutate(lambda p: p["placements"].append("square_1x1"))
    check("compile keep fraction 1:1", abs(keep_fraction(sq) - 0.5625) < 0.01)
    check("compile no crop clause for 9:16 only", keep_fraction(mutate(lambda p: p.update(
        placements=["reels", "tiktok"]))) is None)
    # references + first frame -> explicit declarations
    ref = mutate(lambda p: p["shots"][1].update(image_refs=[{"path": "logo.png", "label": "brand logo"}]))
    jr = build_job(str(FIX / "good_plan.json"), ref, ref["shots"][1], "final", "out")
    check("compile declarations with refs",
          jr["prompt"].startswith("[# Sources <FIRST_FRAME>@Image1] [# References <IMAGE_REF_0>@Image2]")
          and "<IMAGE_REF_0> is the brand logo." in jr["prompt"] and "Use Image1 as the starting frame." in jr["prompt"],
          jr["prompt"][:200])
    check("compile final resolution", jr["resolution"] == "720p")
    ed = {"id": "e1", "mode": "edit", "edits": "s4", "edit_prompt": "Make the can matte"}
    je = build_job(str(FIX / "good_plan.json"), GOOD, ed, "draft", "out")
    check("compile edit prompt", je["prompt"] == "Make the can matte. Keep everything else the same." and
          je["previous_shot"] == "s4" and je["duration"] is None)
    dl = mutate(lambda p: p["shots"][0].update(dialogue={"speaker": "sofia", "line": "Not again.",
                                                         "delivery": "muttering"}))
    check("compile dialogue line", 'The woman says, muttering: "Not again."' in compile_prompt(dl, dl["shots"][0])
          and "No dialogue." not in compile_prompt(dl, dl["shots"][0]))


def test_estimate_and_segments():
    jobs = [build_job(str(FIX / "good_plan.json"), GOOD, s, "final", "out") for s in GOOD["shots"]]
    jobs, total = estimate(jobs, get("omni"))
    by = {j["shot"]: j for j in jobs}
    check("estimate extend billed cumulative", by["s3"]["est_billed_seconds"] == 7)
    check("estimate total at 720p", abs(total - (3 + 4 + 7 + 3) * 0.10) < 1e-6, total)
    check("segments chain", [s["shots"] for s in segments(GOOD)] == [["s1"], ["s2", "s3"], ["s4"]])
    p = mutate(lambda p: p["shots"] + [])
    p["shots"] += [{"id": "e1", "mode": "edit", "edits": "s4", "edit_prompt": "x"},
                   {"id": "e2", "mode": "edit", "edits": "e1", "edit_prompt": "y"}]
    check("segments follow edit chain", segments(p)[-1]["source"] == "e2" and len(chains(p)) == 3)


# ---------------------------------------------------------------- pipeline
def test_pipeline():
    tmp = Path(tempfile.mkdtemp(prefix="ova_"))
    out = tmp / "out"
    plan = tmp / "plan.json"
    for f in ("good_plan.json", "product_still.png", "logo.png"):
        shutil.copy(FIX / f, tmp / f)
    shutil.move(tmp / "good_plan.json", plan)
    try:
        r = sh("scripts/build_jobs.py", plan, "--pass", "draft", "--out", out, "--quiet")
        check("pipeline build_jobs", "Estimated spend (draft, omni): $0.51" in r.stdout, r.stdout[-300:])
        r = sh("scripts/generate.py", "run", out / "draft/jobs.json", "--budget", "0.10", ok=(3,))
        check("pipeline budget guard refuses", "exceeds --budget" in r.stdout)
        r = sh("scripts/generate.py", "run", out / "draft/jobs.json", ok=(3,))
        check("pipeline live needs --budget", "without --budget" in r.stdout)
        sh("scripts/generate.py", "run", out / "draft/jobs.json", "--dry-run")
        req = json.loads((out / "draft/requests/s3.json").read_text())
        check("pipeline dry-run payload", req["store"] is True and req["response_format"]["duration"] == "3s"
              and req["previous_interaction_id"] == "<interaction id of s2>")
        sh("scripts/generate.py", "run", out / "draft/jobs.json", "--mock")
        log = json.loads((out / "draft/runlog.json").read_text())["shots"]
        check("pipeline mock all ok", all(v["status"] == "ok" for v in log.values()), log)
        check("pipeline extend cumulative", abs(probe(log["s3"]["output"])["duration"] - 7) < 0.2)
        r = sh("scripts/generate.py", "run", out / "draft/jobs.json", "--mock")
        check("pipeline resume skips done", "0 of 4 job(s)" in r.stdout)
        sh("scripts/generate.py", "edit", out / "draft/jobs.json", "--shot", "s4", "--prompt", "Matte can", "--mock")
        log = json.loads((out / "draft/runlog.json").read_text())["shots"]
        check("pipeline edit chains newest id", len(log["s4"]["history"]) == 2 and
              log["s4"]["interaction_id"] == log["s4"]["history"][-1] and (out / "draft/s4.v1.mp4").exists())
        sh("scripts/assemble.py", plan, "--pass", "draft", "--out", out)
        man = json.loads((out / "draft/deliverables/manifest.json").read_text())
        sizes = {k: (v["width"], v["height"]) for k, v in man["placements"].items()}
        check("pipeline placements sizes", sizes == {"reels": (1080, 1920), "tiktok": (1080, 1920),
                                                     "feed_4x5": (1080, 1350)}, sizes)
        durs = [v["duration"] for v in man["placements"].values()]
        check("pipeline cut length 15s", all(abs(d - 15) < 0.3 for d in durs), durs)
        check("pipeline supers timed on cut", [round(s["start"], 1) for s in man["placements"]["reels"]["supers"]]
              == [0.0, 4.0, 7.3], man["placements"]["reels"]["supers"])
        r = sh("scripts/review.py", "cut", out / "draft")
        check("pipeline review cut clean", "auto checks ok" in r.stdout and "safe area" not in r.stdout)
        sh("scripts/review.py", "clips", out / "draft")
        check("pipeline contact sheets", all((out / f"draft/qc/{s}/contact_sheet.jpg").exists()
                                             for s in ("s1", "s2", "s3", "s4")))
        # a super too long for the safe area must be caught by review, not silently cropped
        cramped = json.loads(plan.read_text())
        cramped["end_card"]["url"] = "nativa.example"
        # voiceover mix + loudness
        vo = tmp / "vo.wav"
        subprocess.run(["ffmpeg", "-y", "-v", "error", "-f", "lavfi", "-i", "sine=frequency=500:duration=6",
                        str(vo)], check=True)
        sh("scripts/assemble.py", plan, "--pass", "draft", "--out", out, "--voiceover", vo, "--only", "reels")
        r = sh("scripts/review.py", "cut", out / "draft", ok=(0, 1))
        check("pipeline voiceover mix loudness ok", "LUFS" not in r.stdout.split("[reels]")[1].split("\n")[0])
        # promote (experimental) and compare
        sh("scripts/generate.py", "promote", out / "draft/jobs.json", "--resolution", "1080p", "--mock")
        flog = json.loads((out / "final/runlog.json").read_text())["shots"]
        check("pipeline promote only used takes", set(flog) == {"s1", "s3", "s4"}, set(flog))
        r = sh("scripts/review.py", "compare", out / "draft", out / "final", ok=(0, 1))
        check("pipeline compare runs", "similarity" in r.stdout)
        # incremental extension fallback: provider that returns only the new segment
        log = json.loads((out / "draft/runlog.json").read_text())
        inc = tmp / "s3_only.mp4"
        subprocess.run(["ffmpeg", "-y", "-v", "error", "-i", log["shots"]["s3"]["output"], "-ss", "4",
                        "-c:v", "libx264", "-c:a", "aac", str(inc)], check=True)
        log["shots"]["s3"]["output"] = str(inc)
        (out / "draft/runlog.json").write_text(json.dumps(log))
        r = sh("scripts/assemble.py", plan, "--pass", "draft", "--out", out, "--only", "tiktok")
        man = json.loads((out / "draft/deliverables/manifest.json").read_text())
        check("pipeline incremental extend stitched", "came back incremental" in r.stdout and
              abs(man["placements"]["tiktok"]["duration"] - 15) < 0.3, r.stdout[-300:])
        # lesson logging goes to LESSONS_PATH
        lp = tmp / "LESSONS.md"
        lp.write_text("# lessons\n")
        env_before = os.environ.get("LESSONS_PATH")
        os.environ["LESSONS_PATH"] = str(lp)
        sh("scripts/review.py", "lesson", "--category", "hook", "--score", "3", "--lesson",
           "Hooks that start mid-action stop the scroll better than slow establishing frames",
           "--evidence", "test")
        r = sh("scripts/review.py", "lesson", "--category", "hook", "--score", "3", "--lesson", "bad",
               "--evidence", "x", ok=(1,))
        if env_before is None:
            os.environ.pop("LESSONS_PATH")
        check("pipeline lesson append + reject vague", "LESSON: Hooks that start" in lp.read_text())
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


def test_cli_validate():
    r = sh("scripts/validate_plan.py", FIX / "good_plan.json")
    check("cli validate pass", "PASS" in r.stdout)
    bad = Path(tempfile.mkdtemp()) / "bad.json"
    bad.write_text(json.dumps(mutate(lambda p: p["end_card"].pop("cta"))))
    for f in ("product_still.png", "logo.png"):
        shutil.copy(FIX / f, bad.parent / f)
    r = sh("scripts/validate_plan.py", bad, ok=(1,))
    check("cli validate fail exit 1", "FAIL" in r.stdout)
    r = sh("scripts/build_jobs.py", bad, "--pass", "draft", "--out", bad.parent / "o", ok=(1,))
    check("cli build refuses invalid plan", "Refusing" in r.stdout)
    r = sh("scripts/validate_plan.py", FIX / "nope.json", ok=(2,))
    check("cli validate unreadable exit 2", "cannot read" in r.stdout)


# ---------------------------------------------------------------- eval-driven fixes (phase 3)
def ugc_plan(tmp: Path) -> Path:
    """Real UGC clip as the hook (recorded), then generated shots; a source_video extend and
    an edit of an uploaded clip exercise the upload paths."""
    for f in ("good_plan.json", "product_still.png", "logo.png", "ugc_long.mp4"):
        shutil.copy(FIX / f, tmp / f)
    p = json.loads((tmp / "good_plan.json").read_text())
    p["id"] = "ugc-mix"
    p["brief"]["likeness_consent"] = True
    rec = {"id": "u1", "role": "hook", "mode": "recorded", "source_video": "ugc_long.mp4", "trim": [0, 4],
           "source_contains_people": True,
           "supers": [{"text": "Lo dijo una clienta real", "start": 0.0, "end": 3.5, "position": "top"}]}
    p["shots"][0]["role"] = "problem"
    p["shots"].insert(0, rec)
    p["end_card"]["url"] = ""
    (tmp / "plan.json").write_text(json.dumps(p, ensure_ascii=False))
    return tmp / "plan.json"


def test_phase3():
    tmp = Path(tempfile.mkdtemp(prefix="ova3_"))
    try:
        plan_path = ugc_plan(tmp)
        plan = json.loads(plan_path.read_text())
        rep = validate(plan, str(plan_path), "")
        check("recorded hook plan validates", not rep.errors, rep.errors)
        got = {(i["level"], i["rule"]) for i in rep.items}
        check("consent recorded -> reminder only", ("WARN", "R20") in got)
        rep = validate(copy.deepcopy(plan), str(plan_path), "eu")
        check("recorded clip allowed in EU (not sent to Omni)", not any(i["rule"] == "R8" for i in rep.items))
        noc = copy.deepcopy(plan)
        noc["brief"].pop("likeness_consent")
        rep = validate(noc, str(plan_path), "")
        check("real person without consent is an error", any(i["rule"] == "R20" and i["level"] == "ERROR"
                                                            for i in rep.items))
        bad = copy.deepcopy(plan)
        bad["shots"][0]["supers"][0]["end"] = 5.0
        rep = validate(bad, str(plan_path), "")
        check("super longer than trimmed clip", any(i["rule"] == "R15" and i["level"] == "ERROR" for i in rep.items))
        bad = copy.deepcopy(plan)
        bad["shots"].append({**copy.deepcopy(plan["shots"][3]), "id": "x", "continues": "u1"})
        rep = validate(bad, str(plan_path), "")
        check("extend of a recorded clip is refused", any("recorded clip" in i["msg"] for i in rep.errors))
        eu = copy.deepcopy(plan)
        eu["shots"][2]["source_contains_people"] = True
        eu["shots"][2]["source_video"] = "ugc_long.mp4"
        rep = validate(eu, str(plan_path), "eu")
        check("R8 message points to a workable path", any("recorded" in i["msg"] and i["rule"] == "R8"
                                                          for i in rep.errors))

        # uploaded-clip extend: cost and planned length include the 6 s source
        up = copy.deepcopy(GOOD)
        up["shots"][2] = {**up["shots"][2], "continues": None, "source_video": str(FIX / "ugc_long.mp4")}
        up["shots"][2].pop("continues")
        from lib.common import attach_path, planned_seconds
        attach_path(up, FIX / "good_plan.json")
        jobs = [build_job(str(FIX / "good_plan.json"), up, s, "final", "out") for s in up["shots"]]
        jobs, _ = estimate(jobs, get("omni"))
        by = {j["shot"]: j for j in jobs}
        check("upload extend billed with source length", abs(by["s3"]["est_billed_seconds"] - 9) < 0.1,
              by["s3"]["est_billed_seconds"])
        check("upload extend counted in cut length", abs(planned_seconds(up) - 21) < 0.1, planned_seconds(up))

        # edit of an uploaded clip is its own segment, and the mock runs it
        ed = copy.deepcopy(GOOD)
        ed["shots"].insert(1, {"id": "e0", "role": "proof", "mode": "edit", "source_video": "ugc_long.mp4",
                               "edit_prompt": "Make it black and white"})
        attach_path(ed, FIX / "good_plan.json")
        check("upload edit is a segment", ["e0"] in [s["shots"] for s in segments(ed)])
        (tmp / "ed.json").write_text(json.dumps(ed))
        sh("scripts/build_jobs.py", tmp / "ed.json", "--pass", "draft", "--out", tmp / "o_ed", "--quiet")
        r = sh("scripts/generate.py", "run", tmp / "o_ed/draft/jobs.json", "--mock")
        check("mock edit of uploaded clip runs", "5/5 shots ok" in r.stdout, r.stdout[-300:])

        # full pipeline with the recorded hook, default --out = out/<plan stem> in the cwd
        r = sh(SKILL / "scripts/build_jobs.py", plan_path, "--pass", "draft", "--quiet", cwd=tmp)
        check("default out folder", (tmp / "out/plan/draft/jobs.json").exists(), r.stdout[-200:])
        jobs = json.loads((tmp / "out/plan/draft/jobs.json").read_text())["jobs"]
        check("recorded shot has no job", "u1" not in {j["shot"] for j in jobs})
        sh(SKILL / "scripts/generate.py", "run", "out/plan/draft/jobs.json", "--mock", cwd=tmp)
        sh(SKILL / "scripts/assemble.py", plan_path, "--pass", "draft", cwd=tmp)
        man = json.loads((tmp / "out/plan/draft/deliverables/manifest.json").read_text())
        d = man["placements"]["reels"]["duration"]
        check("recorded clip cut in (4 s trim + 13 s + 2 s)", abs(d - 19) < 0.3, d)
        first = man["placements"]["reels"]["supers"][0]
        check("super on recorded clip at 0 s", first["start"] == 0.0 and first["shot"] == "u1", first)
        r = sh(SKILL / "scripts/review.py", "cut", "out/plan/draft", cwd=tmp, ok=(0, 1))
        check("review cut samples every segment", len(list((tmp / "out/plan/draft/qc/cut/reels").glob("guide_*.jpg")))
              >= 2 + len(man["segments"]), r.stdout[-200:])
        r = sh(SKILL / "scripts/review.py", "clips", "out/plan/draft", cwd=tmp)
        qc = json.loads((tmp / "out/plan/draft/qc/s3/qc.json").read_text())
        check("extension note is info, not a failed check", not qc["auto_checks"] and qc["info"])

        # prompt text fixes
        j = build_job(str(FIX / "good_plan.json"), GOOD, {**GOOD["shots"][0], "camera": "100mm macro"}, "draft", "o")
        check("shot lens overrides plan lens", "50mm" not in j["prompt"] and "100mm macro" in j["prompt"])
        ref = mutate(lambda p: p["shots"][1].update(image_refs=[{"path": "logo.png", "label": "the brand logo"}]))
        j = build_job(str(FIX / "good_plan.json"), ref, ref["shots"][1], "draft", "o")
        check("no doubled article", "is the the" not in j["prompt"] and "<IMAGE_REF_0> is the brand logo." in j["prompt"])
        got, _ = rules(GOOD)
        check("placeholder url warns", ("WARN", "R19") in got)
        one = mutate(lambda p: p["shots"][0].update(characters=[]))
        got, _ = rules(one)
        check("R16 counts segments, not shots", ("WARN", "R16") not in got, sorted(got))

        # lessons: default location outside the skill, score optional
        env = dict(os.environ, HOME=str(tmp))
        env.pop("LESSONS_PATH", None)
        res = subprocess.run([sys.executable, "scripts/review.py", "lesson", "--category", "region",
                              "--lesson", "Uploaded video edits fail in the EEA so plan generated shots instead",
                              "--evidence", "validator R8"], capture_output=True, text=True, cwd=SKILL, env=env)
        check("lesson default path is per user", (tmp / ".omni-video-ads/LESSONS.md").exists() and res.returncode == 0,
              res.stdout + res.stderr)
        res = subprocess.run([sys.executable, "scripts/review.py", "lessons"], capture_output=True, text=True,
                             cwd=SKILL, env=env)
        check("lessons prints seed + accumulated", "Seed lessons" in res.stdout and "Uploaded video edits" in res.stdout)
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


if __name__ == "__main__":
    test_validator()
    test_compiler()
    test_estimate_and_segments()
    test_cli_validate()
    if "--fast" not in sys.argv:
        test_pipeline()
        test_phase3()
    print(f"\n{len(PASSED)} passed, {len(FAILED)} failed")
    sys.exit(1 if FAILED else 0)
