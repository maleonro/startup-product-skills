#!/usr/bin/env python3
"""Run generation jobs built by build_jobs.py.

Usage:
  generate.py run  out/adplan/draft/jobs.json --dry-run            # write request payloads, no network, no spend
  generate.py run  out/adplan/draft/jobs.json --mock               # offline test clips through the whole pipeline
  generate.py run  out/adplan/draft/jobs.json --budget 5           # live; refuses if the estimate exceeds the budget
  generate.py edit out/adplan/draft/jobs.json --shot s2 --prompt "Make the light warmer." --budget 2
  generate.py promote out/adplan/draft/jobs.json --resolution 1080p --budget 6   # EXPERIMENTAL, see omni-api.md

Live runs need GEMINI_API_KEY. Every call stores the interaction (store=True) and the
runlog keeps the latest interaction id per shot, so edits always chain from the newest turn.
Re-running skips shots whose output exists and whose prompt is unchanged (use --force).
"""
from __future__ import annotations

import argparse
import concurrent.futures as cf
import datetime as dt
import hashlib
import json
import os
import shutil
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from lib import providers  # noqa: E402
from lib.common import load_json, load_or_exit, probe, save_json, segments  # noqa: E402


def sha(text: str) -> str:
    return hashlib.sha256(text.encode()).hexdigest()[:12]


def now() -> str:
    return dt.datetime.now(dt.timezone.utc).isoformat(timespec="seconds")


def runlog_path(jobs_file: Path) -> Path:
    return jobs_file.parent / "runlog.json"


def load_runlog(jobs_file: Path) -> dict:
    p = runlog_path(jobs_file)
    return load_json(p) if p.exists() else {"shots": {}}


def pick_provider(args, spec: dict):
    if getattr(args, "mock", False):
        return providers.get("mock")
    return providers.get(spec.get("provider", "omni"))


def check_budget(args, cost: float, live: bool) -> bool:
    if not live:
        return True
    if args.budget is None:
        print(f"Refusing a live run without --budget. Estimated spend: ${cost:.2f}. "
              "Confirm the amount with the user, then pass --budget.")
        return False
    if cost > args.budget + 1e-9:
        print(f"Estimated spend ${cost:.2f} exceeds --budget ${args.budget:.2f}. Nothing was generated.")
        return False
    return True


def cmd_run(args) -> int:
    jobs_file = Path(args.jobs)
    spec = load_or_exit(jobs_file, "jobs file", "Run build_jobs.py first")
    jobs = spec["jobs"]
    log = load_runlog(jobs_file)
    prov = pick_provider(args, spec)
    live = not (args.dry_run or args.mock)
    shots_log = log.setdefault("shots", {})
    log["provider"] = prov.name if not args.dry_run else f"{spec.get('provider')} (dry-run)"

    if args.mock:  # let the mock chain from outputs made in earlier runs
        for sid, e in shots_log.items():
            if e.get("interaction_id") and e.get("output") and os.path.exists(e["output"]):
                prov.remember(e["interaction_id"], e["output"])

    def done(j):
        e = shots_log.get(j["shot"], {})
        return (not args.force and e.get("status") == "ok" and e.get("prompt_sha") == sha(j["prompt"] + j["resolution"])
                and os.path.exists(e.get("output", "")))

    todo = [j for j in jobs if not done(j)]
    cost = round(sum(j.get("est_usd", 0) for j in todo), 2)
    if args.mock:
        print(f"{len(todo)} of {len(jobs)} job(s) to run; mock costs $0 (would be ~${cost:.2f} on {spec.get('provider')}).")
    else:
        print(f"{len(todo)} of {len(jobs)} job(s) to run; estimated spend ${cost:.2f} ({prov.name}).")
    if not check_budget(args, cost, live):
        return 3

    if args.dry_run:
        req_dir = jobs_file.parent / "requests"
        for j in todo:
            prev = f"<interaction id of {j['previous_shot']}>" if j["previous_shot"] else None
            req = prov.build_request(j, prev)
            save_json(req_dir / f"{j['shot']}.json", req)
            if shots_log.get(j["shot"], {}).get("status") != "ok":  # never hide a real take
                shots_log[j["shot"]] = {"status": "dry-run", "request": str(req_dir / f"{j['shot']}.json"), "at": now()}
        save_json(runlog_path(jobs_file), log)
        print(f"Dry run: wrote {len(todo)} request payload(s) to {req_dir}. Nothing was sent.")
        return 0

    if todo:
        prov.preflight()
    pending = {j["shot"]: j for j in todo}
    failed: set[str] = set()

    def ready(j):
        dep = j["previous_shot"]
        if not dep:
            return True
        e = shots_log.get(dep, {})
        return dep not in pending and e.get("status") == "ok"

    def work(j):
        prev_id = shots_log.get(j["previous_shot"], {}).get("interaction_id") if j["previous_shot"] else None
        req = prov.build_request(j, prev_id)
        return prov.execute(req, j["output"])

    with cf.ThreadPoolExecutor(max_workers=args.concurrency) as ex:
        running: dict[cf.Future, dict] = {}
        while pending or running:
            for sid in list(pending):
                j = pending[sid]
                dep = j["previous_shot"]
                if dep and (dep in failed or (dep not in pending and shots_log.get(dep, {}).get("status") != "ok"
                                              and dep not in {r["shot"] for r in running.values()})):
                    failed.add(sid)
                    shots_log[sid] = {"status": "skipped", "error": f"dependency {dep} did not succeed", "at": now()}
                    del pending[sid]
                    print(f"[{sid}] skipped: dependency {dep} failed")
                elif ready(j):
                    running[ex.submit(work, j)] = j
                    del pending[sid]
                    print(f"[{sid}] generating ({j['mode']}, {j['resolution']})...")
            if not running:
                if pending:  # unresolved dependencies (should not happen after validation)
                    for sid in pending:
                        shots_log[sid] = {"status": "skipped", "error": "unresolved dependency", "at": now()}
                    break
                continue
            finished, _ = cf.wait(list(running), return_when=cf.FIRST_COMPLETED)
            for fut in finished:
                j = running.pop(fut)
                sid = j["shot"]
                prev = shots_log.get(sid, {})
                try:
                    res = fut.result()
                    info = probe(res["output"])
                    shots_log[sid] = {
                        "status": "ok", "interaction_id": res["interaction_id"],
                        "history": prev.get("history", []) + [res["interaction_id"]],
                        "output": res["output"], "prompt_sha": sha(j["prompt"] + j["resolution"]),
                        "mode": j["mode"], "resolution": j["resolution"], "est_usd": j.get("est_usd", 0),
                        "requested_seconds": j["duration"], "probe": info, "at": now()}
                    print(f"[{sid}] ok -> {res['output']} ({info['duration']:.1f}s {info['width']}x{info['height']})")
                except Exception as e:  # noqa: BLE001
                    failed.add(sid)
                    shots_log[sid] = {**prev, "status": "failed", "error": str(e)[:500], "at": now()}
                    print(f"[{sid}] FAILED: {str(e)[:300]}")
                save_json(runlog_path(jobs_file), log)

    save_json(runlog_path(jobs_file), log)
    ok = sum(1 for j in jobs if shots_log.get(j["shot"], {}).get("status") == "ok")
    print(f"Done: {ok}/{len(jobs)} shots ok. Runlog: {runlog_path(jobs_file)}")
    return 0 if ok == len(jobs) else 1


def _turn(args, sid: str, prompt: str, resolution: str | None, out_path: str | None) -> int:
    """One turn-by-turn edit on the newest interaction of a shot."""
    jobs_file = Path(args.jobs)
    spec = load_or_exit(jobs_file, "jobs file", "Run build_jobs.py first")
    log = load_runlog(jobs_file)
    e = log.get("shots", {}).get(sid)
    if not e or e.get("status") != "ok" or not e.get("interaction_id"):
        print(f"Shot {sid} has no successful generation in {runlog_path(jobs_file)}; run it first.")
        return 1
    prov = pick_provider(args, spec)
    if args.mock:
        prov.remember(e["interaction_id"], e["output"])
    else:
        prov.preflight()
    job = next((j for j in spec["jobs"] if j["shot"] == sid), None)
    if job is None:
        print(f"Shot {sid} is not in {jobs_file}.")
        return 1
    text = prompt.strip()
    if "keep everything" not in text.lower():
        text = (text.rstrip(".") + ". Keep everything else the same.")
    edit_job = {**job, "mode": "edit", "prompt": text, "inputs": [], "duration": None,
                "resolution": resolution or job["resolution"], "previous_shot": sid}
    secs, usd = prov.estimate_usd(edit_job, e.get("probe", {}).get("duration", 10.0))
    live = not args.mock
    if not check_budget(args, usd, live):
        return 3
    target = out_path or e["output"]
    if not out_path:  # keep the previous take next to the new one
        n = len(e.get("history", []))
        shutil.copy(e["output"], e["output"].replace(".mp4", f".v{n}.mp4"))
    req = prov.build_request(edit_job, e["interaction_id"])
    res = prov.execute(req, target)
    info = probe(res["output"])
    entry = {**e, "interaction_id": res["interaction_id"], "history": e.get("history", []) + [res["interaction_id"]],
             "output": res["output"], "probe": info, "last_edit": text, "at": now(),
             "est_usd": round(e.get("est_usd", 0) + usd, 4)}
    return entry


def cmd_edit(args) -> int:
    jobs_file = Path(args.jobs)
    log = load_runlog(jobs_file)
    entry = _turn(args, args.shot, args.prompt, None, None)
    if isinstance(entry, int):
        return entry
    log["shots"][args.shot] = entry
    save_json(runlog_path(jobs_file), log)
    print(f"[{args.shot}] edited -> {entry['output']} (interaction {entry['interaction_id']}); "
          f"previous take kept as .v{len(entry['history']) - 1}.mp4")
    return 0


def cmd_promote(args) -> int:
    """EXPERIMENTAL: ask Omni to re-render approved draft takes at a higher resolution
    through a keep-everything edit. Not documented by Google; QC compares the result."""
    jobs_file = Path(args.jobs)
    spec = load_or_exit(jobs_file, "jobs file", "Run build_jobs.py first")
    log = load_runlog(jobs_file)
    final_dir = jobs_file.parent.parent / "final"
    final_log_path = final_dir / "runlog.json"
    final_log = load_json(final_log_path) if final_log_path.exists() else {"shots": {}}
    final_log["provider"] = log.get("provider")
    final_log["promoted_from"] = str(jobs_file)
    prov = pick_provider(args, spec)
    # Only the takes the cut uses: chain tails, or the latest edit of them.
    used = {seg["source"] for seg in segments(load_json(spec["plan"]))}
    total = 0.0
    for j in spec["jobs"]:
        e = log["shots"].get(j["shot"], {})
        if j["shot"] in used and e.get("status") == "ok":
            total += prov.estimate_usd({**j, "mode": "edit", "resolution": args.resolution},
                                       e.get("probe", {}).get("duration", 10.0))[1]
    if not check_budget(args, total, not args.mock):
        return 3
    args.budget = None if args.mock else float("inf")  # already checked for the whole batch
    for j in spec["jobs"]:
        sid = j["shot"]
        if sid not in used or log["shots"].get(sid, {}).get("status") != "ok":
            continue
        entry = _turn(args, sid, "Keep everything exactly the same", args.resolution,
                      str(final_dir / f"{sid}.mp4"))
        if isinstance(entry, int):
            return entry
        entry["promoted_from_interaction"] = log["shots"][sid]["interaction_id"]
        entry["resolution"] = args.resolution
        final_log["shots"][sid] = entry
        save_json(final_log_path, final_log)
        print(f"[{sid}] promoted -> {entry['output']}")
    print("Promoted. Run review.py compare to check each final take matches its draft.")
    return 0


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)
    for name in ("run", "edit", "promote"):
        p = sub.add_parser(name)
        p.add_argument("jobs")
        p.add_argument("--mock", action="store_true", help="offline test clips, no key, no spend")
        p.add_argument("--budget", type=float, default=None, help="max USD for this command (required live)")
        if name == "run":
            p.add_argument("--dry-run", action="store_true")
            p.add_argument("--concurrency", type=int, default=3)
            p.add_argument("--force", action="store_true")
        if name == "edit":
            p.add_argument("--shot", required=True)
            p.add_argument("--prompt", required=True)
        if name == "promote":
            p.add_argument("--resolution", default="1080p", choices=("720p", "1080p", "4k"))
    a = ap.parse_args()
    try:
        return {"run": cmd_run, "edit": cmd_edit, "promote": cmd_promote}[a.cmd](a)
    except providers.ProviderError as e:
        print(f"ERROR: {e}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
