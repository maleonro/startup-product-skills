"""Gemini Omni Flash via the Interactions API (google-genai >= 2.19).

Request shape mirrors Google's reference script (google-gemini/gemini-skills,
skills/gemini-omni-flash-api/scripts/video/generate_video.py, Sept 2026):
input = ordered parts [image..., video..., text], response_format = video config,
previous_interaction_id for turn-by-turn edit/extend, store=True so later turns work.
"""
from __future__ import annotations

import base64
import os
import threading
import time

from .base import Provider, ProviderError

MODEL = os.environ.get("GEMINI_OMNI_MODEL", "gemini-omni-1.1-flash")


class OmniProvider(Provider):
    name = "omni"
    modes = ("text_to_video", "first_frame", "first_last", "reference", "extend", "edit")
    resolutions = ("360p", "720p", "1080p", "4k")
    # 720p is Google's published rate (5,792 output tokens/s at $17.50/M = ~$0.10/s).
    # The other tiers are third-party list prices; override with OMNI_PRICE_JSON.
    price_per_second = {"360p": 0.03, "720p": 0.10, "1080p": 0.15, "4k": 0.30}

    def __init__(self):
        override = os.environ.get("OMNI_PRICE_JSON")
        if override:
            import json
            self.price_per_second = {**self.price_per_second, **json.loads(override)}
        self._client = None
        self._uploads: dict[str, dict] = {}
        self._lock = threading.Lock()

    # ---- request -------------------------------------------------------
    def build_request(self, job: dict, previous_id: str | None) -> dict:
        parts = [{"type": i["kind"], "path": i["path"], "mime_type": i["mime_type"]} for i in job["inputs"]]
        parts.append({"type": "text", "text": job["prompt"]})
        fmt = {"type": "video", "delivery": "uri", "aspect_ratio": job["aspect_ratio"],
               "resolution": job["resolution"]}
        if job.get("duration"):
            fmt["duration"] = f"{int(job['duration'])}s"
        req = {"model": MODEL, "input": parts, "response_format": fmt,
               "store": True, "background": False}
        if previous_id:
            req["previous_interaction_id"] = previous_id
        return req

    # ---- execution -----------------------------------------------------
    def preflight(self) -> None:
        self._get_client()

    def _get_client(self):
        if self._client is None:
            try:
                from google import genai
                from google.genai import types
            except ImportError as e:
                raise ProviderError("google-genai is not installed: pip install -U 'google-genai>=2.19'") from e
            key = os.environ.get("GEMINI_API_KEY") or os.environ.get("GOOGLE_API_KEY")
            if not key:
                raise ProviderError("GEMINI_API_KEY is not set; use --dry-run or --mock instead.")
            # 900 s: Google's script defaults to 600 s and recommends 900-1200 s for 4K and long extensions.
            timeout_s = int(os.environ.get("OMNI_TIMEOUT_S", "900"))
            self._client = genai.Client(api_key=key, http_options=types.HttpOptions(timeout=timeout_s * 1000))
        return self._client

    def _upload(self, path: str, mime: str) -> dict:
        with self._lock:
            if path in self._uploads:
                return self._uploads[path]
        client = self._get_client()
        f = client.files.upload(file=path, config={"mime_type": mime})
        # Files API processing: up to 5 min, polled from 2 s backing off to 15 s (Google's pattern).
        deadline = time.time() + 300
        delay = 2.0
        while True:
            state = getattr(getattr(f, "state", None), "name", str(getattr(f, "state", "")))
            if state == "ACTIVE" or state.endswith("ACTIVE"):
                break
            if "FAILED" in state:
                raise ProviderError(f"File API processing failed for {path}")
            if time.time() > deadline:
                raise ProviderError(f"Timed out waiting for {path} to become ACTIVE")
            time.sleep(delay)
            delay = min(delay * 1.5, 15)
            f = client.files.get(name=f.name)
        ref = {"uri": f.uri, "mime_type": getattr(f, "mime_type", None) or mime}
        with self._lock:
            self._uploads[path] = ref
        return ref

    def execute(self, request: dict, output_path: str) -> dict:
        client = self._get_client()
        body = dict(request)
        parts = []
        for p in body["input"]:
            if p["type"] == "text":
                parts.append(p)
            else:
                ref = self._upload(p["path"], p["mime_type"])
                parts.append({"type": p["type"], "uri": ref["uri"], "mime_type": ref["mime_type"]})
        body["input"] = parts
        try:
            interaction = client.interactions.create(**body)
        except Exception as e:  # SDK raises APIError subclasses
            msg = getattr(e, "message", None) or str(e)
            raise ProviderError(f"Omni request failed: {msg[:400]}") from e
        video = getattr(interaction, "output_video", None)
        if not video:
            raise ProviderError(
                "Omni returned no video. Likely a safety filter, or a regional block on "
                "uploaded video / recognizable people (EEA, CH, UK). See references/omni-api.md.")
        os.makedirs(os.path.dirname(output_path) or ".", exist_ok=True)
        if getattr(video, "data", None):
            data = video.data
            with open(output_path, "wb") as fh:
                fh.write(base64.b64decode(data) if isinstance(data, str) else data)
        elif getattr(video, "uri", None):
            blob = client.files.download(file=video)
            with open(output_path, "wb") as fh:
                fh.write(blob)
        else:
            raise ProviderError("Omni response had an output_video without data or uri.")
        return {"interaction_id": getattr(interaction, "id", None), "output": output_path}
