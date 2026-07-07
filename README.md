# shtimung — one-pager

Web za smart home biznis (Zagreb). Vanilla HTML/CSS/JS, bez build stepa.

## Pokretanje

```bash
cd ~/Dev/personal/smarthome
python3 -m http.server 5173
# → http://localhost:5173
```

## Struktura

- `index.html` — sav sadržaj (hero, scroll scena, usluge, zašto, proces, kontakt)
- `css/style.css` — tema (dark, amber/cyan), scroll animacije, responsive
- `js/main.js` — reveal animacije + scroll scena logika
- `js/shader.js` — WebGL "sequin wave" pozadina heroja (adaptirano iz [Radiant](https://github.com/pbakaus/radiant), MIT); tuning: `WAVE_SPEED`, `SPARKLE_INTENSITY` u vrhu datoteke, opacity/maska u CSS-u (`#hero-shader`)

## Scroll scena

Centralni dio: SVG presjek stana koji se "pali" kroz 4 koraka dok korisnik scrolla.
Stanja po koraku definirana su deklarativno u `js/main.js` (`states` objekt) —
za novi korak/efekt dodaj element s id-em u SVG, referencu u `apartment` i stanje u `states`.

## Deploy (Plus Hosting, SSH)

```bash
cp scripts/deploy.env.example scripts/deploy.env  # prvi put: upiši SSH podatke iz cPanela
./scripts/deploy.sh        # dry-run
./scripts/deploy.sh --go   # deploy na shtimung.hr
```

## TODO / kasnije

- Brand: **shtimung** (odabrano 06.07.2026.) — registrirati shtimung.hr, shtimung.com i stimung.hr (redirect)
- Kontakt: trenutno mailto na privatni gmail — zamijeniti poslovnim mailom/formom
- Hosting: statika — može Cloudflare Pages / Netlify (besplatno)
- Vault kontekst: `~/Life/Personal/projects/smarthome/`
