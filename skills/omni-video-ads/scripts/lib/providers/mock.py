"""Offline stand-in for a video model. Renders labelled test clips with ffmpeg so
the whole pipeline (chaining, assembly, crops, overlays, QC) runs without an API key
or spend. Behaves like Omni where it matters: extend returns the cumulative video,
edit returns a same-length replacement, every call returns a new interaction id."""
from __future__ import annotations

import hashlib
import os
import shutil
import threading
import uuid

from ..common import probe, run
from .base import Provider

RES_H = {"360p": 360, "720p": 720, "1080p": 1080, "4k": 2160}
PALETTE = ["0x2E4057", "0x6B2737", "0x1B5E20", "0x4A148C", "0x8D6E00", "0x004D61"]


class MockProvider(Provider):
    name = "mock"
    modes = ("text_to_video", "first_frame", "first_last", "reference", "extend", "edit")
    resolutions = ("360p", "720p", "1080p", "4k")
    price_per_second = {"360p": 0.0, "720p": 0.0, "1080p": 0.0, "4k": 0.0}

    def __init__(self):
        self._outputs: dict[str, str] = {}  # interaction id -> file
        self._lock = threading.Lock()

    def build_request(self, job: dict, previous_id: str | None) -> dict:
        return {"job": job, "previous_interaction_id": previous_id}

    def _size(self, aspect: str, res: str) -> tuple[int, int]:
        h = RES_H.get(res, 720)
        w = round(h * 16 / 9 / 2) * 2
        return (h, w) if aspect == "9:16" else (w, h)

    def _render(self, path: str, secs: float, w: int, h: int, label: str, color: str) -> None:
        fs = max(12, h // 24)
        txt = label.replace(":", r"\:").replace("'", "")
        run(["ffmpeg", "-y", "-v", "error",
             "-f", "lavfi", "-i", f"color=c={color}:s={w}x{h}:r=24:d={secs}",
             "-f", "lavfi", "-i", f"sine=frequency=330:sample_rate=48000:duration={secs}",
             "-vf", f"drawtext=text='{txt}':fontcolor=white:fontsize={fs}:x=(w-tw)/2:y=h*0.46,"
                    f"drawtext=text='%{{pts\\:hms}}':fontcolor=white@0.8:fontsize={fs}:x=(w-tw)/2:y=h*0.54",
             "-c:v", "libx264", "-pix_fmt", "yuv420p", "-c:a", "aac", "-shortest", path])

    def execute(self, request: dict, output_path: str) -> dict:
        job = request["job"]
        prev = request.get("previous_interaction_id")
        os.makedirs(os.path.dirname(output_path) or ".", exist_ok=True)
        w, h = self._size(job["aspect_ratio"], job["resolution"])
        color = PALETTE[int(hashlib.md5(job["shot"].encode()).hexdigest(), 16) % len(PALETTE)]
        tmp = output_path + ".part.mp4"
        src = next((i["path"] for i in job["inputs"] if i["role"] == "source_video"), None)
        if job["mode"] == "extend" and (prev or src):
            base = self._outputs[prev] if prev else src
            self._render(tmp, float(job["duration"]), w, h, f"{job['shot']} (extension)", color)
            lst = output_path + ".txt"
            with open(lst, "w") as fh:
                fh.write(f"file '{os.path.abspath(base)}'\nfile '{os.path.abspath(tmp)}'\n")
            run(["ffmpeg", "-y", "-v", "error", "-f", "concat", "-safe", "0", "-i", lst,
                 "-c:v", "libx264", "-pix_fmt", "yuv420p", "-c:a", "aac", output_path])
            os.remove(lst)
            os.remove(tmp)
        elif job["mode"] == "edit" and (prev or src):
            base = self._outputs[prev] if prev else src
            secs = probe(base)["duration"]
            self._render(tmp, round(secs, 2), w, h, f"{job['shot']} (edit)", "0x333333")
            shutil.move(tmp, output_path)
        else:
            self._render(tmp, float(job["duration"]), w, h, f"{job['shot']} {job['role'] or ''}".strip(), color)
            shutil.move(tmp, output_path)
        with self._lock:
            iid = f"mock_{job['shot']}_{uuid.uuid4().hex[:8]}"
            self._outputs[iid] = output_path
        return {"interaction_id": iid, "output": output_path}

    def remember(self, interaction_id: str, path: str) -> None:
        """Let a resumed run chain from outputs produced in an earlier process."""
        self._outputs[interaction_id] = path
