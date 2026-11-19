/* Activate + Chimal · avatar-core.js
 *
 * Renderizador del avatar: un ASTRO del sistema solar (Sol, planetas, Luna, Plutón, asteroide) dibujado
 * en SVG por capas. Es la ÚNICA implementación de dibujo: la usan el creador (con vista previa y
 * transiciones) y el resto del sitio (menú, perfil, clasificación).
 *
 * Qué hay aquí:
 *   1. utilidades de color, azar determinista y formas orgánicas
 *   2. astro: forma, sombreado y texturas (bandas, cráteres, continentes, nubes...)
 *   3. anillos, lunas con órbita y atmósfera
 *   4. fondo espacial, acompañantes (cometa, satélite...) y carita
 *   5. composición del SVG:  AvatarCore.svg(cfg, opciones)  -> texto SVG
 *   6. controlador animado:  AvatarCore.crear(elemento, cfg) -> { set, vista }
 *   7. hidratación de los <span data-avatar> del sitio
 *
 * Para AGREGAR una opción (p. ej. otra textura): añádela a static/data/avatar_esquema.json y dibuja
 * su id en la tabla correspondiente (TEXTURAS, ANILLOS, CARAS, EXTRAS...).
 */
(function (G) {
  "use strict";

  const CX = 100, CY = 100;                              // centro del lienzo (200 × 200)
  const n = (v) => Math.round(v * 100) / 100;            // redondeo para acortar el SVG
  const clamp = (v, a, b) => Math.max(a, Math.min(b, v));
  const lerp = (a, b, t) => a + (b - a) * t;
  const TAU = Math.PI * 2;
  let contador = 0;                                      // ids únicos por avatar dibujado

  /* ───────────── 1. Utilidades ───────────── */
  const hex2rgb = (h) => [1, 3, 5].map((i) => parseInt(h.slice(i, i + 2), 16));
  const rgb2hex = (c) => "#" + c.map((v) => clamp(Math.round(v), 0, 255).toString(16).padStart(2, "0")).join("");
  const mix = (a, b, t) => { const x = hex2rgb(a), y = hex2rgb(b); return rgb2hex(x.map((v, i) => lerp(v, y[i], t))); };
  const claro = (c, t) => mix(c, "#ffffff", t);
  const oscuro = (c, t) => mix(c, "#0b0b1e", t);
  const luminosidad = (c) => { const [r, g, b] = hex2rgb(c); return 0.299 * r + 0.587 * g + 0.114 * b; };
  const texto = (t) => String(t).replace(/[&<>"']/g, "");

  /** Generador pseudoaleatorio determinista (los cráteres y las estrellas siempre salen en el mismo lugar). */
  function rng(semilla) {
    let a = semilla >>> 0;
    return function () {
      a = (a + 0x6D2B79F5) >>> 0;
      let t = a;
      t = Math.imul(t ^ (t >>> 15), t | 1);
      t ^= t + Math.imul(t ^ (t >>> 7), t | 61);
      return ((t ^ (t >>> 14)) >>> 0) / 4294967296;
    };
  }

  const circulo = (cx, cy, r) => `M${n(cx - r)} ${n(cy)}a${n(r)} ${n(r)} 0 1 0 ${n(2 * r)} 0a${n(r)} ${n(r)} 0 1 0 ${n(-2 * r)} 0Z`;

  /** Mancha orgánica cerrada (curva suave por puntos con radio irregular). */
  function mancha(cx, cy, r, semilla, irregular, puntos) {
    const R = rng(semilla), p = [];
    for (let i = 0; i < puntos; i++) {
      const a = (i / puntos) * TAU, k = 1 - irregular / 2 + R() * irregular;
      p.push([cx + Math.cos(a) * r * k, cy + Math.sin(a) * r * k * 0.86]);
    }
    let d = `M${n(p[0][0])} ${n(p[0][1])}`;
    for (let i = 0; i < puntos; i++) {
      const p0 = p[(i - 1 + puntos) % puntos], p1 = p[i], p2 = p[(i + 1) % puntos], p3 = p[(i + 2) % puntos];
      d += `C${n(p1[0] + (p2[0] - p0[0]) / 6)} ${n(p1[1] + (p2[1] - p0[1]) / 6)} ${n(p2[0] - (p3[0] - p1[0]) / 6)} ${n(p2[1] - (p3[1] - p1[1]) / 6)} ${n(p2[0])} ${n(p2[1])}`;
    }
    return d + "Z";
  }

  /* ───────────── 2. Astro: sombreado y texturas ───────────── */
  /** Definiciones comunes: recorte con la forma del astro y degradados de luz. */
  function defsComunes(c) {
    const u = c.u;
    return `<clipPath id="${u}cp"><path d="${c.forma}"/></clipPath>` +
      // luz desde arriba a la izquierda; el lado opuesto queda en sombra
      `<radialGradient id="${u}sh" cx=".35" cy=".3" r=".9"><stop offset="0" stop-color="#fff" stop-opacity=".34"/><stop offset=".4" stop-color="#fff" stop-opacity="0"/>` +
      `<stop offset=".78" stop-color="#070722" stop-opacity=".38"/><stop offset="1" stop-color="#04041a" stop-opacity=".74"/></radialGradient>` +
      // el Sol brilla: centro claro y borde del color del detalle (sin lado oscuro)
      `<radialGradient id="${u}ss" cx=".5" cy=".5" r=".5"><stop offset="0" stop-color="#fff" stop-opacity=".6"/><stop offset=".6" stop-color="#fff" stop-opacity="0"/>` +
      `<stop offset="1" stop-color="${c.det}" stop-opacity=".6"/></radialGradient>`;
  }

  function bandas(c, tormenta) {
    const { R, base, det, f } = c, r = rng(9);
    const cortes = [-1.2, -0.74, -0.52, -0.3, -0.1, 0.12, 0.34, 0.58, 0.8, 1.2];
    let o = `<g transform="rotate(-9 ${CX} ${CY})">`;
    for (let i = 0; i < cortes.length - 1; i++) {
      const y0 = CY + R * cortes[i], h = R * (cortes[i + 1] - cortes[i]), osc = i % 2 === 0;
      o += `<rect x="${n(CX - R * 1.3)}" y="${n(y0)}" width="${n(R * 2.6)}" height="${n(h + 0.5)}" fill="${osc ? det : claro(base, 0.35)}" opacity="${n((osc ? 0.85 : 0.45) * f * (0.65 + 0.35 * r()))}"/>`;
    }
    if (tormenta) {                                      // gran mancha (roja en planetas claros, azul oscuro en los oscuros)
      const col = luminosidad(base) > 140 ? mix(det, "#c2410c", 0.5) : oscuro(det, 0.35), x = CX + R * 0.3, y = CY + R * 0.32;
      o += `<ellipse cx="${n(x)}" cy="${n(y)}" rx="${n(R * 0.3)}" ry="${n(R * 0.17)}" fill="${col}" opacity="${n(0.95 * Math.max(c.f, 0.25))}"/>` +
           `<ellipse cx="${n(x - R * 0.03)}" cy="${n(y - R * 0.02)}" rx="${n(R * 0.18)}" ry="${n(R * 0.085)}" fill="${claro(col, 0.35)}" opacity="${n(0.45 * Math.max(c.f, 0.25))}"/>`;
    }
    return o + "</g>";
  }

  function crateres(c) {
    const R = rng(11), lista = [];
    for (let t = 0; t < 90 && lista.length < 9; t++) {
      const a = R() * TAU, d = Math.sqrt(R()) * c.R * 0.82, r = c.R * (0.07 + R() * 0.13), x = CX + Math.cos(a) * d, y = CY + Math.sin(a) * d;
      if (lista.some((q) => Math.hypot(q.x - x, q.y - y) < q.r + r + 2)) continue;
      lista.push({ x, y, r });
    }
    const p = (x, y, r, g) => `${n(x + r * Math.cos(g))} ${n(y + r * Math.sin(g))}`;
    return lista.map((q) =>
      `<circle cx="${n(q.x)}" cy="${n(q.y)}" r="${n(q.r)}" fill="${c.det}" opacity="${n(c.f * 0.8)}"/>` +
      `<path d="M${p(q.x, q.y, q.r, 0.35)}A${n(q.r)} ${n(q.r)} 0 0 1 ${p(q.x, q.y, q.r, 1.9)}" fill="none" stroke="${claro(c.base, 0.5)}" stroke-width="1.2" stroke-linecap="round" opacity="${n(c.f * 0.55)}"/>`).join("");
  }

  function continentes(c) {
    const lugares = [[-0.35, -0.25, 0.34], [0.3, -0.1, 0.3], [0.05, 0.42, 0.28], [-0.45, 0.35, 0.2], [0.52, 0.45, 0.18]];
    let o = lugares.map(([dx, dy, k], i) => `<path d="${mancha(CX + dx * c.R, CY + dy * c.R, c.R * k, 40 + i, 0.6, 9)}" fill="${c.det}" opacity="${n(c.f * 0.95)}"/>`).join("");
    const nubes = [[-0.1, -0.5, 0.2], [0.35, 0.18, 0.16], [-0.4, 0.1, 0.14]];
    return o + nubes.map(([dx, dy, k], i) => `<path d="${mancha(CX + dx * c.R, CY + dy * c.R, c.R * k, 70 + i, 0.5, 8)}" fill="#fff" opacity="${n(c.f * 0.4)}"/>`).join("");
  }

  function nubes(c) {
    const r = rng(4); let o = "";
    for (let i = 0; i < 7; i++) {
      const y = CY + c.R * (-0.78 + i * 0.26), dir = i % 2 ? 1 : -1, amp = c.R * 0.16;
      o += `<path d="M${n(CX - c.R * 1.1)} ${n(y)}q${n(c.R * 0.55)} ${n(amp * dir)} ${n(c.R * 1.1)} 0t${n(c.R * 1.1)} 0" fill="none" stroke="${i % 2 ? c.det : claro(c.base, 0.55)}" stroke-width="${n(c.R * (0.13 + r() * 0.06))}" stroke-linecap="round" opacity="${n(c.f * (i % 2 ? 0.55 : 0.5))}"/>`;
    }
    return o;
  }

  function manchas(c) {
    const r = rng(14); let o = "";
    for (let i = 0; i < 7; i++) {
      const a = r() * TAU, d = Math.sqrt(r()) * c.R * 0.75, x = CX + Math.cos(a) * d, y = CY + Math.sin(a) * d, k = c.R * (0.07 + r() * 0.12);
      o += `<path d="${mancha(x, y, k * 1.6, 60 + i, 0.35, 8)}" fill="${claro(c.base, 0.25)}" opacity="${n(c.f * 0.4)}"/>` +
           `<path d="${mancha(x, y, k, 80 + i, 0.4, 8)}" fill="${c.det}" opacity="${n(c.f * 0.9)}"/>`;
    }
    return o;
  }

  function casquetes(c) {
    const r = rng(6); let o = "";
    for (let i = 0; i < 4; i++) {
      const x = CX + (r() - 0.5) * c.R * 1.1, y = CY + (r() - 0.5) * c.R * 0.9, k = c.R * (0.2 + r() * 0.14);
      o += `<path d="${mancha(x, y, k, 100 + i, 0.5, 9)}" fill="${c.det}" opacity="${n(c.f * 0.6)}"/>`;
    }
    return o + `<ellipse cx="${CX}" cy="${n(CY - c.R * 0.95)}" rx="${n(c.R * 0.58)}" ry="${n(c.R * 0.3)}" fill="#f4f8ff" opacity="${n(c.f * 0.9)}"/>` +
      `<ellipse cx="${CX}" cy="${n(CY + c.R * 0.98)}" rx="${n(c.R * 0.42)}" ry="${n(c.R * 0.2)}" fill="#f4f8ff" opacity="${n(c.f * 0.8)}"/>`;
  }

  const TEXTURAS = { lisa: () => "", bandas: (c) => bandas(c, false), tormenta: (c) => bandas(c, true), crateres, continentes, nubes, manchas, casquetes };

  function capaAstro(c) {
    const tex = (TEXTURAS[c.s.textura] || TEXTURAS.lisa)(c);
    return `<g clip-path="url(#${c.u}cp)"><path d="${c.forma}" fill="${c.base}"/>${tex}<path d="${c.forma}" fill="url(#${c.u}${c.sol ? "ss" : "sh"})"/></g>`;
  }

  /* ───────────── 3. Anillos, lunas y atmósfera ───────────── */
  /** Bandas de anillo: [radio interior, radio exterior, oscurecimiento] (múltiplos del radio del astro). */
  const ANILLOS = { fino: [[1.45, 1.63, 0]], ancho: [[1.25, 1.5, 0.14], [1.56, 1.85, 0]], doble: [[1.3, 1.48, 0], [1.62, 1.85, 0.1]] };
  /** Media corona elíptica: la de atrás (arriba) o la de adelante (abajo, tapa al astro). */
  const semi = (r1, r2, k, frente) => frente
    ? `M${n(CX - r2)} ${CY}A${n(r2)} ${n(r2 * k)} 0 0 0 ${n(CX + r2)} ${CY}L${n(CX + r1)} ${CY}A${n(r1)} ${n(r1 * k)} 0 0 1 ${n(CX - r1)} ${CY}Z`
    : `M${n(CX - r2)} ${CY}A${n(r2)} ${n(r2 * k)} 0 0 1 ${n(CX + r2)} ${CY}L${n(CX + r1)} ${CY}A${n(r1)} ${n(r1 * k)} 0 0 0 ${n(CX - r1)} ${CY}Z`;

  function anillos(c) {
    const s = c.s, tipo = s.anillos;
    if (tipo === "ninguno") return { atras: "", frente: "" };
    const R = c.R, k = 0.3, col = s.color_anillos, rot = `rotate(${n(s.anillos_inclinacion)} ${CX} ${CY})`;
    let atras = "", frente = "";
    if (tipo === "polvo") {                              // cinturón de partículas
      [[1.5, "1 3.4", 2.2, 0.95], [1.75, "2 5", 2.8, 0.8]].forEach(([m, da, w, op]) => {
        const r = R * m, arco = (sw) => `<path d="M${n(CX - r)} ${CY}A${n(r)} ${n(r * k)} 0 0 ${sw} ${n(CX + r)} ${CY}" fill="none" stroke="${col}" stroke-width="${w}" stroke-linecap="round" stroke-dasharray="${da}" opacity="${op}"/>`;
        atras += arco(1); frente += arco(0);
      });
    } else {
      for (const [a, b, tono] of ANILLOS[tipo] || ANILLOS.fino) {
        const relleno = tono ? oscuro(col, tono) : col;
        atras += `<path d="${semi(R * a, R * b, k, false)}" fill="${relleno}" opacity=".92"/>`;
        frente += `<path d="${semi(R * a, R * b, k, true)}" fill="${relleno}" opacity=".92"/>`;
      }
    }
    return { atras: `<g transform="${rot}">${atras}</g>`, frente: `<g transform="${rot}">${frente}</g>` };
  }

  /** Lunas sobre órbitas elípticas: las de la mitad de atrás quedan detrás del astro, las de adelante delante. */
  function lunas(c) {
    const s = c.s, cuantas = { ninguna: 0, una: 1, dos: 2, tres: 3 }[s.lunas] || 0;
    if (!cuantas) return { atras: "", frente: "" };
    const tam = [0.2, 0.14, 0.11], fase = [0, 0.36, 0.67], R = c.R, base = s.anillos !== "ninguno" ? 1.95 : 1.55;
    let atras = "", frente = "";
    for (let i = 0; i < cuantas; i++) {
      const mr = R * tam[i], rx = Math.min(R * base + 9 * i, 94 - mr), ry = rx * 0.38, a = (s.orbita + fase[i]) * TAU;
      const x = CX + rx * Math.cos(a), y = CY + ry * Math.sin(a);
      atras += `<ellipse cx="${CX}" cy="${CY}" rx="${n(rx)}" ry="${n(ry)}" fill="none" stroke="#fff" stroke-opacity=".2" stroke-width=".9" stroke-dasharray="2 3"/>`;
      const luna = `<circle cx="${n(x)}" cy="${n(y)}" r="${n(mr)}" fill="${s.color_luna}"/>` +
        `<circle cx="${n(x - mr * 0.3)}" cy="${n(y + mr * 0.25)}" r="${n(mr * 0.22)}" fill="${oscuro(s.color_luna, 0.35)}" opacity=".5"/>` +
        `<circle cx="${n(x + mr * 0.35)}" cy="${n(y - mr * 0.3)}" r="${n(mr * 0.15)}" fill="${oscuro(s.color_luna, 0.35)}" opacity=".45"/>` +
        `<circle cx="${n(x)}" cy="${n(y)}" r="${n(mr)}" fill="url(#${c.u}sh)"/>`;
      if (Math.sin(a) > 0) frente += luna; else atras += luna;
    }
    const rot = `rotate(-14 ${CX} ${CY})`;
    return { atras: `<g transform="${rot}">${atras}</g>`, frente: `<g transform="${rot}">${frente}</g>` };
  }

  /** Atmósfera: halo fino, resplandor amplio o corona con rayos (para el Sol). */
  function atmosfera(c) {
    const s = c.s, tipo = s.atmosfera, k = s.brillo;
    if (tipo === "ninguna") return { defs: "", atras: "", rim: "" };
    const col = s.color_atmosfera, rg = c.R * { halo: 1.4, brillo: 2.05, corona: 1.9 }[tipo], a = 0.2 + 0.55 * k, u = c.u;
    const defs = `<radialGradient id="${u}gl" cx="${CX}" cy="${CY}" r="${n(rg)}" gradientUnits="userSpaceOnUse"><stop offset="${n((c.R / rg) * 0.9)}" stop-color="${col}" stop-opacity="${n(a)}"/>` +
      `<stop offset="${n((c.R / rg + 1) / 2)}" stop-color="${col}" stop-opacity="${n(a * 0.3)}"/><stop offset="1" stop-color="${col}" stop-opacity="0"/></radialGradient>`;
    let atras = `<circle cx="${CX}" cy="${CY}" r="${n(rg)}" fill="url(#${u}gl)"/>`;
    if (tipo === "corona") {
      for (let i = 0; i < 16; i++) {
        const g = (i / 16) * TAU + 0.1, w = 0.1, largo = c.R * (i % 2 ? 1.38 : 1.58), r0 = c.R * 0.9;
        atras += `<path d="M${n(CX + Math.cos(g - w) * r0)} ${n(CY + Math.sin(g - w) * r0)}L${n(CX + Math.cos(g) * largo)} ${n(CY + Math.sin(g) * largo)}L${n(CX + Math.cos(g + w) * r0)} ${n(CY + Math.sin(g + w) * r0)}Z" fill="${col}" opacity="${n(0.25 + 0.5 * k)}"/>`;
      }
    }
    const rim = `<path d="${c.forma}" fill="none" stroke="${col}" stroke-width="${n(c.R * 0.16)}" stroke-opacity="${n(0.12 + 0.5 * k)}" clip-path="url(#${u}cp)"/>`;
    return { defs, atras, rim };
  }

  /* ───────────── 4. Fondo, acompañantes y carita ───────────── */
  function fondo(c) {
    const s = c.s, u = c.u, col = s.color_fondo, tipo = s.fondo;
    let defs = `<clipPath id="${u}fc"><circle cx="${CX}" cy="${CY}" r="100"/></clipPath>`, relleno = col, o = "";
    if (tipo === "degradado") {
      defs += `<linearGradient id="${u}fd" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="${claro(col, 0.22)}"/><stop offset="1" stop-color="${oscuro(col, 0.45)}"/></linearGradient>`;
      relleno = `url(#${u}fd)`;
    } else if (tipo !== "liso") {
      defs += `<radialGradient id="${u}fd" cx=".5" cy=".42" r=".75"><stop offset="0" stop-color="${claro(col, 0.14)}"/><stop offset="1" stop-color="${oscuro(col, 0.5)}"/></radialGradient>`;
      relleno = `url(#${u}fd)`;
    }
    o += `<circle cx="${CX}" cy="${CY}" r="100" fill="${relleno}"/>`;
    if (tipo === "nebulosa") {
      const n1 = mix(col, "#ff4fa3", 0.65), n2 = mix(col, "#4f8bff", 0.65);
      defs += `<radialGradient id="${u}n1"><stop offset="0" stop-color="${n1}" stop-opacity=".6"/><stop offset="1" stop-color="${n1}" stop-opacity="0"/></radialGradient>` +
              `<radialGradient id="${u}n2"><stop offset="0" stop-color="${n2}" stop-opacity=".55"/><stop offset="1" stop-color="${n2}" stop-opacity="0"/></radialGradient>`;
      o += `<g clip-path="url(#${u}fc)"><ellipse cx="62" cy="48" rx="78" ry="42" transform="rotate(-24 62 48)" fill="url(#${u}n1)"/>` +
           `<ellipse cx="148" cy="154" rx="82" ry="44" transform="rotate(-18 148 154)" fill="url(#${u}n2)"/></g>`;
    }
    if (tipo === "estrellas" || tipo === "nebulosa") {
      const r = rng(tipo === "nebulosa" ? 8 : 5), total = tipo === "nebulosa" ? 26 : 44;
      for (let i = 0; i < total; i++) {
        const a = r() * TAU, d = Math.sqrt(r()) * 96, x = CX + Math.cos(a) * d, y = CY + Math.sin(a) * d, rad = 0.45 + r() * 1.0, op = n(0.35 + r() * 0.6);
        o += i % 9 === 0
          ? `<path d="M${n(x)} ${n(y - 3.6)}Q${n(x)} ${n(y)} ${n(x + 3.6)} ${n(y)}Q${n(x)} ${n(y)} ${n(x)} ${n(y + 3.6)}Q${n(x)} ${n(y)} ${n(x - 3.6)} ${n(y)}Q${n(x)} ${n(y)} ${n(x)} ${n(y - 3.6)}Z" fill="#fff" opacity="${op}"/>`
          : `<circle cx="${n(x)}" cy="${n(y)}" r="${n(rad)}" fill="#fff" opacity="${op}"/>`;
      }
    }
    return { defs, capa: o };
  }

  /** Acompañantes (van detrás del astro, en las esquinas). */
  const EXTRAS = {
    ninguno: () => ({ defs: "", capa: "" }),
    cometa: (c) => ({
      defs: `<linearGradient id="${c.u}cm" gradientUnits="userSpaceOnUse" x1="148" y1="54" x2="170" y2="32"><stop offset="0" stop-color="#fff" stop-opacity=".95"/><stop offset="1" stop-color="#9fd0ff" stop-opacity="0"/></linearGradient>`,
      capa: `<path d="M152.2 57.2L170 32L144.8 50.8Z" fill="url(#${c.u}cm)"/><circle cx="148" cy="54" r="9" fill="#9fd0ff" opacity=".22"/><circle cx="148" cy="54" r="4.6" fill="#fff"/>`,
    }),
    satelite: () => ({
      defs: "",
      capa: `<g transform="translate(48 50) rotate(-30)"><rect x="-27" y="-4" width="19" height="8" rx="1" fill="#3b6fd9" stroke="#bcd0ff" stroke-width=".6"/><rect x="8" y="-4" width="19" height="8" rx="1" fill="#3b6fd9" stroke="#bcd0ff" stroke-width=".6"/>` +
        `<path d="M-21 -4v8M-15 -4v8M14 -4v8M20 -4v8" stroke="#bcd0ff" stroke-width=".5"/><rect x="-8" y="-5.5" width="16" height="11" rx="2" fill="#d9deeb" stroke="#8a93ad" stroke-width=".8"/>` +
        `<path d="M0 -5.5V-12" stroke="#d9deeb" stroke-width="1"/><circle cx="0" cy="-13" r="1.8" fill="#ff6b6b"/></g>`,
    }),
    cohete: () => ({
      defs: "",
      capa: `<g transform="translate(152 148) rotate(45)"><path d="M-3 10Q0 25 3 10Z" fill="#ffb347"/><path d="M-1.6 10Q0 18 1.6 10Z" fill="#fff3c4"/>` +
        `<path d="M-5 3L-11 13L-5 10ZM5 3L11 13L5 10Z" fill="#e5484d"/><path d="M0 -17C7 -10 7 4 5 10L-5 10C-7 4 -7 -10 0 -17Z" fill="#f4f6fb"/>` +
        `<path d="M0 -17C3.5 -13.5 5.3 -10 5.7 -7L-5.7 -7C-5.3 -10 -3.5 -13.5 0 -17Z" fill="#e5484d"/><circle cx="0" cy="-1" r="2.7" fill="#7fc4ff" stroke="#5b6786" stroke-width=".9"/></g>`,
    }),
    meteoros: (c) => {
      const lineas = [[170, 44, 34], [186, 78, 26], [150, 22, 22]];
      return {
        defs: lineas.map(([x, y, L], i) => `<linearGradient id="${c.u}m${i}" gradientUnits="userSpaceOnUse" x1="${x}" y1="${y}" x2="${x - L}" y2="${n(y - L * 0.5)}"><stop offset="0" stop-color="#fff"/><stop offset="1" stop-color="#fff" stop-opacity="0"/></linearGradient>`).join(""),
        capa: lineas.map(([x, y, L], i) => `<path d="M${x} ${y}L${x - L} ${n(y - L * 0.5)}" stroke="url(#${c.u}m${i})" stroke-width="${i === 0 ? 2 : 1.5}" stroke-linecap="round"/>`).join(""),
      };
    },
  };

  /** Carita: los trazos son oscuros sobre astros claros y blancos sobre astros oscuros. */
  const CARAS = {
    ninguna: () => "",
    feliz: (c, t) => ojosRedondos(c, t) + sonrisa(c, t) + rubor(c),
    guino: (c, t) => ojo(c.R, -1, t) + arcoOjo(c, 1, t) + sonrisa(c, t) + rubor(c),
    genial: (c, t) => gafas(c) + `<path d="M${n(CX - c.R * 0.16)} ${n(CY + c.R * 0.26)}Q${n(CX + c.R * 0.06)} ${n(CY + c.R * 0.4)} ${n(CX + c.R * 0.24)} ${n(CY + c.R * 0.2)}" ${trazo(c, t)}/>`,
    sorprendido: (c, t) => ojosRedondos(c, t, 1.25) + `<ellipse cx="${CX}" cy="${n(CY + c.R * 0.3)}" rx="${n(c.R * 0.07)}" ry="${n(c.R * 0.1)}" fill="${t.tinta}"/>`,
    dormido: (c, t) => [-1, 1].map((sg) => `<path d="M${n(CX + sg * c.R * 0.3 - c.R * 0.11)} ${n(CY - c.R * 0.02)}Q${n(CX + sg * c.R * 0.3)} ${n(CY + c.R * 0.1)} ${n(CX + sg * c.R * 0.3 + c.R * 0.11)} ${n(CY - c.R * 0.02)}" ${trazo(c, t)}/>`).join("") +
      `<path d="M${n(CX - c.R * 0.07)} ${n(CY + c.R * 0.28)}Q${CX} ${n(CY + c.R * 0.33)} ${n(CX + c.R * 0.07)} ${n(CY + c.R * 0.28)}" ${trazo(c, t)}/>` +
      `<path d="M${n(CX + c.R * 0.62)} ${n(CY - c.R * 0.62)}h${n(c.R * 0.2)}l${n(-c.R * 0.2)} ${n(c.R * 0.2)}h${n(c.R * 0.2)}" ${trazo(c, t)}/>`,
  };
  const trazo = (c, t) => `fill="none" stroke="${t.tinta}" stroke-width="${n(c.R * 0.07)}" stroke-linecap="round" stroke-linejoin="round"`;
  function ojo(R, sg, t, k) {
    const x = CX + sg * R * 0.3, y = CY - R * 0.02, s = k || 1;
    return `<ellipse cx="${n(x)}" cy="${n(y)}" rx="${n(R * 0.075 * s)}" ry="${n(R * 0.1 * s)}" fill="${t.tinta}"/><circle cx="${n(x + R * 0.025)}" cy="${n(y - R * 0.04 * s)}" r="${n(R * 0.03)}" fill="${t.brillo}"/>`;
  }
  const ojosRedondos = (c, t, k) => ojo(c.R, -1, t, k) + ojo(c.R, 1, t, k);
  const arcoOjo = (c, sg, t) => { const x = CX + sg * c.R * 0.3, y = CY; return `<path d="M${n(x - c.R * 0.09)} ${n(y + c.R * 0.02)}Q${n(x)} ${n(y - c.R * 0.12)} ${n(x + c.R * 0.09)} ${n(y + c.R * 0.02)}" ${trazo(c, t)}/>`; };
  const sonrisa = (c, t) => `<path d="M${n(CX - c.R * 0.2)} ${n(CY + c.R * 0.2)}Q${CX} ${n(CY + c.R * 0.42)} ${n(CX + c.R * 0.2)} ${n(CY + c.R * 0.2)}" ${trazo(c, t)}/>`;
  const rubor = (c) => [-1, 1].map((sg) => `<circle cx="${n(CX + sg * c.R * 0.52)}" cy="${n(CY + c.R * 0.2)}" r="${n(c.R * 0.1)}" fill="#ff6b8a" opacity=".38"/>`).join("");
  function gafas(c) {
    const R = c.R, w = R * 0.44, h = R * 0.27, y = CY - R * 0.16;
    return [-1, 1].map((sg) => { const x = sg < 0 ? CX - R * 0.5 : CX + R * 0.06;
      return `<rect x="${n(x)}" y="${n(y)}" width="${n(w)}" height="${n(h)}" rx="${n(R * 0.09)}" fill="#14141f"/><path d="M${n(x + w * 0.15)} ${n(y + h * 0.3)}l${n(w * 0.25)} ${n(-h * 0.0)}" stroke="#fff" stroke-opacity=".4" stroke-width="${n(R * 0.04)}" stroke-linecap="round"/>`; }).join("") +
      `<path d="M${n(CX - R * 0.06)} ${n(y + h * 0.3)}H${n(CX + R * 0.06)}" stroke="#14141f" stroke-width="${n(R * 0.05)}"/>`;
  }
  function capaCara(c) {
    const f = CARAS[c.s.cara] || CARAS.ninguna, oscuro_ = luminosidad(c.base) > 120;
    return f(c, { tinta: oscuro_ ? "#1d1630" : "#ffffff", brillo: oscuro_ ? "#ffffff" : "#1d1630" });
  }

  /* ───────────── 5. Composición ───────────── */
  const CAPAS = ["fondo", "extras", "atras", "astro", "frente", "cara"];
  /** Vistas predefinidas [x, y, ancho, alto]. */
  const VISTAS = { completo: [0, 0, 200, 200], retrato: [20, 20, 160, 160], planeta: [38, 38, 124, 124] };
  const caja = (vista) => (VISTAS[vista] || VISTAS.completo).slice();
  const viewBox = (v) => v.map(n).join(" ");

  /** Todas las capas del avatar como texto, más las definiciones (gradientes, recortes). */
  function partes(s, o) {
    const R = 48 * s.tamano;
    const c = { s, u: o.u, R, sol: s.astro === "sol", base: s.color_base, det: s.color_detalle, f: s.textura_fuerza,
      forma: s.astro === "asteroide" ? mancha(CX, CY, R, 21, 0.3, 11) : circulo(CX, CY, R) };
    const atm = atmosfera(c), fon = fondo(c), ani = anillos(c), lun = lunas(c), ext = (EXTRAS[s.extra] || EXTRAS.ninguno)(c);
    return {
      defs: defsComunes(c) + atm.defs + fon.defs + ext.defs,
      fondo: fon.capa, extras: ext.capa,
      atras: atm.atras + ani.atras + lun.atras,
      astro: capaAstro(c) + atm.rim,
      frente: ani.frente + lun.frente,
      cara: capaCara(c),
    };
  }

  /** SVG completo como texto (miniaturas y avatares pequeños del sitio). */
  function svg(cfg, opciones) {
    const o = Object.assign({ vista: "completo" }, opciones);
    o.u = o.u || "av" + ++contador + "-";
    const p = partes(cfg, o);
    return `<svg xmlns="http://www.w3.org/2000/svg" viewBox="${viewBox(caja(o.vista))}" class="avatar-svg" role="img" aria-label="${texto(o.etiqueta || "Avatar")}">` +
      `<defs>${p.defs}</defs>${CAPAS.map((id) => `<g data-capa="${id}">${p[id]}</g>`).join("")}</svg>`;
  }

  /* ───────────── 6. Controlador animado (creador) ───────────── */
  const NUMEROS = ["tamano", "textura_fuerza", "anillos_inclinacion", "orbita", "brillo"];
  const COLORES = ["color_base", "color_detalle", "color_anillos", "color_luna", "color_atmosfera", "color_fondo"];
  /** Qué capas "saltan" cuando cambia una opción discreta (el fondo no salta: sería mareante). */
  const CAPAS_POR_CAMPO = {
    astro: ["astro", "cara"], textura: ["astro"], anillos: ["atras", "frente"], lunas: ["atras", "frente"],
    atmosfera: ["atras"], cara: ["cara"], extra: ["extras"],
  };
  const acercar = (a, b) => {
    const x = hex2rgb(a), y = hex2rgb(b);
    return Math.max(...x.map((v, i) => Math.abs(y[i] - v))) < 2 ? b : rgb2hex(x.map((v, i) => v + (y[i] - v) * 0.26));
  };

  /**
   * Dibuja el avatar dentro de `el` y devuelve un control:
   *   set(cfg)     -> anima hacia la nueva configuración (números y colores se funden, las opciones "saltan")
   *   vista(nombre)-> acerca o aleja la cámara con una transición
   */
  function crear(el, cfg, opciones) {
    const o = Object.assign({ vista: "completo" }, opciones);
    o.u = "av" + ++contador + "-";
    let actual = Object.assign({}, cfg), meta = Object.assign({}, cfg), vistaNombre = o.vista;
    let vb = caja(vistaNombre), raf = 0;
    el.innerHTML = `<svg xmlns="http://www.w3.org/2000/svg" class="avatar-svg" role="img" aria-label="Vista previa de tu avatar"><defs></defs><g class="fig">` +
      CAPAS.map((id) => `<g data-capa="${id}"></g>`).join("") + `</g></svg>`;
    const raiz = el.firstElementChild, defs = raiz.querySelector("defs");
    const capas = {}; CAPAS.forEach((id) => (capas[id] = raiz.querySelector(`[data-capa="${id}"]`)));
    const cache = {};

    function pintar() {
      const p = partes(actual, o);
      if (cache.defs !== p.defs) { defs.innerHTML = p.defs; cache.defs = p.defs; }
      for (const id of CAPAS) if (cache[id] !== p[id]) { capas[id].innerHTML = p[id]; cache[id] = p[id]; }   // solo se toca lo que cambió
      raiz.setAttribute("viewBox", viewBox(vb));
    }
    function paso() {
      let mueve = false;
      for (const k of NUMEROS) { const d = meta[k] - actual[k]; if (Math.abs(d) > 0.002) { actual[k] += d * 0.2; mueve = true; } else actual[k] = meta[k]; }
      for (const k of COLORES) if (actual[k] !== meta[k]) { actual[k] = acercar(actual[k], meta[k]); mueve = true; }
      const objetivo = caja(vistaNombre);
      vb = vb.map((v, i) => { const d = objetivo[i] - v; if (Math.abs(d) > 0.05) { mueve = true; return v + d * 0.16; } return objetivo[i]; });
      pintar();
      raf = mueve ? requestAnimationFrame(paso) : 0;
    }
    const arrancar = () => { if (!raf) raf = requestAnimationFrame(paso); };
    function saltar(nombres) {
      nombres.forEach((id) => { const g = capas[id]; g.classList.remove("capa-cambia"); g.getBoundingClientRect(); g.classList.add("capa-cambia"); });
    }
    pintar();

    return {
      set(nuevo, animar = true) {
        const cambiadas = new Set();
        for (const k of Object.keys(nuevo)) {
          if (NUMEROS.includes(k) || COLORES.includes(k)) continue;
          if (actual[k] !== nuevo[k]) { actual[k] = nuevo[k]; (CAPAS_POR_CAMPO[k] || []).forEach((id) => cambiadas.add(id)); }
        }
        meta = Object.assign({}, nuevo);
        if (!animar) { actual = Object.assign({}, nuevo); vb = caja(vistaNombre); }
        pintar(); saltar(cambiadas); arrancar();
      },
      vista(nombre) { vistaNombre = nombre; arrancar(); },
      destruir() { if (raf) cancelAnimationFrame(raf); el.innerHTML = ""; },
    };
  }

  /* ───────────── 7. Avatares pequeños del sitio ───────────── */
  function hidratar(raiz) {
    (raiz || document).querySelectorAll("[data-avatar]").forEach((el) => {
      try {
        const cfg = JSON.parse(el.getAttribute("data-avatar"));
        el.innerHTML = svg(cfg, { vista: el.getAttribute("data-vista") || "retrato" });
      } catch (e) { /* se queda la imagen de respaldo */ }
    });
  }

  G.AvatarCore = { svg, crear, hidratar, VISTAS };
  if (typeof document !== "undefined") hidratar(document);
})(typeof window !== "undefined" ? window : globalThis);
