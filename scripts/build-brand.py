#!/usr/bin/env python3
"""Generira kompletan shtimung brand paket u brand/.

- Vektorizira glifove iz Space Grotesk Bold (nema ovisnosti o instaliranom fontu)
- SVG masteri: logo (tamna/svijetla podloga), wordmark, avatar, favicon
- PNG renderi preko headless Chromea (profilne 320/512/1024, favicon 16/32, apple-touch 180)
- favicon.ico (16+32, PNG-in-ICO)

Pokretanje:  python3 scripts/build-brand.py
"""

import io
import struct
import subprocess
import sys
import tempfile
import urllib.request
from pathlib import Path

from fontTools.pens.svgPathPen import SVGPathPen
from fontTools.pens.transformPen import TransformPen
from fontTools.ttLib import TTFont
from fontTools.varLib.instancer import instantiateVariableFont

ROOT = Path(__file__).resolve().parent.parent
BRAND = ROOT / "www" / "brand"
SRC = BRAND / "_src"
CHROME = "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"
FONT_URL = "https://raw.githubusercontent.com/google/fonts/main/ofl/spacegrotesk/SpaceGrotesk%5Bwght%5D.ttf"

# paleta
AMBER = "#ffb45c"
AMBER_DARK = "#f59a2e"   # amber za svijetle podloge
BG = "#0a0c12"
TEXT = "#eef0f6"
TEXT_LIGHTBG = "#1a1d28"
TEXT_DIM = "#9aa1b5"


def get_font():
    SRC.mkdir(parents=True, exist_ok=True)
    ttf = SRC / "SpaceGrotesk-wght.ttf"
    if not ttf.exists():
        print("↓ Space Grotesk (Google Fonts, OFL licenca)")
        urllib.request.urlretrieve(FONT_URL, ttf)
    font = TTFont(ttf)
    instantiateVariableFont(font, {"wght": 700}, inplace=True)
    return font


def glyph_path(font, char, font_size, x, y, anchor="middle"):
    """SVG path glifa: baseline na y; anchor: middle|left po advance širini."""
    upm = font["head"].unitsPerEm
    scale = font_size / upm
    cmap = font.getBestCmap()
    gname = cmap[ord(char)]
    glyph_set = font.getGlyphSet()
    advance = font["hmtx"][gname][0] * scale
    tx = x - advance / 2 if anchor == "middle" else x
    spen = SVGPathPen(glyph_set)
    pen = TransformPen(spen, (scale, 0, 0, -scale, tx, y))
    glyph_set[gname].draw(pen)
    return spen.getCommands(), advance


def mark_svg(s_fill, amber, halo_opacity, bg=None, rx=0):
    """V9 znak: krov + s + svjetlo. Geometrija identična onoj na webu."""
    font = FONT
    s_path, _ = glyph_path(font, "s", 52, 44, 72)
    bg_rect = f'<rect width="100" height="100" rx="{rx}" fill="{bg}"/>' if bg else ""
    return f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 100 100">
  {bg_rect}
  <path d="M 30 38 L 44 26 L 58 38" fill="none" stroke="{amber}" stroke-width="6" stroke-linecap="round" stroke-linejoin="round"/>
  <path d="{s_path}" fill="{s_fill}"/>
  <circle cx="68" cy="68" r="11" fill="{amber}" opacity="{halo_opacity}"/>
  <circle cx="68" cy="68" r="6" fill="{amber}"/>
</svg>'''


def wordmark_svg():
    """shtim(ung)• — vektorizirani wordmark za tamnu podlogu."""
    font = FONT
    fs, baseline, x = 32, 31, 2
    parts = []
    for i, ch in enumerate("shtimung"):
        fill = TEXT if i < 5 else TEXT_DIM
        path, adv = glyph_path(font, ch, fs, x, baseline, anchor="left")
        parts.append(f'<path d="{path}" fill="{fill}"/>')
        x += adv
    dot_x = x + 5
    parts.append(f'<circle cx="{dot_x:.1f}" cy="{baseline - 3}" r="3.4" fill="{AMBER}"/>')
    w = dot_x + 8
    return f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w:.0f} 40">
  {"".join(parts)}
</svg>'''


def render_png(svg_file, out_png, size, transparent=False):
    html = SRC / f"_render_{out_png.stem}.html"
    html.write_text(
        f'<!doctype html><body style="margin:0"><img src="{svg_file.resolve().as_uri()}" '
        f'width="{size}" height="{size}" style="display:block"></body>'
    )
    cmd = [CHROME, "--headless", "--disable-gpu", f"--screenshot={out_png}",
           f"--window-size={size},{size}", "--hide-scrollbars"]
    if transparent:
        cmd.append("--default-background-color=00000000")
    cmd.append(html.as_uri())
    subprocess.run(cmd, cwd=SRC, capture_output=True, check=True)
    html.unlink()


def build_ico(png_paths, out):
    """PNG-in-ICO (validno za 16/32; svi moderni parseri to čitaju)."""
    entries, blobs, offset = [], [], 6 + 16 * len(png_paths)
    for p in png_paths:
        data = p.read_bytes()
        size = int(p.stem.rsplit("-", 1)[-1])
        dim = 0 if size == 256 else size
        entries.append(struct.pack("<BBBBHHII", dim, dim, 0, 0, 1, 32, len(data), offset))
        blobs.append(data)
        offset += len(data)
    out.write_bytes(struct.pack("<HHH", 0, 1, len(png_paths)) + b"".join(entries) + b"".join(blobs))


FONT = get_font()
BRAND.mkdir(exist_ok=True)

# ---------- SVG masteri ----------
(BRAND / "logo.svg").write_text(mark_svg(TEXT, AMBER, 0.2))
(BRAND / "logo-light.svg").write_text(mark_svg(TEXT_LIGHTBG, AMBER_DARK, 0.25))
(BRAND / "avatar.svg").write_text(mark_svg(TEXT, AMBER, 0.2, bg=BG))
(BRAND / "favicon.svg").write_text(mark_svg(TEXT, AMBER, 0.2, bg=BG, rx=20))
(BRAND / "wordmark.svg").write_text(wordmark_svg())
print("✓ SVG masteri")

# ---------- PNG renderi ----------
for size in (1024, 512, 320):
    render_png(BRAND / "avatar.svg", BRAND / f"avatar-{size}.png", size)
render_png(BRAND / "avatar.svg", BRAND / "apple-touch-icon.png", 180)
for size in (32, 16):
    render_png(BRAND / "favicon.svg", BRAND / f"favicon-{size}.png", size)
render_png(BRAND / "logo.svg", BRAND / "logo-1024.png", 1024, transparent=True)
render_png(BRAND / "logo-light.svg", BRAND / "logo-light-1024.png", 1024, transparent=True)
print("✓ PNG renderi")

# ---------- favicon.ico ----------
build_ico([BRAND / "favicon-16.png", BRAND / "favicon-32.png"], BRAND / "favicon.ico")
print("✓ favicon.ico")

print(f"\nGotovo → {BRAND}")
