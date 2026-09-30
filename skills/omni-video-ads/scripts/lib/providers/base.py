"""Provider interface. Add a model by writing one module that subclasses Provider
and registering it in providers/__init__.py (see references/adapters.md)."""
from __future__ import annotations


class ProviderError(RuntimeError):
    pass


class Provider:
    name = "base"
    # Modes this provider can run, from lib.common.MODES.
    modes: tuple[str, ...] = ()
    aspects: tuple[str, ...] = ("9:16", "16:9")
    resolutions: tuple[str, ...] = ("720p",)
    # USD per output second, by resolution. Estimates only; see references/omni-api.md.
    price_per_second: dict[str, float] = {}
    # True when an extend call returns the whole video so far (billing and assembly
    # treat the output as cumulative).
    extend_is_cumulative = True

    def estimate_usd(self, job: dict, prior_seconds: float = 0.0) -> tuple[float, float]:
        """Return (billed_seconds_upper_bound, usd) for a job."""
        rate = self.price_per_second.get(job["resolution"], 0.0)
        if job["mode"] == "edit":
            secs = prior_seconds or 10.0  # unknown source length: bill the 10 s upload maximum
        elif job["mode"] == "extend" and self.extend_is_cumulative:
            secs = prior_seconds + (job["duration"] or 0)
        else:
            secs = float(job["duration"] or 0)
        return secs, round(secs * rate, 4)

    def preflight(self) -> None:
        """Fail fast (raise ProviderError) before any job is submitted."""
        return None

    def build_request(self, job: dict, previous_id: str | None) -> dict:
        """JSON-serialisable request, with local file paths still in place.
        Used verbatim by --dry-run so it must not touch the network."""
        raise NotImplementedError

    def execute(self, request: dict, output_path: str) -> dict:
        """Run the request, write the video to output_path and return
        {"interaction_id": str | None, "output": output_path}."""
        raise NotImplementedError
