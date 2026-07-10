#!/usr/bin/env python3
"""Generira shtimung Facebook cover i desktop/mobile crop preglede."""

import os
import subprocess
from pathlib import Path


HERE = Path(__file__).resolve()
PROJECT_ROOT = HERE.parent.parent
SOURCE_ROOT = Path(
    os.environ.get(
        "SHTIMUNG_SOURCE_ROOT",
        PROJECT_ROOT
        if (PROJECT_ROOT / "brand").exists()
        else "/Users/mrcina/Dev/personal/smarthome/shtimung",
    )
)
OUT = Path(
    os.environ.get(
        "SHTIMUNG_FACEBOOK_OUT",
        PROJECT_ROOT / "output/facebook"
        if not (PROJECT_ROOT / "brand").exists()
        else SOURCE_ROOT / "social/facebook",
    )
)
CHROME = "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"
SRGB = "/System/Library/ColorSync/Profiles/sRGB Profile.icc"

WIDTH = 820
HEIGHT = 360
MAX_JPEG_BYTES = 100_000

SG_TTF = (SOURCE_ROOT / "brand/_src/SpaceGrotesk-wght.ttf").as_uri()
INTER_TTF = (SOURCE_ROOT / "brand/_src/Inter-var.ttf").as_uri()
HTML = f"""<!doctype html>
<html lang="hr">
<head>
<meta charset="utf-8">
<style>
@font-face {{ font-family:'Space Grotesk'; src:url('{SG_TTF}') format('truetype'); font-weight:300 700; }}
@font-face {{ font-family:'Inter'; src:url('{INTER_TTF}') format('truetype'); font-weight:100 900; }}
:root {{
  --bg:#0a0c12; --text:#eef0f6; --dim:#9aa1b5;
  --amber:#ffb45c; --cyan:#5cd6ff; --pink:#ff5c8a;
}}
* {{ box-sizing:border-box; }}
html, body {{ margin:0; width:{WIDTH}px; height:{HEIGHT}px; overflow:hidden; }}
body {{
  position:relative; display:flex; align-items:center; justify-content:center;
  background:var(--bg); color:var(--text); font-family:Inter, sans-serif;
}}
.hero-bg {{
  position:absolute; inset:0;
  background:
    radial-gradient(ellipse 58% 54% at 50% 116%, rgba(255,180,92,.17), transparent 72%),
    radial-gradient(ellipse 35% 58% at 89% -14%, rgba(92,214,255,.11), transparent 72%),
    radial-gradient(ellipse 30% 44% at 7% 0%, rgba(255,92,138,.06), transparent 70%);
}}
.grid {{
  position:absolute; inset:0;
  background-image:
    linear-gradient(rgba(255,255,255,.018) 1px, transparent 1px),
    linear-gradient(90deg, rgba(255,255,255,.018) 1px, transparent 1px);
  background-size:42px 42px;
  mask-image:radial-gradient(ellipse 66% 90% at 50% 48%, black 22%, transparent 82%);
  -webkit-mask-image:radial-gradient(ellipse 66% 90% at 50% 48%, black 22%, transparent 82%);
}}
.sequins {{ position:absolute; inset:0; overflow:hidden; opacity:.28; }}
.wave {{ position:absolute; left:35px; right:35px; top:77px; height:162px; }}
.wave span {{
  position:absolute; width:4px; height:4px; border-radius:50%;
  background:rgba(238,240,246,.16); box-shadow:0 0 9px rgba(238,240,246,.08);
}}
.wave span:nth-child(1) {{ left:0%; top:80px; }}
.wave span:nth-child(2) {{ left:5%; top:61px; }}
.wave span:nth-child(3) {{ left:10%; top:45px; }}
.wave span:nth-child(4) {{ left:15%; top:34px; background:rgba(255,180,92,.33); }}
.wave span:nth-child(5) {{ left:20%; top:28px; }}
.wave span:nth-child(6) {{ left:25%; top:30px; }}
.wave span:nth-child(7) {{ left:30%; top:40px; }}
.wave span:nth-child(8) {{ left:35%; top:54px; }}
.wave span:nth-child(9) {{ left:40%; top:67px; }}
.wave span:nth-child(10) {{ left:45%; top:76px; }}
.wave span:nth-child(11) {{ left:50%; top:80px; background:rgba(255,180,92,.36); }}
.wave span:nth-child(12) {{ left:55%; top:75px; }}
.wave span:nth-child(13) {{ left:60%; top:64px; }}
.wave span:nth-child(14) {{ left:65%; top:48px; }}
.wave span:nth-child(15) {{ left:70%; top:34px; }}
.wave span:nth-child(16) {{ left:75%; top:27px; background:rgba(92,214,255,.38); }}
.wave span:nth-child(17) {{ left:80%; top:30px; }}
.wave span:nth-child(18) {{ left:85%; top:42px; }}
.wave span:nth-child(19) {{ left:90%; top:59px; }}
.wave span:nth-child(20) {{ left:95%; top:78px; }}
.wave::before, .wave::after {{
  content:""; position:absolute; left:0; right:0; height:1px;
  background:linear-gradient(90deg, transparent, rgba(255,255,255,.08), transparent);
}}
.wave::before {{ top:26px; transform:rotate(2deg); }}
.wave::after {{ top:100px; transform:rotate(-2deg); }}

.safe {{
  position:relative; z-index:2; width:640px; height:312px;
  display:flex; flex-direction:column; align-items:center; justify-content:center; text-align:center;
}}
h1 {{
  margin:0; font:600 58px/.98 'Space Grotesk'; letter-spacing:-.018em;
}}
h1 em {{
  display:inline-block; font-style:normal;
  background:linear-gradient(90deg,var(--amber),var(--cyan));
  -webkit-background-clip:text; background-clip:text; -webkit-text-fill-color:transparent;
}}
.lead {{ margin:18px 0 0; color:var(--dim); font-size:17px; line-height:1.35; }}
.lead strong {{ color:var(--text); font-weight:600; }}
.topics {{
  display:flex; align-items:center; justify-content:center; gap:13px; margin-top:20px;
  color:rgba(154,161,181,.80); font:600 10px/1 'Space Grotesk';
  letter-spacing:.13em; text-transform:uppercase;
}}
.topics i {{ width:4px; height:4px; border-radius:50%; background:var(--amber); box-shadow:0 0 9px rgba(255,180,92,.75); }}
.light {{
  position:absolute; z-index:1; width:7px; height:7px; border-radius:50%;
}}
.light.amber {{ left:68px; bottom:76px; background:var(--amber); box-shadow:0 0 22px 5px rgba(255,180,92,.24); }}
.light.cyan {{ right:68px; top:74px; background:var(--cyan); box-shadow:0 0 22px 5px rgba(92,214,255,.20); }}
</style>
</head>
<body>
  <div class="hero-bg"></div><div class="grid"></div>
  <div class="sequins"><div class="wave">{''.join('<span></span>' for _ in range(20))}</div></div>
  <span class="light amber"></span><span class="light cyan"></span>
  <main class="safe">
    <h1>Dom koji te <em>razumije.</em></h1>
    <p class="lead">Svjetlo, ambijent i automatizacije koje rade same. <strong>Čisti štimung.</strong></p>
    <div class="topics"><span>Home Assistant</span><i></i><span>Automatizacije</span><i></i><span>WLED</span></div>
  </main>
</body>
</html>"""


def run(command: list[str]) -> None:
    subprocess.run(command, check=True, capture_output=True)


def to_jpeg(source: Path, target: Path, quality: int) -> None:
    run(
        [
            "sips",
            "-m",
            SRGB,
            "-s",
            "format",
            "jpeg",
            "-s",
            "formatOptions",
            str(quality),
            str(source),
            "--out",
            str(target),
        ]
    )


def make_crop(source: Path, target: Path, width: int, height: int) -> None:
    run(
        [
            "sips",
            "--cropToHeightWidth",
            str(height),
            str(width),
            str(source),
            "--out",
            str(target),
        ]
    )


def main() -> None:
    if not Path(CHROME).exists():
        raise SystemExit(f"Chrome nije pronađen: {CHROME}")

    OUT.mkdir(parents=True, exist_ok=True)
    source = OUT / "facebook-cover.html"
    master_png = OUT / "facebook-cover-master-820x360.png"
    final_jpg = OUT / "facebook-cover-820x360.jpg"
    desktop_png = OUT / "facebook-cover-desktop-preview-820x312.png"
    mobile_png = OUT / "facebook-cover-mobile-preview-640x360.png"
    desktop_jpg = OUT / "facebook-cover-desktop-preview-820x312.jpg"
    mobile_jpg = OUT / "facebook-cover-mobile-preview-640x360.jpg"

    source.write_text(HTML, encoding="utf-8")
    run(
        [
            CHROME,
            "--headless",
            "--disable-gpu",
            "--hide-scrollbars",
            "--allow-file-access-from-files",
            f"--window-size={WIDTH},{HEIGHT}",
            f"--screenshot={master_png}",
            "--virtual-time-budget=2500",
            source.as_uri(),
        ]
    )

    for quality in (96, 92, 88, 84, 80):
        to_jpeg(master_png, final_jpg, quality)
        if final_jpg.stat().st_size < MAX_JPEG_BYTES:
            break

    if final_jpg.stat().st_size >= MAX_JPEG_BYTES:
        raise SystemExit("JPG je i nakon kompresije veći od 100 KB")

    make_crop(master_png, desktop_png, 820, 312)
    make_crop(master_png, mobile_png, 640, 360)
    to_jpeg(desktop_png, desktop_jpg, quality)
    to_jpeg(mobile_png, mobile_jpg, quality)
    desktop_png.unlink()
    mobile_png.unlink()

    print(f"Upload: {final_jpg} ({final_jpg.stat().st_size / 1024:.1f} KB)")
    print(f"Desktop preview: {desktop_jpg}")
    print(f"Mobile preview: {mobile_jpg}")
    print(f"Source: {source}")


if __name__ == "__main__":
    main()
