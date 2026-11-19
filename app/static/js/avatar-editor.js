/* Activate + Chimal · avatar-editor.js
 *
 * Interfaz del creador de astros. NO tiene listas de opciones escritas a mano: todo (categorías,
 * miniaturas, deslizadores, paletas) se genera a partir de `avatar_esquema.json`, así que añadir una
 * opción nueva solo requiere tocar el esquema y dibujarla en avatar-core.js.
 *
 * Piezas:  esquema -> constructores de controles (opciones / color / slider)
 *          estado `cfg` -> control.set() (vista previa animada) + sincronizarUI() + miniaturas
 *          historial (deshacer), aleatorio, restablecer, guardado sin recargar.
 */
(function () {
  "use strict";
  const raiz = document.getElementById("creador");
  if (!raiz || !window.AvatarCore) return;

  const esquema = JSON.parse(document.getElementById("avatar-esquema").textContent);
  const guardada = JSON.parse(raiz.dataset.config);
  const SECCIONES = {};
  esquema.categorias.forEach((c) => c.secciones.forEach((s) => (SECCIONES[s.campo] = s)));

  const nav = document.getElementById("cr-categorias"), panel = document.getElementById("cr-panel");
  const estado = document.getElementById("cr-estado"), form = document.getElementById("creador-form");
  const btn = (a) => raiz.querySelector(`[data-accion="${a}"]`);
  const esc = (t) => String(t).replace(/[&<>"']/g, (c) => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" }[c]));
  const icono = (n) => `<svg class="ico" aria-hidden="true" focusable="false"><use href="#i-${n}"/></svg>`;

  let cfg = Object.assign({}, guardada), categoria = esquema.categorias[0], vistaManual = null;
  const control = AvatarCore.crear(document.getElementById("cr-escenario"), cfg, { texturas: true, vista: categoria.vista });

  /* ───────────── Constructores de controles ───────────── */
  function cfgMiniatura(sec, op) {
    const c = Object.assign({}, cfg);
    if (sec.campo === "astro") Object.assign(c, esquema.presets_astro[op.id] || {});   // la miniatura muestra el astro con sus lunas y anillos
    c[sec.campo] = op.id;
    return c;
  }
  const miniatura = (sec, op) => AvatarCore.svg(cfgMiniatura(sec, op), { vista: sec.vista, etiqueta: op.nombre });

  function htmlOpciones(sec) {
    const tiles = sec.opciones.filter((o) => !o.oculto).map((o) =>
      `<label class="cr-tile${sec.vista ? "" : " cr-tile--texto"}" data-id="${o.id}">` +
      `<input type="radio" name="${sec.campo}" value="${o.id}"><span class="cr-marca">${icono("check")}</span>` +
      (sec.vista ? `<span class="cr-mini">${miniatura(sec, o)}</span>` : "") + `<span class="cr-nombre">${esc(o.nombre)}</span></label>`).join("");
    return `<fieldset class="cr-seccion" data-campo="${sec.campo}"><legend>${esc(sec.titulo)}</legend><div class="cr-tiles">${tiles}</div></fieldset>`;
  }
  function htmlColor(sec) {
    const sw = sec.paleta.map((p) => `<button type="button" class="cr-color" data-valor="${p.valor}" style="--c:${p.valor}" aria-pressed="false" aria-label="${esc(p.nombre)}" title="${esc(p.nombre)}"><span class="cr-marca">${icono("check")}</span></button>`).join("");
    return `<fieldset class="cr-seccion" data-campo="${sec.campo}"><legend>${esc(sec.titulo)}</legend><div class="cr-colores">${sw}` +
      `<label class="cr-color cr-color--libre" title="Color personalizado"><input type="color" aria-label="Color personalizado: ${esc(sec.titulo)}"><span class="cr-marca">${icono("check")}</span></label></div>` +
      `<p class="cr-hex" data-hex></p></fieldset>`;
  }
  function htmlSlider(sec) {
    return `<div class="cr-seccion cr-slider" data-campo="${sec.campo}"><div class="cr-slider-cab"><label for="cr-${sec.campo}">${esc(sec.titulo)}</label><output for="cr-${sec.campo}"></output></div>` +
      `<input id="cr-${sec.campo}" type="range" min="${sec.min}" max="${sec.max}" step="${sec.paso}"></div>`;
  }
  const CONSTRUCTORES = { opciones: htmlOpciones, color: htmlColor, slider: htmlSlider };

  /* ───────────── Pintar categorías y panel ───────────── */
  function dibujarCategorias() {
    nav.innerHTML = esquema.categorias.map((c) =>
      `<button type="button" role="tab" class="cr-cat" data-cat="${c.id}" aria-selected="false" aria-controls="cr-panel">${icono(c.icono)}<span>${esc(c.nombre)}</span></button>`).join("");
  }
  function elegirCategoria(id, enfocar) {
    categoria = esquema.categorias.find((c) => c.id === id);
    nav.querySelectorAll(".cr-cat").forEach((b) => { const on = b.dataset.cat === id; b.setAttribute("aria-selected", on); b.tabIndex = on ? 0 : -1; if (on && enfocar) b.focus(); });
    panel.setAttribute("aria-label", categoria.nombre);
    panel.innerHTML = categoria.secciones.map((s, i) => CONSTRUCTORES[s.tipo](s).replace(/^<(\w+)/, `<$1 style="--i:${i}"`)).join("");
    panel.scrollTop = 0;
    vistaManual = null; actualizarBotonVista();
    control.vista(categoria.vista);
    sincronizarUI();
  }

  const cumple = (cond) => Object.keys(cond).every((k) => cfg[k] === cond[k]);
  const hexNombre = (sec, v) => { const p = sec.paleta.find((x) => x.valor.toLowerCase() === v.toLowerCase()); return p ? p.nombre : v.toUpperCase(); };

  /** Refleja `cfg` en todos los controles visibles (marcas, valores y visibilidad condicional). */
  function sincronizarUI() {
    panel.querySelectorAll("[data-campo]").forEach((el) => {
      const sec = SECCIONES[el.dataset.campo], v = cfg[sec.campo];
      el.hidden = !!((sec.mostrar_si && !cumple(sec.mostrar_si)) || (sec.ocultar_si && cumple(sec.ocultar_si)));
      if (sec.tipo === "opciones") {
        el.querySelectorAll(".cr-tile").forEach((t) => { const on = t.dataset.id === v; t.classList.toggle("cr-sel", on); t.querySelector("input").checked = on; });
      } else if (sec.tipo === "color") {
        let hay = false;
        el.querySelectorAll(".cr-color[data-valor]").forEach((b) => { const on = b.dataset.valor.toLowerCase() === v.toLowerCase(); hay = hay || on; b.classList.toggle("cr-sel", on); b.setAttribute("aria-pressed", on); });
        const libre = el.querySelector(".cr-color--libre");
        libre.classList.toggle("cr-sel", !hay); libre.style.setProperty("--c", hay ? "" : v); libre.querySelector("input").value = v;
        el.querySelector("[data-hex]").textContent = hexNombre(sec, v);
      } else {
        const inp = el.querySelector("input"), min = +sec.min, max = +sec.max, mostrado = sec.invertir ? min + max - v : v;
        inp.value = mostrado;
        const p = (mostrado - min) / (max - min);
        el.style.setProperty("--p", (p * 100).toFixed(1) + "%");
        el.querySelector("output").textContent = sec.unidad ? Math.round(v) + sec.unidad : Math.round((sec.invertir ? 1 - p : p) * 100) + " %";
      }
    });
  }

  /** Las miniaturas se redibujan (con un pequeño retraso) cuando cambia algo que las afecta. */
  let temporizador = 0;
  function refrescarMiniaturas() {
    clearTimeout(temporizador);
    temporizador = setTimeout(() => {
      panel.querySelectorAll(".cr-seccion[data-campo]").forEach((el) => {
        const sec = SECCIONES[el.dataset.campo];
        if (sec.tipo !== "opciones" || !sec.vista) return;
        el.querySelectorAll(".cr-tile").forEach((t) => {
          const op = sec.opciones.find((o) => o.id === t.dataset.id);
          t.querySelector(".cr-mini").innerHTML = miniatura(sec, op);
        });
      });
    }, 140);
  }

  /* ───────────── Cambios, historial y guardado ───────────── */
  const pila = []; let ultimo = { campo: null, t: 0 }, sucio = false;
  function apilar(campo) {
    const ahora = Date.now();
    if (campo === ultimo.campo && ahora - ultimo.t < 700) { ultimo.t = ahora; return; }   // un deslizador = un solo paso
    pila.push(JSON.stringify(cfg)); if (pila.length > 40) pila.shift();
    ultimo = { campo, t: ahora }; btn("deshacer").disabled = false;
  }
  function aplicar(nuevo, campo) {
    if (campo) apilar(campo);
    cfg = nuevo; control.set(cfg); sincronizarUI(); refrescarMiniaturas();
    sucio = JSON.stringify(cfg) !== JSON.stringify(guardada);
    if (sucio) mensaje("Cambios sin guardar");
  }
  function cambiar(campo, valor) {
    const nuevo = Object.assign({}, cfg);
    if (campo === "astro") Object.assign(nuevo, esquema.presets_astro[valor] || {});   // cada astro trae sus colores, anillos, lunas y atmósfera
    nuevo[campo] = valor;
    aplicar(nuevo, campo);
  }
  function mensaje(t) { estado.textContent = t; }

  function aleatorio() {
    const R = (a) => a[Math.floor(Math.random() * a.length)], n = Object.assign({}, cfg);
    const elegir = (campo) => {
      const sec = SECCIONES[campo];
      if (sec.tipo === "color") return R(sec.paleta).valor;
      const ids = sec.opciones.filter((o) => !o.oculto).map((o) => o.id), ninguno = ids.find((i) => /^ning/.test(i));
      return ninguno && Math.random() < 0.5 ? ninguno : R(ids);
    };
    n.astro = R(Object.keys(esquema.presets_astro));                  // un astro real, con sus anillos y lunas...
    Object.assign(n, esquema.presets_astro[n.astro]);
    if (Math.random() < 0.35) { n.color_base = elegir("color_base"); n.color_detalle = elegir("color_detalle"); }   // ...o un mundo inventado
    for (const campo of ["cara", "fondo", "color_fondo", "extra"]) n[campo] = elegir(campo);
    n.orbita = Math.round(Math.random() * 100) / 100;
    aplicar(n, "*" + Date.now());
    const d = btn("aleatorio"); d.classList.remove("cr-gira"); void d.offsetWidth; d.classList.add("cr-gira");
  }
  function deshacer() {
    const previo = pila.pop(); if (!previo) return;
    cfg = JSON.parse(previo); control.set(cfg); sincronizarUI(); refrescarMiniaturas();
    btn("deshacer").disabled = !pila.length; ultimo = { campo: null, t: 0 };
    sucio = JSON.stringify(cfg) !== JSON.stringify(guardada); mensaje(sucio ? "Cambios sin guardar" : "");
  }
  function guardar() {
    const b = btn("guardar"), datos = new FormData(form);
    datos.set("config", JSON.stringify(cfg));
    b.classList.add("cargando");
    fetch(form.action, { method: "POST", body: datos, credentials: "same-origin", headers: { "X-Requested-With": "fetch" } })
      .then((r) => (r.ok ? r.json() : Promise.reject()))
      .then(() => {
        Object.assign(guardada, cfg); sucio = false; mensaje("¡Avatar guardado!");
        document.querySelectorAll(".menu-avatar [data-avatar]").forEach((el) => { el.setAttribute("data-avatar", JSON.stringify(cfg)); AvatarCore.hidratar(el.parentNode); });
      })
      .catch(() => { document.getElementById("creador-config").value = JSON.stringify(cfg); sucio = false; form.submit(); })
      .finally(() => b.classList.remove("cargando"));
  }
  function actualizarBotonVista() {
    const b = btn("vista"), cerca = (vistaManual || categoria.vista) !== "completo";
    b.setAttribute("aria-pressed", cerca); b.classList.toggle("cr-activo", cerca);
  }

  /* ───────────── Eventos ───────────── */
  nav.addEventListener("click", (e) => { const b = e.target.closest(".cr-cat"); if (b) elegirCategoria(b.dataset.cat); });
  nav.addEventListener("keydown", (e) => {
    const k = { ArrowRight: 1, ArrowDown: 1, ArrowLeft: -1, ArrowUp: -1 }[e.key]; if (!k) return;
    const i = esquema.categorias.indexOf(categoria), sig = esquema.categorias[(i + k + esquema.categorias.length) % esquema.categorias.length];
    elegirCategoria(sig.id, true); e.preventDefault();
  });
  panel.addEventListener("change", (e) => { if (e.target.matches(".cr-tile input")) cambiar(e.target.name, e.target.value); });
  panel.addEventListener("click", (e) => { const b = e.target.closest(".cr-color[data-valor]"); if (b) cambiar(b.closest("[data-campo]").dataset.campo, b.dataset.valor); });
  panel.addEventListener("input", (e) => {
    const t = e.target, campo = t.closest("[data-campo]").dataset.campo, sec = SECCIONES[campo];
    if (t.type === "range") cambiar(campo, sec.invertir ? +sec.min + +sec.max - +t.value : +t.value);
    else if (t.type === "color") cambiar(campo, t.value.toLowerCase());
  });
  raiz.addEventListener("click", (e) => {
    const a = e.target.closest("[data-accion]"); if (!a) return;
    ({ aleatorio, deshacer, guardar, reiniciar() { aplicar(Object.assign({}, guardada), "*reiniciar"); mensaje(""); },
       vista() { vistaManual = (vistaManual || categoria.vista) === "completo" ? "retrato" : "completo"; control.vista(vistaManual); actualizarBotonVista(); } })[a.dataset.accion]();
  });
  window.addEventListener("beforeunload", (e) => { if (sucio) { e.preventDefault(); e.returnValue = ""; } });

  dibujarCategorias();
  elegirCategoria(categoria.id);
})();
