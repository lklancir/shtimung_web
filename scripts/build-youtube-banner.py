#!/usr/bin/env python3
"""Generira shtimung YouTube channel banner i safe-area pregled."""

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
        "SHTIMUNG_YOUTUBE_OUT",
        PROJECT_ROOT / "output/youtube"
        if not (PROJECT_ROOT / "brand").exists()
        else SOURCE_ROOT / "social/youtube",
    )
)
CHROME = "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"

WIDTH = 2560
HEIGHT = 1440
SAFE_WIDTH = 1546
SAFE_HEIGHT = 423

SG_TTF = (SOURCE_ROOT / "brand/_src/SpaceGrotesk-wght.ttf").as_uri()
INTER_TTF = (SOURCE_ROOT / "brand/_src/Inter-var.ttf").as_uri()
WORDMARK = (SOURCE_ROOT / "brand/wordmark.svg").as_uri()


def html(debug: bool = False) -> str:
    debug_class = " debug" if debug else ""
    return f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<style>
@font-face {{ font-family:'Space Grotesk'; src:url('{SG_TTF}') format('truetype'); font-weight:300 700; }}
@font-face {{ font-family:'Inter'; src:url('{INTER_TTF}') format('truetype'); font-weight:100 900; }}
:root {{
  --bg:#0a0c12; --surface:#10131c; --surface-2:#151925;
  --text:#eef0f6; --dim:#9aa1b5; --amber:#ffb45c; --cyan:#5cd6ff;
  --border:rgba(255,255,255,.10);
}}
* {{ box-sizing:border-box; }}
html, body {{ margin:0; width:{WIDTH}px; height:{HEIGHT}px; overflow:hidden; }}
body {{
  position:relative; background:var(--bg); color:var(--text); font-family:Inter, sans-serif;
}}
body::before {{
  content:""; position:absolute; inset:0;
  background-image:
    linear-gradient(rgba(255,255,255,.018) 1px, transparent 1px),
    linear-gradient(90deg, rgba(255,255,255,.018) 1px, transparent 1px);
  background-size:96px 96px;
  mask-image:linear-gradient(to bottom, transparent 6%, black 38%, black 62%, transparent 94%);
  -webkit-mask-image:linear-gradient(to bottom, transparent 6%, black 38%, black 62%, transparent 94%);
}}
.top-line, .bottom-line {{
  position:absolute; left:0; right:0; height:1px;
  background:linear-gradient(90deg, transparent, rgba(255,255,255,.07) 18%, rgba(255,255,255,.07) 82%, transparent);
}}
.top-line {{ top:292px; }}
.bottom-line {{ bottom:292px; }}

/* Wide-screen ambience: intentionally outside the mobile safe area. */
.room {{ position:absolute; left:86px; top:332px; width:570px; height:776px; opacity:.92; }}
.room-frame {{ position:absolute; inset:0; border:2px solid rgba(255,255,255,.10); border-right-color:rgba(255,255,255,.04); }}
.cabinet {{ position:absolute; left:78px; right:84px; top:155px; height:148px; background:#11151f; border:1px solid var(--border); }}
.cabinet::before {{ content:""; position:absolute; top:0; bottom:0; left:50%; width:1px; background:var(--border); }}
.shelf {{ position:absolute; left:52px; right:58px; top:388px; height:82px; background:#151925; border:1px solid var(--border); }}
.led-strip {{ position:absolute; left:78px; right:84px; top:310px; height:7px; border-radius:5px; background:var(--amber); box-shadow:0 12px 56px 18px rgba(255,180,92,.30); }}
.room-copy {{ position:absolute; left:78px; bottom:96px; color:rgba(154,161,181,.48); font:600 18px/1 'Space Grotesk'; letter-spacing:.18em; text-transform:uppercase; }}
.room-copy strong {{ display:block; margin-top:14px; color:rgba(238,240,246,.60); font:600 34px/1.1 'Space Grotesk'; letter-spacing:0; text-transform:none; }}

.system {{ position:absolute; right:72px; top:350px; width:540px; height:740px; opacity:.92; }}
.system-panel {{ position:absolute; inset:82px 0 82px 0; padding:36px; border:1px solid var(--border); background:rgba(16,19,28,.90); border-radius:16px; }}
.system-head {{ display:flex; align-items:center; justify-content:space-between; padding-bottom:28px; border-bottom:1px solid var(--border); }}
.system-title {{ font:600 28px/1.1 'Space Grotesk'; }}
.system-title small {{ display:block; color:var(--dim); font:500 15px/1.2 Inter; margin-top:8px; }}
.online {{ display:flex; align-items:center; gap:10px; color:var(--cyan); font:600 13px/1 'Space Grotesk'; letter-spacing:.14em; }}
.online::before {{ content:""; width:10px; height:10px; border-radius:50%; background:var(--cyan); box-shadow:0 0 18px rgba(92,214,255,.72); }}
.system-row {{ display:grid; grid-template-columns:52px 1fr auto; gap:18px; align-items:center; min-height:116px; border-bottom:1px solid var(--border); }}
.system-row:last-child {{ border-bottom:0; }}
.system-icon {{ width:50px; height:50px; border-radius:12px; border:1px solid var(--border); background:rgba(255,255,255,.025); display:grid; place-items:center; }}
.system-icon i {{ display:block; width:12px; height:12px; border-radius:50%; background:var(--amber); box-shadow:0 0 18px rgba(255,180,92,.6); }}
.system-icon.sensor i {{ background:var(--cyan); box-shadow:0 0 18px rgba(92,214,255,.65); }}
.system-row strong {{ font:600 20px/1.15 'Space Grotesk'; }}
.system-row small {{ display:block; color:var(--dim); font-size:14px; margin-top:7px; }}
.state {{ color:var(--dim); font:600 13px/1 'Space Grotesk'; letter-spacing:.10em; text-transform:uppercase; }}
.state.on {{ color:var(--amber); }}

.safe {{
  position:absolute; left:50%; top:50%; width:{SAFE_WIDTH}px; height:{SAFE_HEIGHT}px;
  transform:translate(-50%,-50%); display:flex; align-items:center; justify-content:center;
  text-align:center;
}}
.identity {{ position:relative; width:100%; display:flex; flex-direction:column; align-items:center; }}
.wordmark {{ width:510px; height:auto; }}
.tagline {{
  margin-top:34px; color:var(--text); font:600 62px/1.03 'Space Grotesk'; letter-spacing:0;
}}
.tagline .amber {{ color:var(--amber); }}
.topics {{
  display:flex; align-items:center; justify-content:center; gap:24px; margin-top:28px;
  color:var(--dim); font:600 18px/1 'Space Grotesk'; letter-spacing:.12em; text-transform:uppercase;
}}
.topics i {{ width:5px; height:5px; border-radius:50%; background:var(--amber); box-shadow:0 0 12px rgba(255,180,92,.7); }}
.signal-left, .signal-right {{ position:absolute; top:50%; width:360px; height:1px; background:rgba(255,255,255,.07); }}
.signal-left {{ right:calc(50% + 390px); }}
.signal-right {{ left:calc(50% + 390px); }}
.signal-left::after, .signal-right::after {{ content:""; position:absolute; top:-4px; width:9px; height:9px; border-radius:50%; }}
.signal-left::after {{ right:0; background:var(--amber); box-shadow:0 0 18px rgba(255,180,92,.75); }}
.signal-right::after {{ left:0; background:var(--cyan); box-shadow:0 0 18px rgba(92,214,255,.68); }}

.edge-label {{ position:absolute; bottom:104px; color:rgba(154,161,181,.42); font:500 16px/1 'Space Grotesk'; letter-spacing:.12em; text-transform:uppercase; }}
.edge-label.left {{ left:86px; }}
.edge-label.right {{ right:72px; }}

.debug .safe {{ border:3px dashed var(--amber); background:rgba(255,180,92,.045); }}
.debug .safe::before {{
  content:"MOBILE SAFE AREA · NOT PART OF UPLOAD"; position:absolute; left:0; top:-34px;
  color:var(--amber); font:600 17px/1 'Space Grotesk'; letter-spacing:.10em;
}}
</style>
</head>
<body class="{debug_class.strip()}">
  <div class="top-line"></div><div class="bottom-line"></div>

  <section class="room" aria-hidden="true">
    <div class="room-frame"></div><div class="cabinet"></div><div class="led-strip"></div><div class="shelf"></div>
    <div class="room-copy">Scene 04<strong>Evening</strong></div>
  </section>

  <section class="system" aria-hidden="true">
    <div class="system-panel">
      <div class="system-head"><div class="system-title">Home<small>Local control</small></div><span class="online">ONLINE</span></div>
      <div class="system-row"><span class="system-icon"><i></i></span><div><strong>Kitchen light</strong><small>Under cabinet · WLED</small></div><span class="state on">68%</span></div>
      <div class="system-row"><span class="system-icon sensor"><i></i></span><div><strong>Presence</strong><small>Living room sensor</small></div><span class="state">CLEAR</span></div>
      <div class="system-row"><span class="system-icon"><i></i></span><div><strong>Evening scene</strong><small>3 lights · automated</small></div><span class="state on">ACTIVE</span></div>
    </div>
  </section>

  <main class="safe">
    <div class="signal-left"></div><div class="signal-right"></div>
    <div class="identity">
      <img class="wordmark" src="{WORDMARK}" alt="shtimung">
      <div class="tagline">smart home, better living<span class="amber">.</span></div>
      <div class="topics"><span>Home Assistant</span><i></i><span>Automation</span><i></i><span>WLED</span></div>
    </div>
  </main>

  <span class="edge-label left">Pametan dom po mjeri</span>
  <span class="edge-label right">Zagreb · Croatia</span>
</body>
</html>"""


def render(source: Path, target: Path) -> None:
    subprocess.run(
        [
            CHROME,
            "--headless",
            "--disable-gpu",
            "--hide-scrollbars",
            "--allow-file-access-from-files",
            f"--window-size={WIDTH},{HEIGHT}",
            f"--screenshot={target}",
            "--virtual-time-budget=2500",
            source.as_uri(),
        ],
        check=True,
        capture_output=True,
    )


def main() -> None:
    if not Path(CHROME).exists():
        raise SystemExit(f"Chrome nije pronađen: {CHROME}")

    OUT.mkdir(parents=True, exist_ok=True)
    source = OUT / "youtube-banner.html"
    safe_source = OUT / "youtube-banner-safe-area.html"
    banner = OUT / "youtube-banner-2560x1440.png"
    safe_preview = OUT / "youtube-banner-safe-area-preview.png"

    source.write_text(html(), encoding="utf-8")
    safe_source.write_text(html(debug=True), encoding="utf-8")
    render(source, banner)
    render(safe_source, safe_preview)
    safe_source.unlink()

    print(f"Banner: {banner}")
    print(f"Safe-area preview: {safe_preview}")
    print(f"Source: {source}")


if __name__ == "__main__":
    main()
