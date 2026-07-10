/* ============================================================
   naštimaj — interaktivni konfigurator pametnog doma
   1) konfiguracija modula i cijena (placeholderi, lako se mijenja)
   2) izometrijska scena: render-once SVG, poslije samo klase
   3) stanje odabira → panel, brojač, sažetak, forma
   ============================================================ */

// ---------- 1) Konfiguracija ----------
const MODULI = {
  rasvjeta: {
    naziv: "Pametna rasvjeta",
    opis: "Scene, automatsko paljenje, sve iz jedne appice",
    min: 150, max: 350,
  },
  led: {
    naziv: "LED ambijent",
    opis: "Trake i profili, skriveno svjetlo koje mijenja prostor",
    min: 150, max: 300,
  },
  rolete: {
    naziv: "Pametne rolete",
    opis: "Prate sunce i tvoje navike, bez poteznog kaiša",
    min: 150, max: 400,
  },
  grijanje: {
    naziv: "Grijanje i hlađenje",
    opis: "Prava temperatura po sobi, ne po stanu",
    min: 100, max: 250,
  },
};

const DOM_MODULI = {
  osnova: {
    naziv: "Osnova sustava",
    opis: "Home Assistant server i mreža, temelj svega. Tvoj sustav, bez najamnine.",
    min: 400, max: 700, uvijek: true,
  },
  sigurnost: {
    naziv: "Sigurnost",
    opis: "Senzori vrata i prozora, dim, poplava. Dom koji pazi i kad te nema.",
    min: 200, max: 600,
  },
  multimedija: {
    naziv: "Multimedija",
    opis: "TV i glazba u scenama: jedan tap za filmsku večer",
    min: 100, max: 300,
  },
};

const SOBE = [
  { id: "hodnik", naziv: "Hodnik", moduli: ["rasvjeta", "led"] },
  { id: "dnevni", naziv: "Dnevni boravak", moduli: ["rasvjeta", "led", "rolete", "grijanje"] },
  { id: "kuhinja", naziv: "Kuhinja", moduli: ["rasvjeta", "led", "grijanje"] },
  { id: "spavaca", naziv: "Spavaća soba", moduli: ["rasvjeta", "led", "rolete", "grijanje"] },
];

// hodnik ima svoje formulacije (senzor na ulazu, noćna staza)
const OPIS_OVERRIDE = {
  "hodnik:rasvjeta": "Senzor te prepozna, svjetlo se pali samo",
  "hodnik:led": "Diskretna noćna staza do kupaonice",
  "spavaca:led": "Toplo svjetlo ispod kreveta, savršeno za noć",
};

// ---------- 2) Stanje ----------
const odabir = {
  hodnik: new Set(),
  dnevni: new Set(),
  kuhinja: new Set(),
  spavaca: new Set(),
  dom: new Set(["osnova"]),
};
let aktivna = null; // trenutno otvoren prostor u panelu
let zelja = "mail"; // mail | showroom
let hintPrikazan = true;

// vizualni elementi po ključu "soba:modul" → [{el, cls}]
const viz = {};
const reg = (kljuc, el, cls = "on") => (viz[kljuc] ||= []).push({ el, cls });

// ============================================================
// IZOMETRIJSKA SCENA
// ============================================================
const NS = "http://www.w3.org/2000/svg";
const svg = document.getElementById("iso-scena");

const COS = 0.866, SIN = 0.5, OX = 485, OY = 175;
const P = (x, y, z = 0) => [(x - y) * COS + OX, (x + y) * SIN - z + OY];
const pts = (lista) => lista.map(([a, b]) => `${a.toFixed(1)},${b.toFixed(1)}`).join(" ");

function el(tag, attrs = {}, parent = svg) {
  const n = document.createElementNS(NS, tag);
  for (const [k, v] of Object.entries(attrs)) n.setAttribute(k, v);
  parent.appendChild(n);
  return n;
}

const poly = (tocke, attrs = {}, parent = svg) =>
  el("polygon", { points: pts(tocke), ...attrs }, parent);

// vodoravna ploha na visini z
const ploha = (x, y, w, d, z, attrs, parent) =>
  poly([P(x, y, z), P(x + w, y, z), P(x + w, y + d, z), P(x, y + d, z)], attrs, parent);

// kutija: top + desna (x+w) + lijeva (y+d) vidljiva ploha
function box(x, y, w, d, h, cls = "", z0 = 0, parent = svg) {
  const g = el("g", { class: `ibox ${cls}`.trim() }, parent);
  poly([P(x, y + d, z0 + h), P(x, y + d, z0), P(x + w, y + d, z0), P(x + w, y + d, z0 + h)], { class: "f-left" }, g);
  poly([P(x + w, y, z0 + h), P(x + w, y, z0), P(x + w, y + d, z0), P(x + w, y + d, z0 + h)], { class: "f-right" }, g);
  ploha(x, y, w, d, z0 + h, { class: "f-top" }, g);
  return g;
}

// ploha na zidu okrenutom prema +x (npr. zapadni zid, ravnina x = konst)
const zidX = (x, y1, y2, z1, z2, attrs, parent) =>
  poly([P(x, y1, z2), P(x, y2, z2), P(x, y2, z1), P(x, y1, z1)], attrs, parent);

// ploha na zidu okrenutom prema +y (sjeverni zid, ravnina y = konst)
const zidY = (y, x1, x2, z1, z2, attrs, parent) =>
  poly([P(x1, y, z2), P(x2, y, z2), P(x2, y, z1), P(x1, y, z1)], attrs, parent);

const linija = (a, b, attrs, parent) =>
  el("line", { x1: a[0].toFixed(1), y1: a[1].toFixed(1), x2: b[0].toFixed(1), y2: b[1].toFixed(1), ...attrs }, parent);

function zarulja(x, y, z, r, parent) {
  return el("circle", { cx: P(x, y, z)[0].toFixed(1), cy: P(x, y, z)[1].toFixed(1), r, class: "bulb" }, parent);
}

function glowElipsa(x, y, rx, parent) {
  const [cx, cy] = P(x, y, 0);
  return el("ellipse", { cx: cx.toFixed(1), cy: cy.toFixed(1), rx, ry: (rx * 0.48).toFixed(0), fill: "url(#warmGlow)", class: "glow" }, parent);
}

// viseća/stolna lampa: kabel + sjenilo + žarulja (sve u screen prostoru od točke)
function lampa(x, y, zVrh, zSjenilo, sirina, parent) {
  const vrh = P(x, y, zVrh);
  const s = P(x, y, zSjenilo);
  linija(vrh, s, { class: "iso-line" }, parent);
  poly(
    [[s[0] - sirina, s[1]], [s[0] + sirina, s[1]], [s[0] + sirina * 0.55, s[1] + 12], [s[0] - sirina * 0.55, s[1] + 12]],
    { class: "iso-shade" }, parent
  );
  return el("circle", { cx: s[0].toFixed(1), cy: (s[1] + 16).toFixed(1), r: sirina * 0.62, class: "bulb" }, parent);
}

function nacrtajScenu() {
  // defs: gradijenti iz postojeće scene
  const defs = el("defs");
  const warm = el("radialGradient", { id: "warmGlow", cx: "50%", cy: "50%", r: "50%" }, defs);
  el("stop", { offset: "0%", "stop-color": "#ffb45c", "stop-opacity": "0.8" }, warm);
  el("stop", { offset: "100%", "stop-color": "#ffb45c", "stop-opacity": "0" }, warm);
  const ledG = el("linearGradient", { id: "ledStrip", x1: "0%", y1: "0%", x2: "100%", y2: "0%" }, defs);
  [["0%", "#ff5c8a"], ["25%", "#ffb45c"], ["50%", "#5cffb0"], ["75%", "#5cd6ff"], ["100%", "#ff5c8a"]]
    .forEach(([o, c]) => el("stop", { offset: o, "stop-color": c }, ledG));
  const tvG = el("linearGradient", { id: "tvGlow", x1: "0%", y1: "0%", x2: "0%", y2: "100%" }, defs);
  el("stop", { offset: "0%", "stop-color": "#5c8aff", "stop-opacity": "0.5" }, tvG);
  el("stop", { offset: "100%", "stop-color": "#5c8aff", "stop-opacity": "0" }, tvG);

  const H = 112; // visina stražnjih zidova

  // pod cijelog stana
  ploha(20, 20, 720, 520, 0, { class: "iso-pod" });

  // stražnji zidovi (sjever + zapad)
  const zidovi = el("g", { class: "iso-zid" });
  box(6, 6, 734, 14, H, "", 0, zidovi); // sjeverni
  box(6, 6, 14, 534, H, "", 0, zidovi); // zapadni

  // sobe, redom od najdalje prema bližima (painter's algorithm)
  const gSpavaca = sobaGrupa("spavaca");
  crtajSpavacu(gSpavaca);

  pregrada(455, 20, 10, 260); // spavaća | hodnik

  const gHodnik = sobaGrupa("hodnik");
  crtajHodnik(gHodnik);

  pregrada(20, 275, 380, 10); // gornje | donje sobe, s prolazom
  pregrada(470, 275, 270, 10);

  const gDnevni = sobaGrupa("dnevni");
  crtajDnevni(gDnevni);

  pregrada(485, 340, 10, 200); // dnevni | kuhinja

  const gKuhinja = sobaGrupa("kuhinja");
  crtajKuhinju(gKuhinja);

  // niski prednji rub (presjek zidova)
  const rub = el("g", { class: "iso-zid niski" });
  box(740, 20, 12, 532, 12, "", 0, rub); // istočni
  box(20, 540, 732, 12, 12, "", 0, rub); // južni

  // hint točka na ulazu
  const [hx, hy] = P(600, 150, 2);
  el("circle", { cx: hx.toFixed(1), cy: hy.toFixed(1), r: 5, class: "hint-dot", id: "hint-dot" });
}

function pregrada(x, y, w, d) {
  box(x, y, w, d, 30, "", 0, el("g", { class: "iso-zid niski" }));
}

function sobaGrupa(id) {
  const g = el("g", { class: "room-g", id: `g-${id}`, "data-soba": id });
  g.addEventListener("click", () => odaberi(id));
  // pod ide odmah, prije svega u sobi, da ništa ne prekrije
  const t = TLOCRT[id];
  ploha(t.x, t.y, t.w, t.d, 0.5, { class: "iso-floor", "data-soba": id }, g);
  return g;
}

// granice soba u tlocrtu (za pod i labelu)
const TLOCRT = {
  spavaca: { x: 24, y: 24, w: 428, d: 248, label: [240, 148], temp: "19.0°" },
  hodnik: { x: 464, y: 24, w: 272, d: 248, label: [600, 150] },
  dnevni: { x: 24, y: 284, w: 458, d: 252, label: [245, 415], temp: "22.5°" },
  kuhinja: { x: 494, y: 284, w: 242, d: 252, label: [618, 415], temp: "21.0°" },
};

function labelaIPill(id, parent) {
  const t = TLOCRT[id];
  const [lx, ly] = P(t.label[0], t.label[1], 150);
  const label = el("text", {
    x: lx.toFixed(1), y: ly.toFixed(1),
    class: "iso-label", "text-anchor": "middle", "data-soba": id,
  }, parent);
  label.textContent = SOBE.find((s) => s.id === id).naziv.toUpperCase();
  label.dataset.osnovni = label.textContent;

  if (t.temp) {
    const pill = el("g", { class: "thermo-pill" }, parent);
    el("rect", { x: (lx - 31).toFixed(1), y: (ly + 12).toFixed(1), width: 62, height: 26, rx: 13 }, pill);
    const txt = el("text", { x: lx.toFixed(1), y: (ly + 30).toFixed(1), "text-anchor": "middle" }, pill);
    txt.textContent = t.temp;
    reg(`${id}:grijanje`, pill);
  }
  return label;
}

// ---------- spavaća (gore lijevo) ----------
function crtajSpavacu(g) {
  reg("spavaca:rasvjeta", glowElipsa(220, 150, 150, g));

  // prozor na zapadnom zidu + roleta
  zidX(20, 96, 204, 36, 92, { class: "iso-window" }, g);
  linija(P(20, 150, 36), P(20, 150, 92), { class: "iso-window-bar" }, g);
  reg("spavaca:rolete", zidX(20, 96, 204, 36, 92, { class: "roleta" }, g), "down");
  const wd = el("circle", { cx: P(20, 150, 98)[0].toFixed(1), cy: P(20, 150, 98)[1].toFixed(1), r: 3, class: "sec-dot" }, g);
  reg("dom:sigurnost", wd);

  // LED ispod kreveta (crta se prije kreveta da viri ispod ruba)
  reg("spavaca:led", poly([P(228, 64, 1.5), P(238, 64, 1.5), P(238, 196, 1.5), P(228, 196, 1.5)], { fill: "url(#ledStrip)", class: "led-strip" }, g));
  reg("spavaca:led", poly([P(56, 192, 1.5), P(228, 192, 1.5), P(228, 202, 1.5), P(56, 202, 1.5)], { fill: "url(#ledStrip)", class: "led-strip" }, g));

  // krevet: baza + poplun + jastuk + uzglavlje
  box(46, 60, 10, 136, 52, "dark", 0, g);
  box(56, 64, 172, 128, 26, "", 0, g);
  box(60, 68, 164, 120, 10, "light", 26, g);
  box(64, 76, 26, 104, 7, "light", 36, g);

  // noćni ormarić + lampa
  box(56, 208, 42, 44, 32, "", 0, g);
  linija(P(77, 230, 32), P(77, 230, 58), { class: "iso-line" }, g);
  const s = P(77, 230, 74);
  poly([[s[0] - 9, s[1]], [s[0] + 9, s[1]], [s[0] + 5, s[1] + 11], [s[0] - 5, s[1] + 11]], { class: "iso-shade" }, g);
  reg("spavaca:rasvjeta", el("circle", { cx: s[0].toFixed(1), cy: (s[1] + 15).toFixed(1), r: 6, class: "bulb" }, g));

  labelaIPill("spavaca", g);
}

// ---------- hodnik (gore desno) ----------
function crtajHodnik(g) {
  reg("hodnik:rasvjeta", glowElipsa(595, 150, 115, g));

  // ulazna vrata na sjevernom zidu + kvaka
  zidY(20, 606, 672, 0, 98, { class: "iso-door" }, g);
  el("circle", { cx: P(612, 20, 48)[0].toFixed(1), cy: P(612, 20, 48)[1].toFixed(1), r: 3, fill: "#4a5268" }, g);

  // lokot na vratima (sigurnost)
  const lk = el("g", { class: "sec-lock" }, g);
  const q = P(639, 20, 76);
  el("rect", { x: (q[0] - 6).toFixed(1), y: q[1].toFixed(1), width: 12, height: 9, rx: 2 }, lk);
  el("path", { d: `M ${(q[0] - 3.5).toFixed(1)} ${q[1].toFixed(1)} v -4 a 3.5 3.5 0 0 1 7 0 v 4` }, lk);
  reg("dom:sigurnost", lk);

  // senzor pokreta iznad vrata (isti jezik kao scroll-scena)
  const sz = el("g", { id: "senzor-hodnik" }, g);
  const sp = P(585, 20, 100);
  el("circle", { cx: sp[0].toFixed(1), cy: sp[1].toFixed(1), r: 5, class: "sensor" }, sz);
  el("circle", { cx: sp[0].toFixed(1), cy: sp[1].toFixed(1), r: 12, class: "sensor-ring" }, sz);
  el("circle", { cx: sp[0].toFixed(1), cy: sp[1].toFixed(1), r: 20, class: "sensor-ring r2" }, sz);
  reg("hodnik:rasvjeta", sz, "active");

  // sec-dot na vratima
  const dd = el("circle", { cx: P(668, 20, 104)[0].toFixed(1), cy: P(668, 20, 104)[1].toFixed(1), r: 3, class: "sec-dot" }, g);
  reg("dom:sigurnost", dd);

  // noćna staza uz prolaz prema dnevnom
  reg("hodnik:led", poly([P(470, 262, 1), P(730, 262, 1), P(730, 271, 1), P(470, 271, 1)], { class: "night-strip" }, g));

  // komoda + hub (osnova sustava, uvijek diše)
  box(482, 32, 104, 42, 34, "", 0, g);
  box(500, 40, 26, 24, 11, "dark", 34, g);
  const hb = P(526, 58, 39);
  el("circle", { cx: hb[0].toFixed(1), cy: hb[1].toFixed(1), r: 2.6, class: "hub-dot" }, g);

  // stropni spotovi
  [560, 660].forEach((x) => {
    linija(P(x, 150, 148), P(x, 150, 128), { class: "iso-line" }, g);
    reg("hodnik:rasvjeta", zarulja(x, 150, 122, 6, g));
  });

  labelaIPill("hodnik", g);
}

// ---------- dnevni boravak (dolje lijevo) ----------
function crtajDnevni(g) {
  reg("dnevni:rasvjeta", glowElipsa(240, 420, 180, g));

  // prozor + roleta na gornjem dijelu zapadnog zida
  zidX(20, 300, 400, 36, 92, { class: "iso-window" }, g);
  linija(P(20, 350, 36), P(20, 350, 92), { class: "iso-window-bar" }, g);
  reg("dnevni:rolete", zidX(20, 300, 400, 36, 92, { class: "roleta" }, g), "down");
  const wd = el("circle", { cx: P(20, 350, 98)[0].toFixed(1), cy: P(20, 350, 98)[1].toFixed(1), r: 3, class: "sec-dot" }, g);
  reg("dom:sigurnost", wd);

  // ambijent iza TV-a (multimedija)
  reg("dom:multimedija", zidX(21, 408, 540, 32, 114, { fill: "url(#tvGlow)", class: "iso-tv-ambient" }, g));

  // TV komoda + LED traka + TV (prednji dio zida, dalje od prozora)
  box(34, 420, 34, 112, 40, "light", 0, g);
  reg("dnevni:led", poly([P(61, 420, 40.5), P(68, 420, 40.5), P(68, 532, 40.5), P(61, 532, 40.5)], { fill: "url(#ledStrip)", class: "led-strip" }, g));
  box(42, 430, 8, 92, 64, "dark", 44, g);
  reg("dom:multimedija", zidX(50.5, 434, 518, 50, 104, { class: "iso-tv-screen" }, g));

  // sofa: baza + naslon + rukohvati, stolić
  box(304, 370, 72, 136, 32, "", 0, g);
  box(376, 370, 22, 136, 56, "", 0, g);
  box(300, 354, 84, 18, 44, "", 0, g);
  box(300, 504, 84, 18, 44, "", 0, g);
  box(190, 420, 54, 60, 20, "dark", 0, g);

  // podna lampa u kutu kraj prozora
  linija(P(70, 310, 0), P(70, 310, 60), { class: "iso-line" }, g);
  const s = P(70, 310, 78);
  poly([[s[0] - 10, s[1]], [s[0] + 10, s[1]], [s[0] + 6, s[1] + 12], [s[0] - 6, s[1] + 12]], { class: "iso-shade" }, g);
  reg("dnevni:rasvjeta", el("circle", { cx: s[0].toFixed(1), cy: (s[1] + 16).toFixed(1), r: 6.5, class: "bulb" }, g));

  labelaIPill("dnevni", g);
}

// ---------- kuhinja (dolje desno) ----------
function crtajKuhinju(g) {
  reg("kuhinja:rasvjeta", glowElipsa(610, 415, 130, g));

  // radna ploha uz pregradu, LED ispod ruba ploče
  box(506, 290, 224, 62, 42, "", 0, g);
  box(504, 288, 228, 66, 6, "light", 42, g);
  reg("kuhinja:led", poly([P(506, 353, 42), P(730, 353, 42), P(730, 353, 37), P(506, 353, 37)], { fill: "url(#ledStrip)", class: "led-strip" }, g));

  // otok, također s LED-om pod pločom
  box(556, 412, 120, 52, 42, "", 0, g);
  box(554, 410, 124, 56, 5, "light", 42, g);
  reg("kuhinja:led", poly([P(556, 465, 42), P(676, 465, 42), P(676, 465, 37), P(556, 465, 37)], { fill: "url(#ledStrip)", class: "led-strip" }, g));

  // visilice nad otokom
  [586, 646].forEach((x) => {
    reg("kuhinja:rasvjeta", lampa(x, 438, 170, 132, 11, g));
  });

  labelaIPill("kuhinja", g);
}

// ============================================================
// 3) UI: panel, brojač, sažetak
// ============================================================
const $ = (id) => document.getElementById(id);
const fmt = (n) => n.toLocaleString("hr-HR");
const range = (min, max) => `${fmt(min)} - ${fmt(max)} €`;

function cijenaModula(soba, mod) {
  return soba === "dom" ? DOM_MODULI[mod] : MODULI[mod];
}

function ukupno() {
  let min = 0, max = 0;
  for (const soba of [...SOBE.map((s) => s.id), "dom"]) {
    for (const mod of odabir[soba]) {
      const c = cijenaModula(soba, mod);
      min += c.min; max += c.max;
    }
  }
  return [min, max];
}

function brojOdabranih(id) {
  // osnova je uvijek uključena pa je ne brojimo kao korisnikov odabir
  return id === "dom" ? odabir.dom.size - 1 : odabir[id].size;
}

function imaOdabira() {
  return [...SOBE.map((s) => s.id), "dom"].some((id) => brojOdabranih(id) > 0);
}

// ---------- chips ----------
function renderChips() {
  const c = $("nsh-chips");
  c.innerHTML = "";
  const stavke = [...SOBE, { id: "dom", naziv: "Cijeli dom" }];
  for (const s of stavke) {
    const b = document.createElement("button");
    b.type = "button";
    b.className = "nsh-chip" + (aktivna === s.id ? " active" : "");
    b.textContent = s.naziv;
    const n = brojOdabranih(s.id);
    if (n > 0) {
      const bb = document.createElement("b");
      bb.textContent = n;
      b.appendChild(bb);
    }
    b.addEventListener("click", () => odaberi(s.id));
    c.appendChild(b);
  }
}

// ---------- panel s modulima ----------
function renderModuli() {
  const wrap = $("nsh-moduli");
  wrap.innerHTML = "";

  if (!aktivna) {
    const p = document.createElement("p");
    p.className = "nsh-moduli-uvod";
    p.textContent = "Klikni sobu u stanu (ili odaberi prostor gore) pa upali ono što te zanima. Stan reagira odmah.";
    wrap.appendChild(p);
    return;
  }

  const moduli = aktivna === "dom"
    ? Object.keys(DOM_MODULI)
    : SOBE.find((s) => s.id === aktivna).moduli;

  for (const mod of moduli) {
    const c = cijenaModula(aktivna, mod);
    const ukljucen = odabir[aktivna].has(mod);
    const row = document.createElement("div");
    row.className = "nsh-mod" + (ukljucen ? " ukljucen" : "") + (c.uvijek ? " zakljucan" : "");

    const info = document.createElement("div");
    info.className = "nsh-mod-info";
    const h = document.createElement("h4");
    h.textContent = c.naziv;
    const p = document.createElement("p");
    p.textContent = OPIS_OVERRIDE[`${aktivna}:${mod}`] || c.opis;
    info.append(h, p);
    if (c.uvijek) {
      const u = document.createElement("span");
      u.className = "nsh-mod-uvijek";
      u.textContent = "uvijek uključeno";
      info.appendChild(u);
    }

    const cijena = document.createElement("span");
    cijena.className = "nsh-mod-cijena";
    cijena.textContent = range(c.min, c.max);

    const sw = document.createElement("span");
    sw.className = "nsh-switch";

    row.append(info, cijena, sw);
    if (!c.uvijek) {
      row.addEventListener("click", () => toggleModul(aktivna, mod));
    }
    wrap.appendChild(row);
  }
}

// ---------- brojač ----------
function renderBrojac() {
  const [min, max] = ukupno();
  const txt = range(min, max);
  for (const id of ["nsh-total-val", "nsh-mbar-val", "sazetak-total"]) {
    const n = $(id);
    if (n.textContent !== txt) {
      n.textContent = txt;
      if (id === "nsh-total-val") {
        n.classList.remove("pop");
        void n.offsetWidth;
        n.classList.add("pop");
      }
    }
  }
}

// ---------- scena: klase po stanju ----------
function renderScena() {
  for (const [kljuc, elementi] of Object.entries(viz)) {
    const [soba, mod] = kljuc.split(":");
    const on = odabir[soba].has(mod);
    for (const { el: e, cls } of elementi) e.classList.toggle(cls, on);
  }
  // fokus sobe + dim ostalih + labela s brojem
  for (const s of SOBE) {
    const g = $(`g-${s.id}`);
    g.classList.toggle("odabrana", aktivna === s.id);
    g.classList.toggle("dim", aktivna !== null && aktivna !== "dom" && aktivna !== s.id);
    const label = g.querySelector(".iso-label");
    const n = brojOdabranih(s.id);
    label.textContent = n > 0 ? `${label.dataset.osnovni} · ${n}` : label.dataset.osnovni;
  }
}

// ---------- sažetak ----------
function renderSazetak() {
  const ima = imaOdabira();
  $("sazetak-prazno").hidden = ima;
  $("sazetak-sadrzaj").hidden = !ima;
  if (!ima) return;

  const lista = $("sazetak-lista");
  lista.innerHTML = "";
  const stavke = [...SOBE, { id: "dom", naziv: "Cijeli dom" }];
  for (const s of stavke) {
    const moduli = [...odabir[s.id]];
    if (s.id !== "dom" && moduli.length === 0) continue;
    const blok = document.createElement("div");
    blok.className = "nsh-sz-blok";
    const h = document.createElement("h4");
    h.textContent = s.naziv;
    blok.appendChild(h);
    for (const mod of moduli) {
      const c = cijenaModula(s.id, mod);
      const red = document.createElement("div");
      red.className = "nsh-sz-red";
      const a = document.createElement("span");
      a.textContent = c.naziv;
      const b = document.createElement("span");
      b.textContent = range(c.min, c.max);
      red.append(a, b);
      blok.appendChild(red);
    }
    lista.appendChild(blok);
  }
}

function renderAll() {
  renderChips();
  renderModuli();
  renderBrojac();
  renderScena();
  renderSazetak();
}

// ---------- akcije ----------
function odaberi(id) {
  aktivna = aktivna === id ? null : id;
  if (hintPrikazan) {
    hintPrikazan = false;
    $("nsh-hint").classList.add("skriven");
    $("hint-dot")?.remove();
  }
  renderAll();
  // na mobitelu panel je ispod scene, dovuci ga u kadar
  if (aktivna && window.matchMedia("(max-width: 980px)").matches) {
    document.querySelector(".nsh-panel").scrollIntoView({ behavior: "smooth", block: "nearest" });
  }
}

function toggleModul(soba, mod) {
  odabir[soba].has(mod) ? odabir[soba].delete(mod) : odabir[soba].add(mod);
  renderAll();
}

// ============================================================
// 4) Sažetak kao tekst (za mail) + forma
// ============================================================
function sazetakTekst() {
  const linije = [];
  const stavke = [...SOBE, { id: "dom", naziv: "Cijeli dom" }];
  for (const s of stavke) {
    const moduli = [...odabir[s.id]];
    if (moduli.length === 0) continue;
    let min = 0, max = 0;
    const imena = moduli.map((m) => {
      const c = cijenaModula(s.id, m);
      min += c.min; max += c.max;
      return c.naziv;
    });
    linije.push(`${s.naziv}: ${imena.join(", ")} (${range(min, max)})`);
  }
  const [min, max] = ukupno();
  linije.push("", `Okvirno ukupno: ${range(min, max)}`);
  return linije.join("\n");
}

function postaviFormu() {
  // izbor želje: mail ili showroom
  $("cta-izbor").addEventListener("click", (ev) => {
    const btn = ev.target.closest(".nsh-izbor");
    if (!btn) return;
    zelja = btn.dataset.zelja;
    document.querySelectorAll(".nsh-izbor").forEach((b) => b.classList.toggle("active", b === btn));
    $("nsh-submit").textContent = zelja === "showroom" ? "Dogovori termin u showroomu" : "Pošalji mi prijedlog";
  });

  $("nsh-forma").addEventListener("submit", async (ev) => {
    ev.preventDefault();
    const f = ev.target;
    const ime = f.ime.value.trim();
    const email = f.email.value.trim();
    if (!ime || !/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email)) {
      prikaziStatus("Upiši ime i ispravan mail pa probaj opet.", true);
      return;
    }

    const submit = $("nsh-submit");
    submit.disabled = true;
    submit.textContent = "Šaljem...";

    try {
      const res = await fetch("posalji.php", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          ime, email,
          telefon: f.telefon.value.trim(),
          web: f.web.value, // honeypot
          zelja,
          sazetak: sazetakTekst(),
        }),
      });
      const data = await res.json().catch(() => ({}));
      if (!res.ok || !data.ok) throw new Error(data.greska || "Slanje nije uspjelo.");

      f.hidden = true;
      $("cta-izbor").hidden = true;
      prikaziStatus(
        zelja === "showroom"
          ? "Poslano! Kopija tvog shtimunga stiže ti na mail, a mi se javljamo s terminom za showroom. Vidimo se."
          : "Poslano! Kopija tvog shtimunga stiže ti na mail, a mi se javljamo s konkretnim prijedlogom u roku dan-dva.",
        false
      );
    } catch (e) {
      const body = encodeURIComponent(`Bok,\n\nslažem svoj shtimung:\n\n${sazetakTekst()}\n\n${ime}`);
      prikaziStatus(
        `Nešto je zapelo pri slanju. Probaj opet za minutu, ili nam piši direktno: <a href="mailto:info@shtimung.hr?subject=nashtimaj%20upit&body=${body}">info@shtimung.hr</a>`,
        true
      );
      submit.disabled = false;
      submit.textContent = zelja === "showroom" ? "Dogovori termin u showroomu" : "Pošalji mi prijedlog";
    }
  });
}

function prikaziStatus(html, greska) {
  const s = $("nsh-status");
  s.hidden = false;
  s.classList.toggle("greska", greska);
  s.innerHTML = html;
}

// ============================================================
// 5) Parallax tilt + reveal
// ============================================================
function postaviTilt() {
  const fino = window.matchMedia("(pointer: fine)").matches;
  const mirno = window.matchMedia("(prefers-reduced-motion: reduce)").matches;
  if (!fino || mirno) return;
  const wrap = $("scene-wrap");
  const tilt = $("iso-tilt");
  wrap.addEventListener("mousemove", (ev) => {
    const r = wrap.getBoundingClientRect();
    const mx = (ev.clientX - r.left) / r.width - 0.5;
    const my = (ev.clientY - r.top) / r.height - 0.5;
    tilt.style.setProperty("--ry", `${(mx * 4).toFixed(2)}deg`);
    tilt.style.setProperty("--rx", `${(-my * 3).toFixed(2)}deg`);
  });
  wrap.addEventListener("mouseleave", () => {
    tilt.style.setProperty("--ry", "0deg");
    tilt.style.setProperty("--rx", "0deg");
  });
}

const revealObserver = new IntersectionObserver(
  (entries) => entries.forEach((e) => {
    if (e.isIntersecting) {
      e.target.classList.add("visible");
      revealObserver.unobserve(e.target);
    }
  }),
  { threshold: 0.15 }
);
document.querySelectorAll(".reveal").forEach((el) => revealObserver.observe(el));

// ---------- start ----------
nacrtajScenu();
postaviFormu();
postaviTilt();
renderAll();
