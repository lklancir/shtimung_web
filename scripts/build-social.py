#!/usr/bin/env python3
"""Generira social media vizuale (Instagram/Facebook, 1080x1350) u social/.

Isti princip kao build-brand.py: HTML template + headless Chrome render.
Fontovi se učitavaju lokalno iz brand/_src/ (bez mreže, bez FOUT-a).

Pokretanje:  python3 scripts/build-social.py
"""

import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "social"
TMP = OUT / "_tmp"
CHROME = "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"

W, H = 1080, 1350

SG_TTF = (ROOT / "brand/_src/SpaceGrotesk-wght.ttf").as_uri()
INTER_TTF = (ROOT / "brand/_src/Inter-var.ttf").as_uri()
LOGO = (ROOT / "brand/logo.svg").as_uri()
WORDMARK = (ROOT / "brand/wordmark.svg").as_uri()

BASE_CSS = f"""
@font-face {{ font-family:'Space Grotesk'; src:url('{SG_TTF}') format('truetype'); font-weight:300 700; }}
@font-face {{ font-family:'Inter'; src:url('{INTER_TTF}') format('truetype'); font-weight:100 900; }}
* {{ margin:0; padding:0; box-sizing:border-box; }}
body {{
  width:{W}px; height:{H}px; overflow:hidden; position:relative;
  background:#0a0c12; color:#eef0f6; font-family:Inter, sans-serif;
  display:flex; flex-direction:column; padding:96px;
}}
/* pozadinski štih kao hero na webu */
body::before {{
  content:""; position:absolute; inset:0; pointer-events:none;
  background:
    radial-gradient(ellipse 65% 45% at 50% 115%, rgba(255,180,92,.14), transparent 70%),
    radial-gradient(ellipse 45% 35% at 85% -10%, rgba(92,214,255,.07), transparent 70%);
}}
body::after {{
  content:""; position:absolute; inset:0; pointer-events:none;
  background-image:
    linear-gradient(rgba(255,255,255,.022) 1px, transparent 1px),
    linear-gradient(90deg, rgba(255,255,255,.022) 1px, transparent 1px);
  background-size:72px 72px;
  mask-image:radial-gradient(ellipse 75% 65% at 50% 45%, black 25%, transparent 80%);
  -webkit-mask-image:radial-gradient(ellipse 75% 65% at 50% 45%, black 25%, transparent 80%);
}}
.top {{ display:flex; justify-content:space-between; align-items:center; z-index:1; }}
.top img {{ height:64px; }}
.kicker {{
  font-family:'Space Grotesk'; font-weight:600; font-size:26px;
  letter-spacing:.28em; text-transform:uppercase; color:#ffb45c;
}}
.mid {{ flex:1; display:flex; flex-direction:column; justify-content:center; z-index:1; }}
h1 {{ font-family:'Space Grotesk'; font-weight:600; font-size:104px; line-height:1.06; letter-spacing:-0.02em; }}
h1 .amber {{ color:#ffb45c; }}
.sub {{ font-size:38px; color:#9aa1b5; margin-top:36px; max-width:22em; line-height:1.5; }}
.sub strong {{ color:#eef0f6; font-weight:600; }}
.bottom {{ display:flex; justify-content:space-between; align-items:center; z-index:1; }}
.site {{ font-family:'Space Grotesk'; font-weight:600; font-size:30px; color:#9aa1b5; }}
.site i {{ display:inline-block; width:12px; height:12px; border-radius:50%; background:#ffb45c;
  box-shadow:0 0 24px #ffb45c; margin-left:8px; }}
.dots {{ display:flex; gap:12px; }}
.dots span {{ width:14px; height:14px; border-radius:50%; background:rgba(255,255,255,.14); }}
.dots span.on {{ background:#ffb45c; box-shadow:0 0 16px rgba(255,180,92,.6); }}
.center {{ text-align:center; align-items:center; }}
.big-logo {{ width:420px; filter:drop-shadow(0 0 80px rgba(255,180,92,.25)); }}
.big-wordmark {{ width:760px; }}
.icon {{ font-size:110px; color:#ffb45c; text-shadow:0 0 60px rgba(255,180,92,.5); margin-bottom:40px; }}
"""


def dots(n, on):
    return '<div class="dots">' + "".join(
        f'<span class="{"on" if i == on else ""}"></span>' for i in range(n)
    ) + "</div>"


def page(kicker, mid_html, footer_right="", center=False):
    return f"""<!doctype html><html><head><meta charset="utf-8"><style>{BASE_CSS}</style></head>
<body>
  <div class="top"><span class="kicker">{kicker}</span><img src="{LOGO}"></div>
  <div class="mid {'center' if center else ''}">{mid_html}</div>
  <div class="bottom"><span class="site">shtimung.hr<i></i></span>{footer_right}</div>
</body></html>"""


POSTS = {
    # ---- 01: launch ----
    "01-launch": page(
        "Zagreb", f"""
        <img class="big-logo" src="{LOGO}" style="margin-bottom:80px">
        <h1>Upalili smo se<span class="amber">.</span></h1>
        <p class="sub">Pametan dom po mjeri. Svjetlo, ambijent i automatizacije koje rade same. <strong>Štimung!</strong></p>
        """, center=True),

    # ---- 02: brand priča (carousel 3) ----
    "02-prica-1": page(
        "Zašto sh?", f"""
        <img class="big-wordmark" src="{WORDMARK}" style="margin-bottom:70px">
        <h1 style="font-size:84px">Pišemo se sh.<br>Čitamo se <span class="amber">š</span>.</h1>
        """, dots(3, 0), center=True),
    "02-prica-2": page(
        "Zašto sh?", f"""
        <img class="big-logo" src="{LOGO}" style="margin-bottom:80px">
        <h1 style="font-size:84px">Kvačica se<br>okrenula u krov<span class="amber">.</span></h1>
        """, dots(3, 1), center=True),
    "02-prica-3": page(
        "Zašto sh?", """
        <h1 style="font-size:92px">Domene ne poznaju š<span class="amber">.</span></h1>
        <p class="sub"><strong>Mi ga vraćamo.</strong> S krovom nad slovom i svjetlom koje uvijek gori. Štimung je ono što ostane kad tehnologiju prestaneš primjećivati.</p>
        """, dots(3, 2)),

    # ---- 03: usluge (carousel 4) ----
    "03-usluge-1": page(
        "Usluge · 1/4", """
        <div class="icon">◐</div>
        <h1 style="font-size:88px">Konzultacija<br>&amp; dizajn<span class="amber">.</span></h1>
        <p class="sub">Obilazak prostora, analiza navika i sustav po mjeri: protokoli, uređaji, budžet. <strong>Dobivaš plan, ne prodajni katalog.</strong></p>
        """, dots(4, 0)),
    "03-usluge-2": page(
        "Usluge · 2/4", """
        <div class="icon">⌂</div>
        <h1 style="font-size:88px">Pametni dom<span class="amber">.</span></h1>
        <p class="sub">Home Assistant, senzori, automatizacije i sučelje koje razumije cijela obitelj. <strong>Sve na jednom mjestu, sve tvoje.</strong></p>
        """, dots(4, 1)),
    "03-usluge-3": page(
        "Usluge · 3/4", """
        <div class="icon">✦</div>
        <h1 style="font-size:88px">LED ambijent<span class="amber">.</span></h1>
        <p class="sub">Trake, profili i scene koje mijenjaju prostor. Rasvjeta koja prati film, glazbu ili doba dana. <strong>Estetika koja se vidi.</strong></p>
        """, dots(4, 2)),
    "03-usluge-4": page(
        "Usluge · 4/4", """
        <div class="icon">↻</div>
        <h1 style="font-size:88px">Održavanje<span class="amber">.</span></h1>
        <p class="sub">Updateovi, backup, nadzor i dorade. <strong>Tvoj dom ostaje pametan i za pet godina</strong>, bez da razmišljaš o tome.</p>
        """, dots(4, 3)),

    # ---- 04: jedna automatizacija (serija, primjer #1) ----
    "04-automatizacija-1": page(
        "Jedna automatizacija", """
        <h1 style="font-size:96px">Rolete znaju kad<br>sunce zalazi<span class="amber">.</span></h1>
        <p class="sub" style="font-size:44px; margin-top:48px"><strong style="color:#ffb45c">Ti ne moraš.</strong></p>
        """),
}


def main():
    TMP.mkdir(parents=True, exist_ok=True)
    for name, html in POSTS.items():
        src = TMP / f"{name}.html"
        out = OUT / f"{name}.png"
        src.write_text(html)
        subprocess.run(
            [CHROME, "--headless", "--disable-gpu", f"--screenshot={out}",
             f"--window-size={W},{H}", "--hide-scrollbars",
             "--virtual-time-budget=3000", src.resolve().as_uri()],
            capture_output=True, check=True)
        print("  ✓", out.relative_to(ROOT))
    for f in TMP.iterdir():
        f.unlink()
    TMP.rmdir()
    print(f"\nGotovo → {OUT} ({len(POSTS)} vizuala, 1080x1350)")


if __name__ == "__main__":
    main()
