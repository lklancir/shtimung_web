/* ============================================================
   Hero shader — "Sequin Wave"
   Adaptirano iz Radiant projekta (github.com/pbakaus/radiant, MIT)
   Prigušena verzija: sporiji val, manji sparkle, pauza izvan viewporta.
   ============================================================ */

(function () {
  var canvas = document.getElementById("hero-shader");
  if (!canvas) return;

  var prefersReduced = window.matchMedia("(prefers-reduced-motion: reduce)").matches;

  var gl = canvas.getContext("webgl", { alpha: false, antialias: false, preserveDrawingBuffer: false });
  if (!gl) { canvas.remove(); return; } // graceful fallback na CSS pozadinu

  // ── Tuning (pritajen puls) ──
  var WAVE_SPEED = 0.4;
  var SPARKLE_INTENSITY = 0.55;

  var vertSrc = "attribute vec2 a_pos; void main() { gl_Position = vec4(a_pos, 0.0, 1.0); }";

  var fragSrc = [
    "precision highp float;",
    "uniform float u_time;",
    "uniform vec2 u_res;",
    "uniform float u_waveSpeed;",
    "uniform float u_sparkle;",
    "uniform vec2 u_mouse;",
    "#define TAU 6.28318530718",
    "#define SQRT3 1.7320508",
    "",
    "float hash21(vec2 p) {",
    "  p = fract(p * vec2(233.34, 851.73));",
    "  p += dot(p, p + 23.45);",
    "  return fract(p.x * p.y);",
    "}",
    "vec2 hash22(vec2 p) {",
    "  float n = hash21(p);",
    "  return vec2(n, hash21(p + n * 47.0));",
    "}",
    "",
    "// heksagonalni raspored 'šljokica'",
    "vec4 hexTile(vec2 p, float scale) {",
    "  p *= scale;",
    "  vec2 s = vec2(1.0, SQRT3);",
    "  vec2 halfS = s * 0.5;",
    "  vec2 aBase = floor(p / s);",
    "  vec2 aLocal = mod(p, s) - halfS;",
    "  vec2 pOff = p - halfS;",
    "  vec2 bBase = floor(pOff / s);",
    "  vec2 bLocal = mod(pOff, s) - halfS;",
    "  float pick = step(dot(aLocal, aLocal), dot(bLocal, bLocal));",
    "  vec2 localCoord = mix(bLocal, aLocal, pick);",
    "  vec2 cellId = mix(bBase + vec2(0.5), aBase, pick);",
    "  return vec4(localCoord, cellId);",
    "}",
    "",
    "// interferencija više valova — daje osjećaj pulsa",
    "float waveField(vec2 cellPos, float t) {",
    "  float w = 0.0;",
    "  w += sin(dot(cellPos, vec2(0.7, 0.5)) * 3.5 - t * 2.8) * 0.35;",
    "  w += sin(cellPos.x * 4.2 + t * 1.9) * 0.25;",
    "  float r1 = length(cellPos - vec2(-0.3, 0.2));",
    "  w += sin(r1 * 6.0 - t * 3.2) * 0.2 * smoothstep(1.2, 0.0, r1);",
    "  w += sin(dot(cellPos, vec2(-0.4, 0.8)) * 2.8 - t * 1.5) * 0.2;",
    "  float r2 = length(cellPos - vec2(0.4, -0.3));",
    "  w += sin(r2 * 5.0 - t * 2.4) * 0.15 * smoothstep(1.0, 0.0, r2);",
    "  return w;",
    "}",
    "",
    "float sequinSpecular(float tiltAngle, float tiltDir) {",
    "  float ct = cos(tiltAngle);",
    "  float st = sin(tiltAngle);",
    "  vec3 N = vec3(st * cos(tiltDir), st * sin(tiltDir), ct);",
    "  vec3 L = normalize(vec3(0.4, 0.6, 0.9));",
    "  vec3 V = vec3(0.0, 0.0, 1.0);",
    "  vec3 R = reflect(-L, N);",
    "  float spec = pow(max(dot(R, V), 0.0), 48.0);",
    "  float sheen = pow(max(dot(R, V), 0.0), 8.0) * 0.15;",
    "  return spec + sheen;",
    "}",
    "",
    "void main() {",
    "  vec2 uv = (gl_FragCoord.xy - u_res * 0.5) / min(u_res.x, u_res.y);",
    "  float t = u_time * u_waveSpeed;",
    "",
    "  float sequinScale = 38.0;",
    "  vec4 hex = hexTile(uv, sequinScale);",
    "  vec2 localPos = hex.xy;",
    "  vec2 cellId = hex.zw;",
    "",
    "  vec2 rnd = hash22(cellId);",
    "  float sizeVar = 0.85 + rnd.x * 0.3;",
    "  float baseTilt = (rnd.y - 0.5) * 0.15;",
    "  float reflVar = 0.7 + rnd.x * 0.3;",
    "  float phaseOff = rnd.y * TAU;",
    "",
    "  float discRadius = 0.42 * sizeVar;",
    "  float dist = length(localPos);",
    "  float disc = smoothstep(discRadius, discRadius - 0.06, dist);",
    "  float bevel = smoothstep(discRadius, discRadius - 0.04, dist)",
    "              - smoothstep(discRadius - 0.04, discRadius - 0.08, dist);",
    "",
    "  vec2 worldPos = cellId / sequinScale;",
    "  float wave = waveField(worldPos, t);",
    "  float shimmer = sin(t * 3.0 + phaseOff) * 0.04;",
    "  float tiltAngle = wave * 0.85 + baseTilt + shimmer;",
    "  float waveH = waveField(worldPos + vec2(0.01, 0.0), t);",
    "  float waveV = waveField(worldPos + vec2(0.0, 0.01), t);",
    "  float tiltDir = atan(waveV - wave, waveH - wave);",
    "",
    "  // miš kao dodatni izvor svjetla",
    "  float mouseSpec = 0.0;",
    "  if (u_mouse.x > 0.0) {",
    "    vec2 mUV = (u_mouse - u_res * 0.5) / min(u_res.x, u_res.y);",
    "    float mDist = length(worldPos - mUV);",
    "    float mInfluence = exp(-mDist * mDist * 6.0);",
    "    vec3 mLightDir = normalize(vec3(mUV.x - worldPos.x, mUV.y - worldPos.y, 0.5));",
    "    float ct = cos(tiltAngle);",
    "    float st2 = sin(tiltAngle);",
    "    vec3 mN = vec3(st2 * cos(tiltDir), st2 * sin(tiltDir), ct);",
    "    vec3 mR = reflect(-mLightDir, mN);",
    "    float mS = pow(max(dot(mR, vec3(0.0, 0.0, 1.0)), 0.0), 32.0);",
    "    mouseSpec = mS * mInfluence * 1.2;",
    "  }",
    "",
    "  float spec = sequinSpecular(tiltAngle, tiltDir) * reflVar * u_sparkle;",
    "  spec += mouseSpec * reflVar;",
    "",
    "  // paleta usklađena s temom stranice (bg #0a0c12, amber #ffb45c)",
    "  vec3 darkSequin = vec3(0.015, 0.014, 0.02);",
    "  vec3 copperMid = vec3(0.78, 0.58, 0.42);",
    "  vec3 amberFlash = vec3(1.0, 0.72, 0.38);",
    "  vec3 hotGold = vec3(1.0, 0.9, 0.68);",
    "",
    "  float facing = clamp(cos(tiltAngle) * 0.5 + 0.5, 0.0, 1.0);",
    "  vec3 ambient = mix(darkSequin, vec3(0.045, 0.038, 0.035), facing * 0.6);",
    "  vec3 sequinColor = ambient;",
    "  sequinColor += copperMid * pow(facing, 3.0) * 0.16 * reflVar;",
    "  sequinColor += copperMid * smoothstep(0.0, 0.3, spec) * 0.5;",
    "  sequinColor += amberFlash * smoothstep(0.3, 0.8, spec) * 0.8;",
    "  sequinColor += hotGold * smoothstep(0.7, 1.0, spec) * 1.2;",
    "  sequinColor += copperMid * bevel * facing * 0.25;",
    "",
    "  // pozadina između šljokica = boja stranice",
    "  vec3 bgColor = vec3(0.039, 0.047, 0.07);",
    "  vec3 col = mix(bgColor, sequinColor, disc);",
    "",
    "  vec2 uvSafe = uv + vec2(0.0001);",
    "  col *= 0.85 + 0.15 * dot(normalize(uvSafe), vec2(0.4, 0.6));",
    "  float vig = 1.0 - smoothstep(0.4, 1.3, length(uv));",
    "  col *= 0.6 + 0.4 * vig;",
    "  col = pow(max(col, vec3(0.0)), vec3(0.93, 0.97, 1.04));",
    "",
    "  gl_FragColor = vec4(clamp(col, 0.0, 1.0), 1.0);",
    "}",
  ].join("\n");

  function compile(type, src) {
    var s = gl.createShader(type);
    gl.shaderSource(s, src);
    gl.compileShader(s);
    if (!gl.getShaderParameter(s, gl.COMPILE_STATUS)) {
      console.error("Shader compile error:", gl.getShaderInfoLog(s));
    }
    return s;
  }

  var prog = gl.createProgram();
  gl.attachShader(prog, compile(gl.VERTEX_SHADER, vertSrc));
  gl.attachShader(prog, compile(gl.FRAGMENT_SHADER, fragSrc));
  gl.linkProgram(prog);
  if (!gl.getProgramParameter(prog, gl.LINK_STATUS)) {
    console.error("Program link error:", gl.getProgramInfoLog(prog));
    canvas.remove();
    return;
  }
  gl.useProgram(prog);

  var buf = gl.createBuffer();
  gl.bindBuffer(gl.ARRAY_BUFFER, buf);
  gl.bufferData(gl.ARRAY_BUFFER, new Float32Array([-1, -1, 3, -1, -1, 3]), gl.STATIC_DRAW);
  var aPos = gl.getAttribLocation(prog, "a_pos");
  gl.enableVertexAttribArray(aPos);
  gl.vertexAttribPointer(aPos, 2, gl.FLOAT, false, 0, 0);

  var uTime = gl.getUniformLocation(prog, "u_time");
  var uRes = gl.getUniformLocation(prog, "u_res");
  var uWaveSpeed = gl.getUniformLocation(prog, "u_waveSpeed");
  var uSparkle = gl.getUniformLocation(prog, "u_sparkle");
  var uMouse = gl.getUniformLocation(prog, "u_mouse");

  var dpr = Math.min(window.devicePixelRatio || 1, 2);
  var mouseX = -1.0, mouseY = -1.0;

  // canvas je pointer-events:none — pratimo miš na heroju
  var hero = canvas.closest(".hero") || canvas.parentElement;
  hero.addEventListener("mousemove", function (e) {
    var rect = canvas.getBoundingClientRect();
    mouseX = (e.clientX - rect.left) * dpr;
    mouseY = (rect.height - (e.clientY - rect.top)) * dpr;
  });
  hero.addEventListener("mouseleave", function () {
    mouseX = -1.0; mouseY = -1.0;
  });

  var needsResize = true;
  function resize() {
    needsResize = false;
    var w = Math.round(canvas.clientWidth * dpr);
    var h = Math.round(canvas.clientHeight * dpr);
    if (canvas.width !== w || canvas.height !== h) {
      canvas.width = w;
      canvas.height = h;
      gl.viewport(0, 0, w, h);
    }
    gl.uniform2f(uRes, canvas.width, canvas.height);
  }
  window.addEventListener("resize", function () { needsResize = true; });

  // renderiraj samo dok je hero u viewportu
  var visible = true;
  new IntersectionObserver(function (entries) {
    visible = entries[0].isIntersecting;
  }).observe(hero);

  function render(now) {
    requestAnimationFrame(render);
    if (!visible || document.hidden) return;
    if (needsResize) resize();

    // spori sinusni "dah" sparklea — puls efekt
    var breathe = 1.0 + 0.35 * Math.sin(now * 0.0004);

    gl.uniform1f(uTime, prefersReduced ? 0.0 : now * 0.001);
    gl.uniform1f(uWaveSpeed, WAVE_SPEED);
    gl.uniform1f(uSparkle, SPARKLE_INTENSITY * breathe);
    gl.uniform2f(uMouse, mouseX, mouseY);
    gl.drawArrays(gl.TRIANGLES, 0, 3);
  }

  resize();
  requestAnimationFrame(render);
})();
