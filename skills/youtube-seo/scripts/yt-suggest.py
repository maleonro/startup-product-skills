#!/usr/bin/env python3
"""What people type into YouTube search, from YouTube's own autocomplete. Free, no key.

Usage:
  yt-suggest.py "seed" ["seed" ...] [--hl en] [--gl US,GB,CA] [--expand] [--json]

For each seed and each country it asks YouTube's autocomplete. With --expand it also asks
"seed a" ... "seed z" and the language's question words before the seed ("how to seed",
"cómo seed"...), so the long tail shows up. A suggestion that comes back for many expansions
and many countries is a phrase many people type. Autocomplete shows that people search a
phrase, not how many: rank phrases against each other, never quote them as volume.
"""
import argparse, json, string, sys, time, unicodedata, urllib.parse, urllib.request
from collections import defaultdict

URL = "https://suggestqueries.google.com/complete/search?client=youtube&ds=yt&hl={hl}&gl={gl}&q={q}"
QUESTIONS = {
    "en": ["how to", "what", "why", "when"],
    "es": ["cómo", "qué", "por qué", "cuándo"],
    "pt": ["como", "o que", "por que", "quando"],
    "fr": ["comment", "qu'est-ce que", "pourquoi", "quand"],
    "de": ["wie", "was", "warum", "wann"],
    "it": ["come", "cosa", "perché", "quando"],
}


def ask(q, hl, gl):
    url = URL.format(hl=hl, gl=gl, q=urllib.parse.quote(q))
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
    for attempt in range(3):
        try:
            raw = urllib.request.urlopen(req, timeout=10).read().decode("utf-8", "replace")
            body = raw[raw.index("(") + 1 : raw.rindex(")")]  # JSONP: window.google.ac.h([...])
            return [s[0] for s in json.loads(body)[1]]
        except Exception as e:  # rate limit or a bad answer: wait and retry, then give up on this query
            if attempt == 2:
                print(f"skip {q!r} {gl}: {e}", file=sys.stderr)
                return []
            time.sleep(2 * (attempt + 1))


def fold(s):
    """'Cómo' and 'como' are the same search: compare without accents or case."""
    return "".join(c for c in unicodedata.normalize("NFD", s.lower()) if unicodedata.category(c) != "Mn")


def main():
    p = argparse.ArgumentParser()
    p.add_argument("seeds", nargs="+")
    p.add_argument("--hl", default="en", help="the audience's language: en, es, pt, fr, de, it, ...")
    p.add_argument("--gl", default="US", help="the audience's countries, comma-separated: US,GB or AR,MX,CO,ES")
    p.add_argument("--expand", action="store_true", help="also ask seed + a..z and question words + seed")
    p.add_argument("--json", action="store_true")
    a = p.parse_args()
    words = QUESTIONS.get(a.hl.split("-")[0], [])
    if a.expand and not words:
        print(f"no question words for --hl {a.hl}: expanding with a..z only", file=sys.stderr)

    hits = defaultdict(lambda: {"text": "", "queries": 0, "countries": set()})
    for gl in a.gl.split(","):
        for seed in a.seeds:
            queries = [seed]
            if a.expand:
                queries += [f"{seed} {c}" for c in string.ascii_lowercase]
                queries += [f"{w} {seed}" for w in words]
            for q in queries:
                for s in ask(q, a.hl, gl):
                    h = hits[fold(s)]
                    h["text"] = h["text"] or s
                    h["queries"] += 1
                    h["countries"].add(gl)
                time.sleep(0.15)

    rows = sorted(hits.values(), key=lambda h: (-len(h["countries"]), -h["queries"], h["text"]))
    if a.json:
        print(json.dumps([{**h, "countries": sorted(h["countries"])} for h in rows], ensure_ascii=False, indent=1))
        return
    for h in rows:
        print(f'{h["queries"]:3d}  {",".join(sorted(h["countries"])):12s}  {h["text"]}')


if __name__ == "__main__":
    main()
