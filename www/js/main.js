/* ============================================================
   shtimung — scroll logika
   1) reveal elemenata (IntersectionObserver)
   2) scroll scena: progress → korak → stanje "stana"
   ============================================================ */

// ---------- 1) Reveal on scroll ----------
const revealObserver = new IntersectionObserver(
  (entries) => {
    entries.forEach((entry) => {
      if (entry.isIntersecting) {
        entry.target.classList.add("visible");
        revealObserver.unobserve(entry.target);
      }
    });
  },
  { threshold: 0.15 }
);
document.querySelectorAll(".reveal").forEach((el) => revealObserver.observe(el));

// ---------- 2) Scroll scena ----------
const scene = document.getElementById("scena");
const progressBar = document.getElementById("progress-bar");
const steps = [...document.querySelectorAll(".step")];

// elementi stana
const el = (id) => document.getElementById(id);
const apartment = {
  glowHodnik: el("glow-hodnik"),
  spotH1: el("spot-hodnik-1"),
  spotH2: el("spot-hodnik-2"),
  senzor: el("senzor-hodnik"),
  nightpath: el("nightpath"),
  glowDnevni: el("glow-dnevni"),
  ledTraka: el("led-traka"),
  lampDnevni: el("lamp-dnevni"),
  glowKuhinja: el("glow-kuhinja"),
  ledKuhinja: el("led-kuhinja"),
  pendant1: el("pendant-1").querySelector(".bulb"),
  pendant2: el("pendant-2").querySelector(".bulb"),
  glowSpavaca: el("glow-spavaca"),
  lampSpavaca: el("lamp-spavaca"),
  roletaSpavaca: el("roleta-spavaca"),
  thermoValue: document.querySelector(".thermo-value"),
};

// stanje stana po koraku — deklarativno, lako mijenjati
const states = {
  0: {}, // sve ugašeno
  1: {
    // dolazak: hodnik + senzor + termostat
    on: ["glowHodnik", "spotH1", "spotH2"],
    sensor: true,
    thermo: "22.5°",
  },
  2: {
    // ambijent: dnevni boravak
    on: ["glowHodnik", "spotH1", "spotH2", "glowDnevni", "ledTraka", "lampDnevni"],
    tv: true,
    thermo: "22.5°",
  },
  3: {
    // dom pazi na sebe: kuhinja + rolete
    on: ["glowDnevni", "ledTraka", "lampDnevni", "glowKuhinja", "ledKuhinja", "pendant1", "pendant2"],
    tv: true,
    rolete: true,
    thermo: "22.5°",
  },
  4: {
    // laku noć: sve off, spavaća soft + noćna staza
    on: ["glowSpavaca", "lampSpavaca"],
    night: true,
    rolete: true,
    thermo: "19.0°",
  },
};

const allLights = [
  "glowHodnik", "spotH1", "spotH2",
  "glowDnevni", "ledTraka", "lampDnevni",
  "glowKuhinja", "ledKuhinja", "pendant1", "pendant2",
  "glowSpavaca", "lampSpavaca",
];

let currentStep = -1;

function applyStep(step) {
  if (step === currentStep) return;
  currentStep = step;

  const state = states[step] || {};
  const on = new Set(state.on || []);

  scene.dataset.step = step;

  allLights.forEach((key) => {
    apartment[key].classList.toggle("on", on.has(key));
  });

  apartment.senzor.classList.toggle("active", !!state.sensor);
  apartment.nightpath.classList.toggle("on", !!state.night);
  apartment.roletaSpavaca.classList.toggle("down", !!state.rolete);
  scene.classList.toggle("tv-on", !!state.tv);
  scene.classList.toggle("thermo-on", !!state.thermo);
  if (state.thermo) apartment.thermoValue.textContent = state.thermo;

  steps.forEach((s, i) => s.classList.toggle("active", i === step - 1));
}

// nav: wordmark → logo nakon što se hero odscrolla
const nav = document.querySelector(".nav");

function onScroll() {
  nav.classList.toggle("scrolled", window.scrollY > window.innerHeight * 0.55);

  const rect = scene.getBoundingClientRect();
  const total = scene.offsetHeight - window.innerHeight;
  // progress 0..1 kroz scenu
  const progress = Math.min(1, Math.max(0, -rect.top / total));

  progressBar.style.height = `${progress * 100}%`;

  // 4 koraka; malo "uvoda" prije prvog paljenja
  const step = progress < 0.04 ? 0 : Math.min(4, Math.floor(progress * 4) + 1);
  applyStep(step);
}

let ticking = false;
window.addEventListener(
  "scroll",
  () => {
    if (!ticking) {
      requestAnimationFrame(() => {
        onScroll();
        ticking = false;
      });
      ticking = true;
    }
  },
  { passive: true }
);
onScroll();

// klik na korak → scrollaj scenu na taj dio
steps.forEach((stepEl) => {
  stepEl.addEventListener("click", () => {
    const target = parseInt(stepEl.dataset.goto, 10);
    const total = scene.offsetHeight - window.innerHeight;
    // sredina segmenta koraka
    const progress = (target - 0.5) / 4;
    const top = scene.offsetTop + progress * total;
    window.scrollTo({ top, behavior: "smooth" });
  });
});
