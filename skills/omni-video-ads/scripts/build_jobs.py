#!/usr/bin/env python3
"""Compile a validated ad plan into generation jobs plus a cost estimate.

Usage:
  build_jobs.py adplan.json --pass draft|final [--provider omni] [--out out/<plan name>] [--only s1,s2]

Writes <out>/<pass>/jobs.json (default <out> = out/<plan file name>) and prints each compiled prompt and the estimated spend.
Refuses to build when validate_plan.py reports ERRORs.
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from lib import providers  # noqa: E402
from lib.common import attach_path, load_or_exit, save_json, shot_index  # noqa: E402
from lib.compile import build_job, ordered_shots  # noqa: E402
from validate_plan import validate  # noqa: E402


def estimate(jobs: list[dict], prov) -> tuple[list[dict], float]:
    by_shot = {j["shot"]: j for j in jobs}
    produced: dict[str, float] = {}  # seconds of video each shot's output contains
    total = 0.0
    for j in jobs:
        prior = produced.get(j["previous_shot"], 0.0) if j["previous_shot"] else j.get("source_seconds", 0.0)
        secs, usd = prov.estimate_usd(j, prior)
        j["est_billed_seconds"], j["est_usd"] = secs, usd
        produced[j["shot"]] = secs if j["mode"] in ("extend", "edit") else float(j["duration"] or 0)
        total += usd
    return list(by_shot.values()), round(total, 2)


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("plan")
    ap.add_argument("--pass", dest="pass_name", choices=("draft", "final"), required=True)
    ap.add_argument("--provider", default="omni")
    ap.add_argument("--out", default=None, help="output folder (default: out/<plan file name>)")
    ap.add_argument("--only", default="", help="comma-separated shot ids (their dependencies are added)")
    ap.add_argument("--region", default="")
    ap.add_argument("--quiet", action="store_true", help="do not print prompts")
    a = ap.parse_args()

    plan = attach_path(load_or_exit(a.plan, "plan"), a.plan)
    a.out = a.out or str(Path("out") / Path(a.plan).stem)
    rep = validate(plan, a.plan, a.region)
    if rep.errors:
        for i in rep.errors:
            print(f"ERROR {i['rule']} {i['where']}: {i['msg']}")
        print("Refusing to build jobs: run validate_plan.py and fix every ERROR.")
        return 1

    try:
        prov = providers.get(a.provider)
    except providers.ProviderError as e:
        print(f"ERROR: {e}")
        return 1
    wanted = {x.strip() for x in a.only.split(",") if x.strip()}
    idx = shot_index(plan)
    if wanted:
        unknown = wanted - set(idx)
        if unknown:
            print(f"ERROR unknown shot ids in --only: {', '.join(sorted(unknown))}")
            return 1
        # pull in dependencies so chains and edits can run
        stack = list(wanted)
        while stack:
            s = idx[stack.pop()]
            dep = s.get("continues") if s.get("mode") == "extend" else s.get("edits") if s.get("mode") == "edit" else None
            if dep and dep not in wanted:
                wanted.add(dep)
                stack.append(dep)

    jobs = []
    for s in ordered_shots(plan):
        if wanted and s["id"] not in wanted:
            continue
        mode = s.get("mode", "text_to_video")
        if mode == "recorded":
            continue  # cut in by assemble.py; nothing to generate
        if mode not in prov.modes:
            print(f"ERROR provider `{prov.name}` cannot run mode `{mode}` (shot {s['id']})")
            return 1
        jobs.append(build_job(a.plan, plan, s, a.pass_name, a.out))

    jobs, total = estimate(jobs, prov)
    out = Path(a.out) / a.pass_name / "jobs.json"
    save_json(out, {"plan": str(Path(a.plan).resolve()), "provider": prov.name, "pass": a.pass_name,
                    "estimated_usd": total, "jobs": jobs})

    for j in jobs:
        dep = f" <- {j['previous_shot']}" if j["previous_shot"] else ""
        print(f"[{j['shot']}] {j['mode']}{dep} | {j['duration'] or '-'}s @ {j['resolution']} | "
              f"~${j['est_usd']:.2f} (billed <= {j['est_billed_seconds']:.0f}s)")
        if not a.quiet:
            print(f"    {j['prompt']}\n")
    print(f"Jobs: {len(jobs)}  Estimated spend ({a.pass_name}, {prov.name}): ${total:.2f}")
    print(f"Wrote {out}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
