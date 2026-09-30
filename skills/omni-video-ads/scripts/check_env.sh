#!/usr/bin/env bash
# Check what this machine can do and print the run mode: LIVE, DRY-RUN or BLOCKED.
#   LIVE     google-genai + API key + API reachable: real generations (they cost money)
#   DRY-RUN  pipeline tools present but no key or no reachable API: build jobs, --dry-run, --mock
#   BLOCKED  a required local tool is missing (python>=3.10, ffmpeg with overlay, Pillow)
# Exit codes: 0 LIVE, 1 DRY-RUN (a normal, supported mode), 2 BLOCKED. The key is never printed.
set -u
ok=1; live=1
say() { printf '%-10s %s\n' "$1" "$2"; }

PY=$(command -v python3 || true)
if [ -z "$PY" ]; then say MISSING "python3 (>=3.10)"; ok=0
else
  if "$PY" -c 'import sys; sys.exit(0 if sys.version_info>=(3,10) else 1)'; then say ok "$($PY --version)"
  else say MISSING "python >= 3.10 (found $($PY --version))"; ok=0; fi
  if "$PY" -c 'import PIL' 2>/dev/null; then say ok "Pillow"; else say MISSING "Pillow: pip install pillow"; ok=0; fi
  if "$PY" -c 'from google import genai; c=genai.Client(api_key="x"); assert hasattr(c,"interactions")' 2>/dev/null; then
    say ok "google-genai $("$PY" -c 'import google.genai as g; print(g.__version__)')"
  else say NO-LIVE "google-genai >= 2.19 with Interactions API: pip install -U google-genai"; live=0; fi
fi

for t in ffmpeg ffprobe; do
  if command -v $t >/dev/null; then say ok "$t"; else say MISSING "$t (apt install ffmpeg / brew install ffmpeg)"; ok=0; fi
done
if command -v ffmpeg >/dev/null && ! ffmpeg -hide_banner -filters 2>/dev/null | grep -q ' overlay '; then
  say MISSING "ffmpeg overlay filter"; ok=0
fi
if command -v ffmpeg >/dev/null && ! ffmpeg -hide_banner -filters 2>/dev/null | grep -q ' drawtext '; then
  say NO-MOCK "ffmpeg drawtext filter (only the --mock test clips need it)"
fi

if [ -n "${GEMINI_API_KEY:-}${GOOGLE_API_KEY:-}" ]; then say ok "API key is set"
else say NO-LIVE "GEMINI_API_KEY is not set"; live=0; fi

if [ $live -eq 1 ] && command -v curl >/dev/null; then
  code=$(curl -s -o /dev/null -m 8 -w '%{http_code}' https://generativelanguage.googleapis.com/ || echo 000)
  if [ "$code" = "000" ]; then say NO-LIVE "generativelanguage.googleapis.com unreachable from here"; live=0
  else say ok "Gemini API reachable (HTTP $code)"; fi
fi

case "${OMNI_REGION:-}" in
  eu|eea|uk|ch|EU|EEA|UK|CH) say REGION "${OMNI_REGION}: no uploaded-video edit/extend, no uploads of recognizable people";;
  "") say REGION "unset (set OMNI_REGION=eu when working from the EEA, CH or UK)";;
  *) say REGION "${OMNI_REGION}";;
esac

if [ $ok -eq 0 ]; then echo "MODE: BLOCKED"; exit 2
elif [ $live -eq 1 ]; then echo "MODE: LIVE"; exit 0
else echo "MODE: DRY-RUN"; exit 1; fi
