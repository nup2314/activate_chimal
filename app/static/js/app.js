/* Activate + Chimal · comportamiento del navegador (todo es opcional: la app funciona sin JS) */
(function () {
  "use strict";

  // ── Menú hamburguesa ──
  var abrir = document.getElementById("abrir-menu");
  var menu = document.getElementById("menu-lateral");
  var velo = document.getElementById("velo");
  if (abrir && menu && velo) {
    var cerrar = document.getElementById("cerrar-menu");
    var mostrar = function (v) {
      menu.hidden = !v; velo.hidden = !v;
      abrir.setAttribute("aria-expanded", v ? "true" : "false");
      document.body.style.overflow = v ? "hidden" : "";
      if (v) { cerrar.focus(); } else { abrir.focus(); }
    };
    abrir.addEventListener("click", function () { mostrar(true); });
    cerrar.addEventListener("click", function () { mostrar(false); });
    velo.addEventListener("click", function () { mostrar(false); });
    document.addEventListener("keydown", function (e) { if (e.key === "Escape" && !menu.hidden) { mostrar(false); } });
  }

  // ── Confirmaciones (formularios con data-confirmar) ──
  document.addEventListener("submit", function (e) {
    var msg = e.target.getAttribute && e.target.getAttribute("data-confirmar");
    if (msg && !window.confirm(msg)) { e.preventDefault(); }
  });

  // ── Pestañas (grupos de edad) ──
  document.querySelectorAll(".tabs").forEach(function (lista) {
    var tabs = Array.prototype.slice.call(lista.querySelectorAll('[role="tab"]'));
    function elegir(tab) {
      tabs.forEach(function (t) {
        var activa = t === tab;
        t.setAttribute("aria-selected", activa ? "true" : "false");
        t.tabIndex = activa ? 0 : -1;
        var panel = document.getElementById(t.getAttribute("aria-controls"));
        if (panel) { panel.hidden = !activa; }
      });
    }
    tabs.forEach(function (t, i) {
      t.tabIndex = t.getAttribute("aria-selected") === "true" ? 0 : -1;
      t.addEventListener("click", function () { elegir(t); });
      t.addEventListener("keydown", function (e) {
        var j = e.key === "ArrowRight" ? i + 1 : e.key === "ArrowLeft" ? i - 1 : null;
        if (j === null) { return; }
        var sig = tabs[(j + tabs.length) % tabs.length];
        elegir(sig); sig.focus(); e.preventDefault();
      });
    });
    var activa = tabs.filter(function (t) { return t.getAttribute("aria-selected") === "true"; })[0];
    if (activa && activa.scrollIntoView) { activa.scrollIntoView({ block: "nearest", inline: "center" }); }
  });

  // ── Vista previa del avatar (el servidor dibuja el SVG) ──
  var editor = document.getElementById("editor-avatar");
  if (editor) {
    var vista = document.getElementById("avatar-vista");
    var url = editor.getAttribute("data-vista");
    var espera = null;
    editor.addEventListener("change", function () {
      clearTimeout(espera);
      espera = setTimeout(function () {
        var datos = new URLSearchParams(new FormData(editor));
        datos.delete("csrf_token");
        fetch(url + "?" + datos.toString(), { credentials: "same-origin" })
          .then(function (r) { return r.ok ? r.text() : Promise.reject(); })
          .then(function (svg) { vista.innerHTML = svg; })
          .catch(function () { /* se mantiene la vista anterior */ });
      }, 60);
    });
  }

  // ── Contador de pasos con el acelerómetro (beta) ──
  var panel = document.getElementById("contador");
  if (panel && "DeviceMotionEvent" in window) {
    panel.hidden = false;
    var num = document.getElementById("contador-num");
    var valor = document.getElementById("contador-valor");
    var iniciar = document.getElementById("contador-iniciar");
    var parar = document.getElementById("contador-parar");
    var guardar = document.getElementById("contador-guardar");
    var pasos = 0, ultimo = 0, filtrado = 9.8, activo = false;
    var UMBRAL = 1.6, INTERVALO = 320;   // m/s² por encima del promedio · ms mínimos entre pasos

    function movimiento(e) {
      var a = e.accelerationIncludingGravity;
      if (!a || a.x === null) { return; }
      var mag = Math.sqrt(a.x * a.x + a.y * a.y + a.z * a.z);
      filtrado = filtrado * 0.9 + mag * 0.1;                  // promedio móvil (gravedad)
      var ahora = Date.now();
      if (mag - filtrado > UMBRAL && ahora - ultimo > INTERVALO) {
        ultimo = ahora; pasos += 1;
        num.textContent = pasos; valor.value = pasos; guardar.disabled = false;
      }
    }
    function empezar() {
      window.addEventListener("devicemotion", movimiento);
      activo = true; iniciar.hidden = true; parar.hidden = false;
    }
    iniciar.addEventListener("click", function () {
      if (typeof DeviceMotionEvent.requestPermission === "function") {   // iOS pide permiso
        DeviceMotionEvent.requestPermission().then(function (r) { if (r === "granted") { empezar(); } });
      } else { empezar(); }
    });
    parar.addEventListener("click", function () {
      window.removeEventListener("devicemotion", movimiento);
      activo = false; parar.hidden = true; iniciar.hidden = false;
    });
  }
})();

/* ───────── Animaciones al tocar y al cargar ───────── */
(function () {
  "use strict";
  var sinMovimiento = window.matchMedia && window.matchMedia("(prefers-reduced-motion: reduce)").matches;

  // ── Onda al tocar ──
  var OBJETIVOS_ONDA = ".btn, .barra-inferior a, .atajos a, .tarjeta--enlace, .lista-item, .tab, .subnav a, .menu-lateral a";
  document.addEventListener("pointerdown", function (e) {
    if (sinMovimiento) { return; }
    var el = e.target.closest && e.target.closest(OBJETIVOS_ONDA);
    if (!el || el.disabled || el.classList.contains("cargando")) { return; }
    var r = el.getBoundingClientRect();
    var d = Math.max(r.width, r.height) * 2;
    var onda = document.createElement("i");
    onda.className = "onda";
    onda.style.cssText = "width:" + d + "px;height:" + d + "px;left:" + (e.clientX - r.left - d / 2) + "px;top:" + (e.clientY - r.top - d / 2) + "px";
    el.appendChild(onda);
    setTimeout(function () { if (onda.parentNode) { onda.parentNode.removeChild(onda); } }, 650);
  }, { passive: true });

  // ── Botón "enviando…" (no se desactiva para no perder el valor del botón pulsado) ──
  document.addEventListener("submit", function (e) {
    if (e.defaultPrevented) { return; }
    var boton = e.submitter || e.target.querySelector('button[type="submit"], button:not([type])');
    if (boton && boton.classList.contains("btn")) { boton.classList.add("cargando"); }
  });
  window.addEventListener("pageshow", function () {
    document.querySelectorAll(".btn.cargando").forEach(function (b) { b.classList.remove("cargando"); });
  });

  // ── Estrella de favorito sin recargar la página ──
  document.querySelectorAll(".favorito-form").forEach(function (form) {
    form.addEventListener("submit", function (e) {
      if (!window.fetch) { return; }
      e.preventDefault();
      var boton = form.querySelector(".favorito");
      fetch(form.action, { method: "POST", body: new FormData(form), credentials: "same-origin", headers: { "X-Requested-With": "fetch" } })
        .then(function (r) { return r.ok ? r.json() : Promise.reject(); })
        .then(function (d) {
          boton.classList.toggle("favorito--si", d.favorito);
          boton.setAttribute("aria-pressed", d.favorito ? "true" : "false");
          var nombre = boton.getAttribute("data-nombre") || "";
          boton.setAttribute("aria-label", (d.favorito ? "Quitar " + nombre + " de favoritos" : "Agregar " + nombre + " a favoritos"));
          boton.classList.remove("pop"); void boton.offsetWidth; boton.classList.add("pop");
          document.querySelectorAll("[data-total-favoritos]").forEach(function (n) { n.textContent = d.total; });
          var celda = form.closest(".deporte-celda");
          if (!d.favorito && celda && celda.parentNode.hasAttribute("data-solo-favoritos")) {
            celda.classList.add("saliendo");
            setTimeout(function () { if (celda.parentNode) { celda.parentNode.removeChild(celda); } }, 320);
          }
        })
        .catch(function () { form.submit(); });
    });
  });

  // ── Números que suben ──
  function contar(el) {
    var nodo = Array.prototype.filter.call(el.childNodes, function (n) { return n.nodeType === 3 && /\d/.test(n.nodeValue); })[0];
    if (!nodo) { return; }
    var texto = nodo.nodeValue.trim();
    if (!/^[\d,]+(\.\d+)?$/.test(texto)) { return; }
    var decimales = (texto.split(".")[1] || "").length;
    var fin = parseFloat(texto.replace(/,/g, ""));
    if (!isFinite(fin) || fin === 0) { return; }
    var inicio = null, dur = 750;
    function paso(t) {
      if (inicio === null) { inicio = t; }
      var p = Math.min(1, (t - inicio) / dur), v = fin * (1 - Math.pow(1 - p, 3));
      nodo.nodeValue = v.toLocaleString("en-US", { minimumFractionDigits: decimales, maximumFractionDigits: decimales });
      if (p < 1) { requestAnimationFrame(paso); }
    }
    nodo.nodeValue = (0).toFixed(decimales);
    requestAnimationFrame(paso);
  }
  if (!sinMovimiento) {
    var cifras = document.querySelectorAll(".cifras strong, .cifra-grande, .anillo-texto strong, .racha-num strong, .ejercicio-cifra strong");
    if ("IntersectionObserver" in window) {
      var obs = new IntersectionObserver(function (entradas) {
        entradas.forEach(function (en) { if (en.isIntersecting) { obs.unobserve(en.target); contar(en.target); } });
      }, { threshold: 0.4 });
      cifras.forEach(function (c) { obs.observe(c); });
    } else { cifras.forEach(contar); }
  }

  // ── Mascota: salta al tocarla ──
  document.addEventListener("click", function (e) {
    var img = e.target.closest && e.target.closest(".mascota-img");
    if (!img) { return; }
    img.classList.remove("salta"); void img.offsetWidth; img.classList.add("salta");
  });

  // ── Confeti cuando se completa el reto o la meta de pasos ──
  function confeti() {
    var caja = document.createElement("div");
    caja.className = "confeti"; caja.setAttribute("aria-hidden", "true");
    var colores = ["#FFC93C", "#3DDC97", "#5FE0E0", "#E2563B", "#7C9BFF", "#FFA85C", "#C39BFF"];
    for (var i = 0; i < 46; i++) {
      var p = document.createElement("i");
      p.style.left = (Math.random() * 100) + "%";
      p.style.background = colores[i % colores.length];
      p.style.setProperty("--dx", (Math.random() * 160 - 80) + "px");
      p.style.setProperty("--giro", (Math.random() * 900 - 300) + "deg");
      p.style.setProperty("--dur", (1.8 + Math.random() * 1.2) + "s");
      p.style.setProperty("--ret", (Math.random() * 0.4) + "s");
      caja.appendChild(p);
    }
    document.body.appendChild(caja);
    setTimeout(function () { if (caja.parentNode) { caja.parentNode.removeChild(caja); } }, 3600);
  }
  if (!sinMovimiento && document.querySelector("[data-celebrar]")) {
    setTimeout(confeti, 250);
    var m = document.querySelector(".mascota-img");
    if (m) { setTimeout(function () { m.classList.add("salta"); }, 400); }
  }
})();
