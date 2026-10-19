#!/usr/bin/env python3
"""Check a YouTube publish package against YouTube's own limits before anyone pastes it.

Usage:
  check-metadata.py <package-dir> --duration 575 --keyword "how to find clients" [--keyword ...]

The package is a folder with the files a person pastes into YouTube Studio:
  title.txt        one title per line: the first is the one to publish, the rest are Test & Compare variants
  description.txt  the description, exactly as it goes into Studio
  tags.txt         optional, comma-separated
  *.srt            optional, the captions file
  thumbnail*.png|jpg  optional, the thumbnails

ERROR = YouTube rejects it or ignores it (official limit). WARN = practitioner advice, a person decides.
Exit code 1 when there is any ERROR.
"""
import argparse, glob, os, re, struct, sys, unicodedata

errors, warns = [], []


def err(m):
    errors.append(m)


def warn(m):
    warns.append(m)


def fold(s):
    return "".join(c for c in unicodedata.normalize("NFD", s.lower()) if unicodedata.category(c) != "Mn")


def secs(stamp):
    parts = [int(p) for p in stamp.split(":")]
    return sum(p * 60 ** i for i, p in enumerate(reversed(parts)))


def check_title(lines, keywords):
    if not lines:
        err("title.txt is empty")
    if len(lines) > 3:
        err(f"{len(lines)} titles: Test & Compare takes at most 3")
    for t in lines:
        if len(t) > 100:
            err(f"title over 100 characters ({len(t)}): {t}")
        if re.search(r"[<>]", t):
            err(f"title has < or >, which Studio rejects: {t}")
        if len(t) > 70:
            warn(f"title is {len(t)} characters; search cuts around 60-70 (practitioner estimate): {t}")
        if keywords and not any(fold(k) in fold(t[:70]) for k in keywords):
            warn(f"no keyword in the first 70 characters: {t}")


def check_description(d, duration, keywords):
    if len(d) > 5000:
        err(f"description over 5,000 characters ({len(d)})")
    if re.search(r"[<>]", d):
        err("description has < or >, which Studio rejects")
    if "**" in d or re.search(r"\]\(https?://", d):
        err("description has Markdown (** or [text](url)); YouTube shows it raw. Use *bold* and bare links")
    first = d.strip().split("\n")[0]
    if len(first) > 150:
        warn(f"first line is {len(first)} characters; about 120-157 show before 'more' (practitioner estimate)")
    if keywords and not any(fold(k) in fold(d[:150]) for k in keywords):
        warn("no keyword in the first 150 characters of the description")
    # chapters: lines that start with a timestamp
    chapters = [(secs(m.group(1)), m.group(2)) for m in re.finditer(r"^((?:\d{1,2}:)?\d{1,2}:\d{2})\s+[-–·]?\s*(.+)$", d, re.M)]
    if not chapters:
        warn("no chapters in the description")
    else:
        if chapters[0][0] != 0:
            err("the first chapter must start at 0:00")
        if len(chapters) < 3:
            err(f"{len(chapters)} chapters: YouTube needs at least 3")
        for (a, ta), (b, tb) in zip(chapters, chapters[1:]):
            if b <= a:
                err(f"chapters out of order: {tb}")
            elif b - a < 10:
                err(f"chapter shorter than 10 seconds: {ta}")
        if duration:
            if chapters[-1][0] >= duration - 10:
                err(f"last chapter starts less than 10 seconds before the end: {chapters[-1][1]}")
        generic = [t for _, t in chapters if re.fullmatch(r"(chapter|part|section|capitulo|parte|chapitre|partie|kapitel|teil|capitolo)\s*\d+", fold(t).strip())]
        if generic:
            warn(f"chapter titles that say nothing ({', '.join(generic)}): name what the chapter teaches")
    tags = re.findall(r"(?<![\w&])#\w+", d)
    if len(tags) > 60:
        err(f"{len(tags)} hashtags: over 60, YouTube ignores all of them")
    elif len(tags) > 3:
        warn(f"{len(tags)} hashtags: only 3 show above the title")
    lines = [l.strip() for l in d.split("\n") if len(l.strip()) > 30]
    dup = {l for l in lines if lines.count(l) > 1}
    if dup:
        err(f"repeated sentences (spam policy): {sorted(dup)[0][:60]}")


def check_tags(t):
    tags = [x.strip() for x in t.split(",") if x.strip()]
    if len(t) > 500:
        warn(f"tags are {len(t)} characters; 500 is the commonly quoted cap (not verified on an official page)")
    if len(tags) > 15:
        warn(f"{len(tags)} tags: YouTube says tags play a minimal role, mostly for misspellings")


def check_srt(path, duration):
    blocks = open(path, encoding="utf-8").read().strip().split("\n\n")
    last = 0.0
    for b in blocks:
        ls = b.split("\n")
        m = re.match(r"(\d+):(\d+):(\d+),(\d+) --> (\d+):(\d+):(\d+),(\d+)", ls[1] if len(ls) > 1 else "")
        if not m:
            err(f"{os.path.basename(path)}: bad caption block {ls[0]}")
            continue
        v = [int(x) for x in m.groups()]
        a, b2 = v[0] * 3600 + v[1] * 60 + v[2] + v[3] / 1000, v[4] * 3600 + v[5] * 60 + v[6] + v[7] / 1000
        if a < last:
            err(f"{os.path.basename(path)}: caption {ls[0]} overlaps the one before")
        last = b2
        if any(len(l) > 42 for l in ls[2:]):
            warn(f"{os.path.basename(path)}: caption {ls[0]} has a line over 42 characters")
    if duration and last > duration:
        err(f"{os.path.basename(path)}: captions run past the end of the video")


def png_size(p):
    with open(p, "rb") as f:
        head = f.read(24)
    return struct.unpack(">II", head[16:24]) if head[:8] == b"\x89PNG\r\n\x1a\n" else None


def check_thumbs(paths):
    for p in paths:
        mb = os.path.getsize(p) / 1e6
        if mb > 2:
            err(f"{os.path.basename(p)} is {mb:.1f} MB: over 2 MB fails on mobile uploads")
        wh = png_size(p) if p.endswith(".png") else None
        if wh:
            w, h = wh
            if abs(w / h - 16 / 9) > 0.01:
                err(f"{os.path.basename(p)} is {w}x{h}, not 16:9")
            if w < 1280:
                warn(f"{os.path.basename(p)} is {w} wide: Test & Compare shrinks thumbnails under 1280x720 to 480p")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("package")
    ap.add_argument("--duration", type=float, help="video length in seconds")
    ap.add_argument("--keyword", action="append", default=[], help="the searched phrase; repeat for more")
    a = ap.parse_args()
    pk = a.package
    read = lambda n: open(os.path.join(pk, n), encoding="utf-8").read() if os.path.exists(os.path.join(pk, n)) else None
    t = read("title.txt")
    if t is None:
        err("missing title.txt")
    else:
        check_title([l.strip() for l in t.strip().split("\n") if l.strip()], a.keyword)
    d = read("description.txt")
    if d is None:
        err("missing description.txt")
    else:
        check_description(d, a.duration, a.keyword)
    if read("tags.txt") is not None:
        check_tags(read("tags.txt"))
    for s in glob.glob(os.path.join(pk, "*.srt")):
        check_srt(s, a.duration)
    check_thumbs(sorted(glob.glob(os.path.join(pk, "thumbnail*.png")) + glob.glob(os.path.join(pk, "thumbnail*.jpg"))))
    for m in errors:
        print("ERROR", m)
    for m in warns:
        print("WARN ", m)
    print(f"{len(errors)} errors, {len(warns)} warnings")
    sys.exit(1 if errors else 0)


if __name__ == "__main__":
    main()
