"""Deportes, objetivos, reto diario, mi rutina, pasos y registro de actividades (Funciones 5-9)."""
from datetime import datetime, time, timedelta

from flask import Blueprint, abort, current_app, flash, jsonify, redirect, render_template, request, url_for

from .. import catalogo, servicios, tiempo
from ..extensions import db
from ..models import Actividad, DeporteFavorito
from ..utils import a_decimal, a_entero, destino_seguro, login_requerido, usuario_actual

actividad = Blueprint("actividad", __name__)


# ───────────────────────── Función 5: deportes ─────────────────────────
def _favoritos(usuario_id: int) -> set:
    return {f.deporte for f in DeporteFavorito.query.filter_by(usuario_id=usuario_id)}


@actividad.route("/deportes")
@login_requerido
def deportes():
    usuario = usuario_actual()
    favoritos = _favoritos(usuario.id)
    solo_favoritos = request.args.get("ver") == "favoritos"
    lista = [(k, d) for k, d in catalogo.DEPORTES.items() if not solo_favoritos or k in favoritos]
    lista.sort(key=lambda par: par[0] not in favoritos)        # los favoritos van primero
    return render_template("actividad/deportes.html", deportes=lista, favoritos=favoritos,
                           solo_favoritos=solo_favoritos)


@actividad.route("/deportes/<clave>/favorito", methods=["POST"])
@login_requerido
def favorito(clave):
    """Marca o desmarca un deporte como favorito."""
    usuario = usuario_actual()
    if clave not in catalogo.DEPORTES:
        abort(404)
    fila = DeporteFavorito.query.filter_by(usuario_id=usuario.id, deporte=clave).first()
    nombre = catalogo.DEPORTES[clave]["nombre"]
    desde_js = request.headers.get("X-Requested-With") == "fetch"
    if fila:
        db.session.delete(fila)
        if not desde_js:
            flash(f"{nombre} ya no está en tus favoritos.", "ok")
    else:
        db.session.add(DeporteFavorito(usuario_id=usuario.id, deporte=clave))
        if not desde_js:
            flash(f"{nombre} se agregó a tus favoritos.", "ok")
    db.session.commit()
    if desde_js:
        total = DeporteFavorito.query.filter_by(usuario_id=usuario.id).count()
        return jsonify(favorito=fila is None, total=total)
    return redirect(destino_seguro(request.form.get("volver")) or url_for("actividad.deportes"))


@actividad.route("/deportes/<clave>")
@login_requerido
def deporte(clave):
    datos = catalogo.DEPORTES.get(clave)
    if datos is None:
        abort(404)
    es_favorito = DeporteFavorito.query.filter_by(usuario_id=usuario_actual().id, deporte=clave).first() is not None
    return render_template("actividad/deporte.html", d=datos, clave=clave, es_favorito=es_favorito)


# ───────────────────────── Función 6: objetivos ─────────────────────────
@actividad.route("/objetivos", methods=["GET", "POST"])
@login_requerido
def objetivos():
    usuario = usuario_actual()
    if request.method == "POST":
        elegido = request.form.get("objetivo", "")
        if elegido not in catalogo.OBJETIVOS:
            flash("Elige uno de los tres objetivos.", "error")
        else:
            usuario.objetivo = elegido
            db.session.commit()
            flash(f"Objetivo guardado: {catalogo.OBJETIVOS[elegido]['nombre']}.", "ok")
            return redirect(url_for("actividad.reto"))
    return render_template("actividad/objetivos.html", primera_vez=not usuario.objetivo)


@actividad.route("/objetivos/<clave>")
@login_requerido
def objetivo(clave):
    """Lista de ejercicios de un objetivo organizada por los 7 grupos de edad."""
    usuario = usuario_actual()
    if clave not in catalogo.OBJETIVOS:
        abort(404)
    return render_template("actividad/objetivo.html", clave=clave, obj=catalogo.OBJETIVOS[clave],
                           grupos=catalogo.rutinas_por_grupo(clave, usuario.frecuencia),
                           mi_grupo=catalogo.indice_grupo_edad(usuario.edad), texto_meta=catalogo.texto_meta)


# ───────────────────────── Función 7: reto diario ─────────────────────────
@actividad.route("/reto")
@login_requerido
def reto():
    usuario = usuario_actual()
    if not usuario.objetivo:
        flash("Primero elige tu objetivo para armar tu reto.", "info")
        return redirect(url_for("actividad.objetivos"))
    return render_template("actividad/reto.html", reto=servicios.reto_del_dia(usuario),
                           unidades=catalogo.UNIDADES)


@actividad.route("/reto/progreso", methods=["POST"])
@login_requerido
def reto_progreso():
    usuario = usuario_actual()
    clave = request.form.get("ejercicio", "")
    rapido = a_entero(request.form.get("rapido"), 1, 999)       # botones +5, +10…
    accion = request.form.get("accion") or "sumar"
    cantidad = rapido or a_entero(request.form.get("cantidad", "0"), 0, 999) or 0
    if accion in ("sumar", "restar") and cantidad <= 0:
        flash("Escribe cuántas repeticiones quieres sumar.", "error")
    elif not servicios.cambiar_progreso(usuario, clave, accion, cantidad):
        flash("No se pudo guardar ese avance.", "error")
    elif accion == "sumar":
        reto = servicios.reto_del_dia(usuario)
        flash("¡Reto completado al 100 %! 🎉" if reto["completo"] else "Avance guardado.", "ok")
    return redirect(url_for("actividad.reto") + f"#e-{clave}")


@actividad.route("/mi-rutina")
@login_requerido
def mi_rutina():
    usuario = usuario_actual()
    if not usuario.objetivo:
        return redirect(url_for("actividad.objetivos"))
    idx = catalogo.indice_grupo_edad(usuario.edad)
    return render_template("actividad/rutina.html", obj=catalogo.OBJETIVOS[usuario.objetivo],
                           grupo=catalogo.GRUPOS_EDAD[idx],
                           ejercicios=catalogo.rutina(usuario.objetivo, idx, usuario.frecuencia),
                           frecuencia=catalogo.FRECUENCIAS[usuario.frecuencia],
                           texto_meta=catalogo.texto_meta)


# ───────────────────────── Función 9: pasos ─────────────────────────
@actividad.route("/pasos", methods=["GET", "POST"])
@login_requerido
def pasos():
    usuario = usuario_actual()
    if request.method == "POST":
        cantidad = a_entero(request.form.get("cantidad"), 0, 100000)
        modo = "fijar" if request.form.get("modo") == "fijar" else "sumar"
        if cantidad is None or (modo == "sumar" and cantidad == 0):
            flash("Escribe un número de pasos entre 1 y 100,000.", "error")
        else:
            total = servicios.guardar_pasos(usuario.id, cantidad, modo)
            meta = current_app.config["META_PASOS"]
            flash("¡Meta de pasos lograda! 👟" if total >= meta else "Pasos guardados.", "ok")
            return redirect(url_for("actividad.pasos"))
    return render_template("actividad/pasos.html", hoy_pasos=servicios.pasos_de(usuario.id),
                           semana=servicios.serie_semana(usuario.id))


# ───────────────────────── Función 8: registrar actividades ─────────────────────────
@actividad.route("/actividades/nueva", methods=["GET", "POST"])
@login_requerido
def registrar():
    usuario = usuario_actual()
    hoy = tiempo.hoy()
    datos = {"tipo": request.args.get("tipo", ""), "fecha": hoy.isoformat(), "esfuerzo": "medio"}
    if request.method == "POST":
        datos = {k: request.form.get(k, "").strip() for k in
                 ("tipo", "tiempo", "distancia", "fecha", "esfuerzo", "notas")}
        minutos = a_entero(datos["tiempo"], 1, 1440)
        dist_txt = datos["distancia"]
        distancia = a_decimal(dist_txt, 0, 1000) if dist_txt else None
        try:
            dia = datetime.strptime(datos["fecha"], "%Y-%m-%d").date()
        except ValueError:
            dia = None

        error = None
        if datos["tipo"] not in catalogo.TIPOS_ACTIVIDAD:
            error = "Elige el tipo de actividad."
        elif minutos is None:
            error = "La duración debe ser de 1 a 1,440 minutos."
        elif dist_txt and distancia is None:
            error = "La distancia debe ser un número positivo en kilómetros."
        elif dia is None or dia > hoy or dia < hoy - timedelta(days=60):
            error = "La fecha debe ser de hoy o de los últimos 60 días."
        elif datos["esfuerzo"] not in catalogo.ESFUERZOS:
            error = "Elige el nivel de esfuerzo."
        elif len(datos["notas"]) > 200:
            error = "Las notas pueden tener máximo 200 caracteres."

        if error:
            flash(error, "error")
        else:
            ahora = tiempo.ahora()
            momento = ahora if dia == hoy else datetime.combine(dia, time(12, 0))
            db.session.add(Actividad(
                usuario_id=usuario.id, actividad=datos["tipo"], tiempo=minutos, distancia=distancia,
                calorias=catalogo.calorias_estimadas(datos["tipo"], minutos, usuario.peso, datos["esfuerzo"]),
                esfuerzo=datos["esfuerzo"], notas=datos["notas"] or None, fecha=momento))
            db.session.commit()
            flash("Actividad registrada.", "ok")
            return redirect(url_for("seguimiento.historial"))
    return render_template("actividad/registrar.html", datos=datos, tipos=catalogo.TIPOS_ACTIVIDAD,
                           esfuerzos=catalogo.ESFUERZOS, minimo=(hoy - timedelta(days=60)).isoformat())


@actividad.route("/actividades/<int:actividad_id>/eliminar", methods=["POST"])
@login_requerido
def eliminar(actividad_id):
    usuario = usuario_actual()
    fila = db.session.get(Actividad, actividad_id)
    if fila is None or fila.usuario_id != usuario.id:
        abort(404)
    db.session.delete(fila)
    db.session.commit()
    flash("Actividad eliminada.", "ok")
    return redirect(url_for("seguimiento.historial"))
