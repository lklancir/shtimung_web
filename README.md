# shtimung

Web, brand i content produkcija za shtimung (pametan dom po mjeri, Zagreb).
Live: **https://shtimung.hr** · GitHub: `lklancir/shtimung_web`

## Struktura

```
shtimung/
├── www/            ← WEB ROOT: 1:1 ono što je na serveru (public_html)
│   ├── index.html      one-pager (hero, scroll scena, usluge, kontakt)
│   ├── .htaccess       301 → https://shtimung.hr + cache statike
│   ├── css/ js/        tema, scroll scena, WebGL shader (js/shader.js)
│   ├── brand/          served brand asseti (favicons, og slika, logo)
│   │   └── _src/       fontovi za lokalne rendere (NE deploya se)
│   └── nashtimaj/      lead-gen konfigurator (HTML/JS + PHP mail endpoint)
├── social/         ← content produkcija (generirani vizuali, po kanalu)
│   ├── feed/ (1080x1350)  square/ (1080x1080)  facebook/  youtube/
├── docs/           ← interni dokumenti: brandbook.html, logo-lab.html
├── scripts/        ← build + deploy (jedina kopija skripti)
└── README.md
```

**Pravilo:** sve što posjetitelj može dobiti preko URL-a živi u `www/`. Sve ostalo
(masteri, generatori, dokumentacija) živi izvan i nikad se ne deploya.

## Deploy

```bash
python3 scripts/deploy-ftp.py         # dry-run
python3 scripts/deploy-ftp.py --go    # deploy www/ → public_html (FTPS)
```

Kredencijali: `scripts/deploy.env` (gitignoriran; predložak je `deploy.env.example`).
`nashtimaj/smtp-config.php` se preskače dok mu je lozinka prazna (ne gazi server).
Kad Plus Hosting uključi shell: `./scripts/deploy.sh --go` (rsync + --delete).

## Build skripte

```bash
python3 scripts/build-brand.py            # brand paket → www/brand/ (SVG+PNG+ICO)
python3 scripts/build-social.py           # postovi 01-04 → social/feed + square
python3 scripts/build-social-v2.py        # postovi 05-09 → social/feed + square
python3 scripts/build-facebook-cover.py   # FB cover → social/facebook
python3 scripts/build-youtube-banner.py   # YT banner → social/youtube
```

Sve rade isto: HTML template + lokalni fontovi (`www/brand/_src/`) → headless
Chrome → PNG. Novi social post = novi entry u POSTS dict + pokretanje skripte.

## Web — ključni dijelovi

- **Scroll scena**: SVG presjek stana koji se "pali" kroz 4 koraka; stanja su
  deklarativna u `www/js/main.js` (`states` objekt) — novi efekt = novi id u SVG-u,
  referenca u `apartment` i stanje u `states`
- **Hero shader**: `www/js/shader.js` (adaptirano iz [Radiant](https://github.com/pbakaus/radiant),
  MIT); tuning: `WAVE_SPEED`, `SPARKLE_INTENSITY` u vrhu datoteke, opacity/maska u CSS-u (`#hero-shader`)
- **Nav logo**: wordmark → V9 znak crossfade na scroll (`.nav.scrolled` u CSS-u)

## Lokalni pregled

```bash
python3 -m http.server 5173 -d www
# → http://localhost:5173  (docs: otvori docs/brandbook.html direktno u browseru)
```

## Kontekst

Vault: `~/Life/Personal/projects/smarthome/` (strategija, TODO, log).
Brand pravila: `docs/brandbook.html` (paleta, tipografija, glas i ton, logo pravila).
