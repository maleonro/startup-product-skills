"""Pillow renderers for text supers, end cards and safe-zone guides.

Text is drawn by us, not by the model: exact copy in any language, wrapped to the
placement's safe area, readable on mute. Colours come from plan.brand."""
from __future__ import annotations

import subprocess
from functools import lru_cache
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

# Type scale as a fraction of frame width. On 1080 px: hook super 84 px, other supers 63 px,
# headline 81 px, CTA 59 px, URL 39 px, disclosure 30 px. Design choice: the smallest text stays
# near 30 px so it survives the platform's downscale on a phone; check the safe-zone sheets.
HOOK_PX, SUPER_PX, HEAD_PX, CTA_PX, URL_PX, DISC_PX = 0.078, 0.058, 0.075, 0.055, 0.036, 0.028
PAD = 0.035          # box padding, fraction of width
LINE_H = 1.22        # line height as a multiple of font size
BOX_ALPHA = 190      # 75% opaque dark box: readable over bright footage without hiding it
MAX_LINES = 3        # beyond 3 lines a super stops being glanceable; the font shrinks instead
SHRINK = 0.92        # font-size step while fitting text

FALLBACK_FONTS = [
    "/usr/share/fonts/truetype/google-fonts/Poppins-Bold.ttf",
    "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
    "/System/Library/Fonts/Supplemental/Arial Bold.ttf",
    "C:/Windows/Fonts/arialbd.ttf",
]


@lru_cache(maxsize=8)
def font_path(preferred: str | None = None) -> str:
    if preferred and Path(preferred).exists():
        return preferred
    try:
        out = subprocess.run(["fc-match", "-f", "%{file}", (preferred or "sans") + ":bold"],
                             capture_output=True, text=True, timeout=5).stdout.strip()
        if out and Path(out).exists() and out.lower().endswith((".ttf", ".otf")):
            return out
    except (OSError, subprocess.SubprocessError):
        pass
    for f in FALLBACK_FONTS:
        if Path(f).exists():
            return f
    raise RuntimeError("No TrueType font found; set brand.font to a .ttf/.otf path")


def hex_rgba(value: str | None, default: tuple, alpha: int = 255) -> tuple:
    if not value:
        return default
    v = value.lstrip("#")
    if len(v) == 6:
        return tuple(int(v[i:i + 2], 16) for i in (0, 2, 4)) + (alpha,)
    if len(v) == 8:
        return tuple(int(v[i:i + 2], 16) for i in (0, 2, 4, 6))
    return default


def safe_rect(size: tuple[int, int], safe: dict) -> tuple[int, int, int, int]:
    w, h = size
    return (int(w * safe["left"]), int(h * safe["top"]), int(w * (1 - safe["right"])), int(h * (1 - safe["bottom"])))


def _wrap(draw, text: str, font, max_w: int) -> list[str]:
    lines, cur = [], ""
    for word in text.split():
        trial = f"{cur} {word}".strip()
        if draw.textlength(trial, font=font) <= max_w or not cur:
            cur = trial
        else:
            lines.append(cur)
            cur = word
    if cur:
        lines.append(cur)
    return lines


def fit_text(text: str, fpath: str, max_w: int, start_px: int, max_lines: int = MAX_LINES, min_px: int = 22):
    img = Image.new("RGBA", (10, 10))
    d = ImageDraw.Draw(img)
    px = start_px
    while True:
        font = ImageFont.truetype(fpath, px)
        lines = _wrap(d, text, font, max_w)
        widest = max(d.textlength(line, font=font) for line in lines)
        if (len(lines) <= max_lines and widest <= max_w) or px <= min_px:
            return font, lines, px
        px = int(px * SHRINK)


def render_super(text: str, size: tuple[int, int], safe: dict, position: str, brand: dict,
                 emphasis: bool, out: Path) -> dict:
    """Transparent full-frame PNG with the super placed inside the safe area.
    Returns the text box rectangle so QC can verify it."""
    w, h = size
    x0, y0, x1, y1 = safe_rect(size, safe)
    pad = int(w * PAD)
    max_w = (x1 - x0) - 2 * pad
    start = int(w * (HOOK_PX if emphasis else SUPER_PX))
    fpath = font_path(brand.get("font"))
    font, lines, px = fit_text(text, fpath, max_w, start)
    img = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    line_h = int(px * LINE_H)
    block_h = line_h * len(lines)
    block_w = int(max(d.textlength(line, font=font) for line in lines))
    if position == "top":
        by = y0 + pad
    elif position == "lower":
        by = y1 - pad - block_h
    else:
        by = y0 + ((y1 - y0) - block_h) // 2
    cx = x0 + (x1 - x0) // 2
    box = (cx - block_w // 2 - pad, by - pad // 2, cx + block_w // 2 + pad, by + block_h + pad // 2)
    d.rounded_rectangle(box, radius=int(pad * 0.6), fill=hex_rgba(brand.get("super_bg"), (0, 0, 0, BOX_ALPHA), BOX_ALPHA))
    fg = hex_rgba(brand.get("super_fg"), (255, 255, 255, 255))
    for i, line in enumerate(lines):
        lw = d.textlength(line, font=font)
        d.text((cx - lw / 2, by + i * line_h), line, font=font, fill=fg)
    out.parent.mkdir(parents=True, exist_ok=True)
    img.save(out)
    return {"box": [int(v) for v in box], "font_px": px, "lines": len(lines)}


def render_end_card(size: tuple[int, int], safe: dict, card: dict, brand: dict, disclosure: str | None,
                    base_dir: Path, out: Path) -> None:
    w, h = size
    x0, y0, x1, y1 = safe_rect(size, safe)
    bg = hex_rgba(card.get("bg") or brand.get("primary"), (17, 17, 17, 255))
    fg = hex_rgba(card.get("fg") or brand.get("on_primary"), (255, 255, 255, 255))
    accent = hex_rgba(brand.get("accent"), (255, 255, 255, 255))
    on_accent = hex_rgba(brand.get("on_accent"), (17, 17, 17, 255))
    img = Image.new("RGBA", (w, h), bg)
    d = ImageDraw.Draw(img)
    fpath = font_path(brand.get("font"))
    cx = x0 + (x1 - x0) // 2
    items = []  # (kind, payload, height)
    logo_path = card.get("logo") or brand.get("logo")
    if logo_path:
        p = Path(logo_path) if Path(logo_path).is_absolute() else base_dir / logo_path
        if p.exists():
            logo = Image.open(p).convert("RGBA")
            lw = int((x1 - x0) * 0.45)
            lh = int(logo.height * lw / logo.width)
            if lh > (y1 - y0) * 0.25:
                lh = int((y1 - y0) * 0.25)
                lw = int(logo.width * lh / logo.height)
            items.append(("logo", logo.resize((lw, lh)), lh))
    if card.get("headline"):
        f, lines, px = fit_text(card["headline"], fpath, int((x1 - x0) * 0.9), int(w * HEAD_PX))
        items.append(("text", (f, lines, px, fg), int(px * 1.22) * len(lines)))
    cta_font, cta_lines, cta_px = fit_text(card["cta"], fpath, int((x1 - x0) * 0.7), int(w * CTA_PX), max_lines=1)
    items.append(("cta", (cta_font, cta_lines[0], cta_px), int(cta_px * 2.2)))
    if card.get("url"):
        f, lines, px = fit_text(card["url"], fpath, int((x1 - x0) * 0.9), int(w * URL_PX), max_lines=1)
        items.append(("text", (f, lines, px, fg), int(px * 1.22)))
    gap = int(h * 0.03)
    total = sum(i[2] for i in items) + gap * (len(items) - 1)
    y = y0 + ((y1 - y0) - total) // 2
    for kind, payload, ih in items:
        if kind == "logo":
            img.alpha_composite(payload, (cx - payload.width // 2, y))
        elif kind == "text":
            f, lines, px, col = payload
            for i, line in enumerate(lines):
                lw = d.textlength(line, font=f)
                d.text((cx - lw / 2, y + i * int(px * 1.22)), line, font=f, fill=col)
        else:
            f, line, px = payload
            lw = d.textlength(line, font=f)
            bw, bh = int(lw + px * 2), int(px * 2.0)
            d.rounded_rectangle((cx - bw // 2, y, cx + bw // 2, y + bh), radius=bh // 2, fill=accent)
            d.text((cx - lw / 2, y + (bh - px * 1.2) / 2), line, font=f, fill=on_accent)
        y += ih + gap
    if disclosure:
        f = ImageFont.truetype(fpath, max(22, int(w * DISC_PX)))
        lw = d.textlength(disclosure, font=f)
        d.text((cx - lw / 2, y1 - int(w * 0.03)), disclosure, font=f, fill=fg[:3] + (190,))
    out.parent.mkdir(parents=True, exist_ok=True)
    img.convert("RGB").save(out)


def render_disclosure(text: str, size: tuple[int, int], safe: dict, brand: dict, out: Path) -> None:
    """Small persistent label at the bottom-left of the safe area."""
    w, h = size
    x0, y0, x1, y1 = safe_rect(size, safe)
    img = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    f = ImageFont.truetype(font_path(brand.get("font")), max(16, int(w * 0.02)))
    pad = int(w * 0.012)
    tw = d.textlength(text, font=f)
    th = int(f.size * 1.3)
    box = (x0, y1 - th - 2 * pad, x0 + tw + 2 * pad, y1)
    d.rounded_rectangle(box, radius=pad, fill=(0, 0, 0, 120))
    d.text((x0 + pad, y1 - th - pad), text, font=f, fill=(255, 255, 255, 230))
    out.parent.mkdir(parents=True, exist_ok=True)
    img.save(out)


def safe_guide(frame: Image.Image, safe: dict) -> Image.Image:
    """Tint the unsafe (platform UI) area red so QC can see text collisions."""
    img = frame.convert("RGBA")
    x0, y0, x1, y1 = safe_rect(img.size, safe)
    over = Image.new("RGBA", img.size, (255, 0, 0, 40))  # light tint: the frame stays readable
    ImageDraw.Draw(over).rectangle((x0, y0, x1, y1), fill=(0, 0, 0, 0))
    img.alpha_composite(over)
    ImageDraw.Draw(img).rectangle((x0, y0, x1, y1), outline=(255, 0, 0, 200), width=3)
    return img.convert("RGB")
