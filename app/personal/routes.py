"""Módulo de personal: acceso, novedades deportivas y mensajes (Funciones 19-21)."""
import time as reloj
from datetime import datetime

from flask import (Blueprint, abort, flash, redirect, render_template, request,
                   session, url_for)

from .. import catalogo, tiempo
from ..extensions import db
from ..models import Mensaje, Novedad, Personal, Usuario
from ..utils import personal_actual, personal_requerido

personal = Blueprint("personal", __name__, url_prefix="/personal")

# Límite de intentos de acceso en memoria (se reinicia al reiniciar el servidor).
_FALLOS: dict[str, list[float]] = {}
_MAX_FALLOS, _VENTANA = 5, 15 * 60


def _bloqueado(clave: str) -> bool:
    ahora = reloj.time()
    recientes = [t for t in _FALLOS.get(clave, []) if ahora - t < _VENTANA]
    _FALLOS[clave] = recientes
    return len(recientes) >= _MAX_FALLOS


# ───────────────────────── Función 19: acceso exclusivo ─────────────────────────
@personal.route("/acceso", methods=["GET", "POST"])
def acceso():
    if personal_actual():
        return redirect(url_for("personal.panel"))
    if request.method == "POST":
        usuario = request.form.get("usuario", "").strip().lower()
        clave_ip = f"{request.remote_addr}|{usuario}"
        if _bloqueado(clave_ip):
            flash("Demasiados intentos. Espera 15 minutos.", "error")
        else:
            persona = Personal.query.filter_by(usuario=usuario).first()
            if persona and persona.activo and persona.revisar_contrasena(request.form.get("contrasena", "")):
                _FALLOS.pop(clave_ip, None)
                usuario_id = session.get("usuario_id")
                session.clear()
                if usuario_id:
                    session["usuario_id"] = usuario_id
                session["personal_id"] = persona.id
                session.permanent = True
                return redirect(url_for("personal.panel"))
            _FALLOS.setdefault(clave_ip, []).append(reloj.time())
            flash("Usuario o contraseña incorrectos.", "error")
    return render_template("personal/acceso.html")


@personal.route("/salir", methods=["POST"])
def salir():
    session.pop("personal_id", None)
    flash("Saliste del módulo de personal.", "ok")
    return redirect(url_for("personal.acceso"))


@personal.route("/")
@personal_requerido
def panel():
    conteo = {e: Novedad.query.filter_by(estado=e).count() for e in catalogo.ESTADOS_NOVEDAD}
    return render_template("personal/panel.html", conteo=conteo,
                           sin_leer=Mensaje.query.filter_by(leido=False).count(),
                           usuarios=Usuario.query.count(),
                           recientes=Novedad.query.order_by(Novedad.actualizado_en.desc()).limit(5).all())


# ───────────────────────── Funciones 20 y 21: novedades ─────────────────────────
@personal.route("/novedades")
@personal_requerido
def novedades():
    estado = request.args.get("estado", "")
    tipo = request.args.get("tipo", "")
    q = Novedad.query
    if estado in catalogo.ESTADOS_NOVEDAD:
        q = q.filter_by(estado=estado)
    else:
        estado = ""
    if tipo in catalogo.TIPOS_NOVEDAD:
        q = q.filter_by(tipo=tipo)
    else:
        tipo = ""
    lista = q.order_by(Novedad.actualizado_en.desc()).all()
    return render_template("personal/novedades.html", novedades=lista, estado=estado, tipo=tipo,
                           estados=catalogo.ESTADOS_NOVEDAD)


def _leer_formulario():
    f = request.form
    datos = {k: f.get(k, "").strip() for k in ("titulo", "descripcion", "tipo", "lugar", "estado", "fecha_evento")}
    fecha_evento = None
    if datos["fecha_evento"]:
        try:
            fecha_evento = datetime.strptime(datos["fecha_evento"], "%Y-%m-%dT%H:%M")
        except ValueError:
            return datos, None, "La fecha del evento no es válida."
    if not (3 <= len(datos["titulo"]) <= 150):
        return datos, fecha_evento, "El título debe tener entre 3 y 150 caracteres."
    if not (10 <= len(datos["descripcion"]) <= 5000):
        return datos, fecha_evento, "La descripción debe tener entre 10 y 5,000 caracteres."
    if datos["tipo"] not in catalogo.TIPOS_NOVEDAD:
        return datos, fecha_evento, "Elige el tipo de novedad."
    if datos["estado"] not in catalogo.ESTADOS_NOVEDAD:
        return datos, fecha_evento, "Elige el estado."
    if len(datos["lugar"]) > 150:
        return datos, fecha_evento, "El lugar es demasiado largo (máximo 150 caracteres)."
    return datos, fecha_evento, None


@personal.route("/novedades/nueva", methods=["GET", "POST"])
@personal_requerido
def nueva():
    datos = {"estado": "publicada"}
    if request.method == "POST":
        datos, fecha_evento, error = _leer_formulario()
        if error:
            flash(error, "error")
        else:
            db.session.add(Novedad(titulo=datos["titulo"], descripcion=datos["descripcion"], tipo=datos["tipo"],
                                   lugar=datos["lugar"] or None, estado=datos["estado"], fecha_evento=fecha_evento,
                                   autor_id=personal_actual().id))
            db.session.commit()
            flash("Novedad creada.", "ok")
            return redirect(url_for("personal.novedades"))
    return render_template("personal/novedad_form.html", n=None, datos=datos,
                           estados=catalogo.ESTADOS_NOVEDAD, tipos=catalogo.TIPOS_NOVEDAD)


@personal.route("/novedades/<int:novedad_id>/editar", methods=["GET", "POST"])
@personal_requerido
def editar(novedad_id):
    n = db.session.get(Novedad, novedad_id) or abort(404)
    datos = {"titulo": n.titulo, "descripcion": n.descripcion, "tipo": n.tipo, "lugar": n.lugar or "",
             "estado": n.estado,
             "fecha_evento": n.fecha_evento.strftime("%Y-%m-%dT%H:%M") if n.fecha_evento else ""}
    if request.method == "POST":
        datos, fecha_evento, error = _leer_formulario()
        if error:
            flash(error, "error")
        else:
            n.titulo, n.descripcion, n.tipo = datos["titulo"], datos["descripcion"], datos["tipo"]
            n.lugar, n.estado, n.fecha_evento = datos["lugar"] or None, datos["estado"], fecha_evento
            db.session.commit()
            flash("Cambios guardados.", "ok")
            return redirect(url_for("personal.novedades"))
    return render_template("personal/novedad_form.html", n=n, datos=datos,
                           estados=catalogo.ESTADOS_NOVEDAD, tipos=catalogo.TIPOS_NOVEDAD)


@personal.route("/novedades/<int:novedad_id>/estado", methods=["POST"])
@personal_requerido
def cambiar_estado(novedad_id):
    n = db.session.get(Novedad, novedad_id) or abort(404)
    nuevo = request.form.get("estado", "")
    if nuevo not in catalogo.ESTADOS_NOVEDAD:
        abort(400)
    n.estado = nuevo
    if nuevo == "publicada":
        n.fecha_publicacion = tiempo.ahora()
    db.session.commit()
    flash(f"«{n.titulo}» ahora está {catalogo.ESTADOS_NOVEDAD[nuevo].lower()}.", "ok")
    return redirect(request.referrer or url_for("personal.novedades"))


@personal.route("/novedades/<int:novedad_id>/eliminar", methods=["POST"])
@personal_requerido
def eliminar(novedad_id):
    n = db.session.get(Novedad, novedad_id) or abort(404)
    db.session.delete(n)
    db.session.commit()
    flash("Novedad eliminada definitivamente.", "ok")
    return redirect(url_for("personal.novedades"))


# ───────────────────────── Mensajes del formulario de contacto ─────────────────────────
@personal.route("/mensajes")
@personal_requerido
def mensajes():
    lista = Mensaje.query.order_by(Mensaje.leido, Mensaje.creado_en.desc()).limit(100).all()
    return render_template("personal/mensajes.html", mensajes=lista)


@personal.route("/mensajes/<int:mensaje_id>/leido", methods=["POST"])
@personal_requerido
def marcar_leido(mensaje_id):
    m = db.session.get(Mensaje, mensaje_id) or abort(404)
    m.leido = not m.leido
    db.session.commit()
    return redirect(url_for("personal.mensajes"))


@personal.route("/mensajes/<int:mensaje_id>/eliminar", methods=["POST"])
@personal_requerido
def eliminar_mensaje(mensaje_id):
    m = db.session.get(Mensaje, mensaje_id) or abort(404)
    db.session.delete(m)
    db.session.commit()
    flash("Mensaje eliminado.", "ok")
    return redirect(url_for("personal.mensajes"))
