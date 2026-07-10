#!/usr/bin/env python3
"""Generira drugi shtimung social set u IG feed i square formatima."""

import os
import re
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
OUT = Path(os.environ.get("SHTIMUNG_SOCIAL_OUT", SOURCE_ROOT / "social"))
TMP = OUT / "_tmp"
CHROME = "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"

FORMATS = [
    ("", 1080, 1350, 1.0),
    ("square", 1080, 1080, 0.8),
]

SG_TTF = (SOURCE_ROOT / "brand/_src/SpaceGrotesk-wght.ttf").as_uri()
INTER_TTF = (SOURCE_ROOT / "brand/_src/Inter-var.ttf").as_uri()
LOGO = (SOURCE_ROOT / "brand/logo.svg").as_uri()


BASE_CSS = f"""
@font-face {{ font-family:'Space Grotesk'; src:url('{SG_TTF}') format('truetype'); font-weight:300 700; }}
@font-face {{ font-family:'Inter'; src:url('{INTER_TTF}') format('truetype'); font-weight:100 900; }}
:root {{
  --bg:#0a0c12; --surface:#10131c; --surface-2:#151925;
  --text:#eef0f6; --dim:#9aa1b5; --amber:#ffb45c; --amber-dark:#f59a2e;
  --cyan:#5cd6ff; --border:rgba(255,255,255,.09);
}}
* {{ margin:0; padding:0; box-sizing:border-box; }}
body {{
  width:__W__px; height:__H__px; overflow:hidden; position:relative;
  background:var(--bg); color:var(--text); font-family:Inter, sans-serif;
  display:flex; flex-direction:column; padding:84px 88px 76px;
}}
body::before {{
  content:""; position:absolute; inset:0; pointer-events:none;
  background-image:
    linear-gradient(rgba(255,255,255,.018) 1px, transparent 1px),
    linear-gradient(90deg, rgba(255,255,255,.018) 1px, transparent 1px);
  background-size:72px 72px;
  mask-image:linear-gradient(to bottom, black, transparent 70%);
  -webkit-mask-image:linear-gradient(to bottom, black, transparent 70%);
}}
.top, .content, .footer {{ position:relative; z-index:1; width:100%; min-width:0; }}
.top {{ display:flex; align-items:center; justify-content:space-between; min-height:56px; }}
.top img {{ width:54px; height:54px; object-fit:contain; }}
.kicker {{
  color:var(--amber); font:600 24px/1 'Space Grotesk';
  letter-spacing:.24em; text-transform:uppercase;
}}
.content {{ flex:1; display:flex; flex-direction:column; justify-content:center; padding:44px 0; }}
h1 {{
  font:600 82px/1.05 'Space Grotesk'; letter-spacing:-.018em;
  max-width:920px;
}}
h1 .amber {{ color:var(--amber); }}
.lead {{ color:var(--dim); font-size:31px; line-height:1.42; margin-top:26px; max-width:790px; }}
.lead strong {{ color:var(--text); font-weight:600; }}
.footer {{ display:flex; align-items:center; justify-content:space-between; min-height:40px; }}
.site {{ color:var(--dim); font:600 26px/1 'Space Grotesk'; }}
.site-dot {{
  display:inline-block; width:11px; height:11px; margin-left:8px; border-radius:50%;
  background:var(--amber); box-shadow:0 0 18px rgba(255,180,92,.65);
}}
.footer-note {{ color:var(--dim); font:500 20px/1 'Space Grotesk'; }}
.panel {{ background:rgba(16,19,28,.94); border:1px solid var(--border); border-radius:16px; }}
.pill {{
  display:inline-flex; align-items:center; gap:10px; min-height:42px; padding:0 18px;
  border:1px solid var(--border); border-radius:999px; color:var(--dim);
  background:rgba(255,255,255,.025); font-size:18px; font-weight:600;
}}
.status-dot {{ width:9px; height:9px; border-radius:50%; background:var(--cyan); box-shadow:0 0 15px rgba(92,214,255,.55); }}
"""


def page(kicker: str, body: str, footer_note: str = "Zagreb") -> str:
    return f"""<!doctype html>
<html lang="hr"><head><meta charset="utf-8"><style>{BASE_CSS}</style></head>
<body>
  <header class="top"><span class="kicker">{kicker}</span><img src="{LOGO}" alt="shtimung"></header>
  <main class="content">{body}</main>
  <footer class="footer"><span class="site">shtimung.hr<span class="site-dot"></span></span><span class="footer-note">{footer_note}</span></footer>
</body></html>"""


SCENE_CSS = """
.scene-layout { display:grid; grid-template-columns:1.06fr .94fr; align-items:center; gap:54px; margin-top:42px; }
.scene-layout h1 { font-size:76px; }
.control { padding:30px; box-shadow:0 28px 80px rgba(0,0,0,.25); }
.control-head { display:flex; align-items:center; justify-content:space-between; }
.room { font:600 28px/1.15 'Space Grotesk'; }
.room small { display:block; color:var(--dim); font:500 16px/1.3 Inter; margin-top:7px; }
.power { width:58px; height:58px; border-radius:50%; display:grid; place-items:center; background:rgba(255,180,92,.15); border:1px solid rgba(255,180,92,.5); }
.power::before { content:""; width:16px; height:22px; border:3px solid var(--amber); border-top:0; border-radius:0 0 12px 12px; }
.power::after { content:""; position:absolute; width:3px; height:16px; top:17px; background:var(--amber); border-radius:2px; }
.power { position:relative; }
.lightbar { height:92px; margin:26px 0 22px; border-radius:10px; position:relative; overflow:hidden; background:#171a22; }
.lightbar::before { content:""; position:absolute; left:16px; right:16px; top:43px; height:6px; border-radius:8px; background:linear-gradient(90deg,#ffb45c,#ffd79d,#f59a2e); box-shadow:0 0 30px rgba(255,180,92,.75); }
.lightbar span { position:absolute; right:14px; bottom:10px; color:var(--dim); font-size:14px; }
.scene-label { color:var(--dim); font-size:15px; letter-spacing:.14em; text-transform:uppercase; margin-bottom:12px; }
.scenes { display:grid; grid-template-columns:repeat(3,1fr); gap:10px; }
.scene { min-height:70px; display:flex; flex-direction:column; justify-content:center; padding:0 13px; border:1px solid var(--border); border-radius:10px; color:var(--dim); font-size:15px; }
.scene i { width:12px; height:12px; border-radius:50%; margin-bottom:8px; background:#697080; }
.scene.active { color:var(--text); border-color:rgba(255,180,92,.48); background:rgba(255,180,92,.08); }
.scene.active i { background:var(--amber); box-shadow:0 0 12px rgba(255,180,92,.7); }
"""

AUTOMATION_CSS = """
.automation h1 { margin-top:44px; max-width:880px; }
.flow { display:grid; grid-template-columns:minmax(0,1fr) 62px minmax(0,1fr) 62px minmax(0,1fr); align-items:stretch; margin-top:62px; min-width:0; }
.step { min-height:220px; padding:28px 24px; display:flex; flex-direction:column; justify-content:space-between; }
.step-no { color:var(--dim); font:600 16px/1 'Space Grotesk'; letter-spacing:.15em; }
.step-icon { width:58px; height:58px; border-radius:50%; border:1px solid var(--border); position:relative; }
.step.sensor .step-icon { border-color:rgba(92,214,255,.45); box-shadow:inset 0 0 0 14px rgba(92,214,255,.05); }
.step.sensor .step-icon::after { content:""; position:absolute; inset:19px; border-radius:50%; background:var(--cyan); box-shadow:0 0 17px rgba(92,214,255,.7); }
.step.logic .step-icon::before, .step.logic .step-icon::after { content:""; position:absolute; left:14px; right:14px; height:2px; background:var(--text); }
.step.logic .step-icon::before { top:20px; box-shadow:0 9px 0 var(--text); }
.step.logic .step-icon::after { width:6px; height:6px; left:21px; top:18px; border-radius:50%; background:var(--amber); box-shadow:15px 9px 0 var(--cyan); }
.step.light .step-icon { border-color:rgba(255,180,92,.55); background:rgba(255,180,92,.1); }
.step.light .step-icon::after { content:""; position:absolute; inset:17px; border-radius:50%; background:var(--amber); box-shadow:0 0 25px rgba(255,180,92,.75); }
.step strong { display:block; font:600 24px/1.15 'Space Grotesk'; }
.step small { display:block; color:var(--dim); font-size:16px; line-height:1.35; margin-top:8px; }
.arrow { align-self:center; height:1px; background:rgba(255,255,255,.22); position:relative; }
.arrow::after { content:""; position:absolute; right:0; top:-4px; width:8px; height:8px; border-top:1px solid rgba(255,255,255,.4); border-right:1px solid rgba(255,255,255,.4); transform:rotate(45deg); }
"""

LOCAL_CSS = """
.local-layout { display:grid; grid-template-columns:1fr .92fr; gap:58px; align-items:center; margin-top:44px; }
.local-layout h1 { font-size:74px; }
.stack { padding:18px; }
.stack-row { display:grid; grid-template-columns:42px 1fr auto; gap:14px; align-items:center; min-height:90px; padding:0 16px; border-bottom:1px solid var(--border); }
.stack-row:last-child { border-bottom:0; }
.stack-icon { width:32px; height:32px; border-radius:8px; background:rgba(255,255,255,.055); display:grid; place-items:center; color:var(--text); font:600 14px/1 'Space Grotesk'; }
.stack-row strong { font:600 21px/1.2 'Space Grotesk'; }
.stack-row small { display:block; color:var(--dim); font-size:14px; margin-top:5px; }
.ok { color:var(--cyan); font:600 13px/1 'Space Grotesk'; letter-spacing:.12em; }
.local-badge { display:inline-flex; align-items:center; gap:12px; margin-top:28px; color:var(--dim); font-size:18px; }
.local-badge::before { content:""; width:13px; height:13px; border-radius:50%; background:var(--cyan); box-shadow:0 0 18px rgba(92,214,255,.65); }
"""

LED_CSS = """
.led h1 { margin-top:42px; }
.rooms { display:grid; grid-template-columns:1fr 1fr; gap:18px; margin-top:48px; }
.room-visual { height:320px; border:1px solid var(--border); border-radius:16px; overflow:hidden; position:relative; background:#11141c; }
.room-visual::before { content:""; position:absolute; left:40px; right:40px; top:52px; height:168px; border:2px solid rgba(255,255,255,.13); border-bottom:0; }
.room-visual::after { content:""; position:absolute; left:56px; right:56px; bottom:58px; height:44px; background:#181c26; border:1px solid rgba(255,255,255,.08); }
.room-visual .shelf { position:absolute; left:74px; right:74px; top:164px; height:8px; background:#252a35; z-index:1; }
.room-visual .strip { position:absolute; left:74px; right:74px; top:174px; height:4px; z-index:2; }
.room-visual.off .strip { background:#484d57; }
.room-visual.on { background:linear-gradient(180deg,#11141c 25%,#18140f 100%); }
.room-visual.on .strip { background:var(--amber); box-shadow:0 8px 32px 10px rgba(255,180,92,.35); }
.room-visual .caption { position:absolute; left:20px; bottom:16px; color:var(--dim); font:600 15px/1 'Space Grotesk'; letter-spacing:.1em; text-transform:uppercase; z-index:3; }
.room-visual.on .caption { color:var(--amber); }
.rooms-note { display:flex; justify-content:space-between; margin-top:18px; color:var(--dim); font-size:17px; }
.rooms-note strong { color:var(--text); }
"""

SHOWROOM_CSS = """
.showroom-layout { display:grid; grid-template-columns:1.04fr .96fr; gap:52px; align-items:center; margin-top:40px; }
.showroom-layout h1 { font-size:74px; }
.showroom-map { min-height:418px; padding:24px; position:relative; }
.map-label { color:var(--amber); font:600 16px/1 'Space Grotesk'; letter-spacing:.18em; text-transform:uppercase; }
.floorplan { position:absolute; left:24px; right:24px; top:72px; bottom:24px; border:2px solid rgba(255,255,255,.16); }
.floorplan::before { content:""; position:absolute; left:42%; top:0; bottom:0; width:2px; background:rgba(255,255,255,.14); }
.floorplan::after { content:""; position:absolute; left:42%; right:0; top:53%; height:2px; background:rgba(255,255,255,.14); }
.zone { position:absolute; color:var(--dim); font-size:14px; }
.zone i { display:block; width:11px; height:11px; border-radius:50%; margin-bottom:7px; }
.zone.kitchen { left:30px; top:42px; }
.zone.kitchen i, .zone.living i { background:var(--amber); box-shadow:0 0 18px rgba(255,180,92,.75); }
.zone.living { left:52%; top:40px; }
.zone.ha { left:52%; top:66%; }
.zone.ha i { background:var(--cyan); box-shadow:0 0 18px rgba(92,214,255,.7); }
.showroom-tags { display:flex; flex-wrap:wrap; gap:10px; margin-top:26px; }
"""


POSTS = {
    "05-jedan-dodir": page(
        "Scena · Večer",
        f"""<style>{SCENE_CSS}</style>
        <section class="scene-layout">
          <div>
            <h1>Jedan dodir.<br>Cijeli <span class="amber">štimung</span>.</h1>
            <p class="lead">Svjetla, jačina i boje mijenjaju se zajedno. <strong>Scena pamti sve.</strong></p>
          </div>
          <div class="panel control">
            <div class="control-head"><div class="room">Dnevni boravak<small>2 LED zone · aktivne</small></div><div class="power"></div></div>
            <div class="lightbar"><span>68%</span></div>
            <div class="scene-label">Scene</div>
            <div class="scenes"><div class="scene"><i></i>Toplo</div><div class="scene active"><i></i>Večer</div><div class="scene"><i></i>Film</div></div>
          </div>
        </section>""",
        "Home Assistant + WLED",
    ),
    "06-dodes-doma": page(
        "Jedna automatizacija",
        f"""<style>{AUTOMATION_CSS}</style>
        <section class="automation">
          <h1>Dođeš doma.<br>Dom je već <span class="amber">spreman</span>.</h1>
          <div class="flow">
            <div class="panel step sensor"><span class="step-no">01</span><div class="step-icon"></div><div><strong>Stigao si</strong><small>Senzor registrira dolazak.</small></div></div>
            <div class="arrow"></div>
            <div class="panel step logic"><span class="step-no">02</span><div class="step-icon"></div><div><strong>Dom provjeri</strong><small>Mrak je i netko je doma.</small></div></div>
            <div class="arrow"></div>
            <div class="panel step light"><span class="step-no">03</span><div class="step-icon"></div><div><strong>Večer se pali</strong><small>Svjetlo baš kako voliš.</small></div></div>
          </div>
        </section>""",
        "Radi samo kad ima smisla",
    ),
    "07-sustav-je-tvoj": page(
        "Bez vendor lock-ina",
        f"""<style>{LOCAL_CSS}</style>
        <section class="local-layout">
          <div>
            <h1>Pametan dom koji ostaje <span class="amber">tvoj</span>.</h1>
            <p class="lead">Lokalno, dokumentirano i složeno po mjeri. <strong>Bez obavezne pretplate.</strong></p>
            <div class="local-badge">Sustav radi i bez interneta</div>
          </div>
          <div class="panel stack">
            <div class="stack-row"><span class="stack-icon">HA</span><div><strong>Home Assistant</strong><small>Kontrola ostaje kod tebe</small></div><span class="ok">LOKALNO</span></div>
            <div class="stack-row"><span class="stack-icon">01</span><div><strong>Dokumentacija</strong><small>Znaš što je ugrađeno</small></div><span class="ok">TVOJE</span></div>
            <div class="stack-row"><span class="stack-icon">↗</span><div><strong>Nadogradivo</strong><small>Sustav raste s domom</small></div><span class="ok">OTVORENO</span></div>
          </div>
        </section>""",
        "Open-source temelj",
    ),
    "08-ista-soba": page(
        "LED ambijent",
        f"""<style>{LED_CSS}</style>
        <section class="led">
          <h1>Ista soba.<br>Drugi <span class="amber">osjećaj</span>.</h1>
          <div class="rooms">
            <div class="room-visual off"><span class="shelf"></span><span class="strip"></span><span class="caption">Bez scene</span></div>
            <div class="room-visual on"><span class="shelf"></span><span class="strip"></span><span class="caption">Scena Večer</span></div>
          </div>
          <div class="rooms-note"><span>LED profil + WLED kontrola</span><strong>Svjetlo mijenja prostor.</strong></div>
        </section>""",
        "Ambijent po mjeri",
    ),
    "09-living-showroom": page(
        "Living showroom · Zagreb",
        f"""<style>{SHOWROOM_CSS}</style>
        <section class="showroom-layout">
          <div>
            <h1>Ne moraš zamišljati.<br><span class="amber">Dođi vidjeti.</span></h1>
            <p class="lead">Pravi stan, pravi uređaji i automatizacije koje svakodnevno rade.</p>
            <div class="showroom-tags"><span class="pill"><span class="status-dot"></span>Home Assistant</span><span class="pill">WLED scene</span><span class="pill">Automatizacije</span></div>
          </div>
          <div class="panel showroom-map">
            <div class="map-label">shtimung stan</div>
            <div class="floorplan"><span class="zone kitchen"><i></i>Kuhinja<br>WLED</span><span class="zone living"><i></i>Dnevni<br>ambijent</span><span class="zone ha"><i></i>Lokalna<br>kontrola</span></div>
          </div>
        </section>""",
        "Javi se za termin",
    ),
}


def scale_html(html: str, scale: float) -> str:
    if scale == 1.0:
        return html
    return re.sub(
        r"(\d+(?:\.\d+)?)px",
        lambda match: f"{float(match.group(1)) * scale:.0f}px",
        html,
    )


def main() -> None:
    if not Path(CHROME).exists():
        raise SystemExit(f"Chrome nije pronađen: {CHROME}")

    TMP.mkdir(parents=True, exist_ok=True)
    rendered = []

    for folder, width, height, scale in FORMATS:
        out_dir = OUT / folder
        out_dir.mkdir(parents=True, exist_ok=True)

        for name, source in POSTS.items():
            html = scale_html(source, scale)
            html = html.replace("__W__", str(width)).replace("__H__", str(height))
            html_path = TMP / f"{folder}-{name}.html"
            image_path = out_dir / f"{name}.png"
            html_path.write_text(html, encoding="utf-8")
            subprocess.run(
                [
                    CHROME,
                    "--headless",
                    "--disable-gpu",
                    "--hide-scrollbars",
                    "--allow-file-access-from-files",
                    f"--window-size={width},{height}",
                    f"--screenshot={image_path}",
                    "--virtual-time-budget=2500",
                    html_path.as_uri(),
                ],
                check=True,
                capture_output=True,
            )
            rendered.append(image_path)
            print(f"  ok  {image_path.relative_to(OUT)}")

    for html_path in TMP.iterdir():
        html_path.unlink()
    TMP.rmdir()
    print(f"\nGotovo: {len(rendered)} vizuala u {OUT}")


if __name__ == "__main__":
    main()
