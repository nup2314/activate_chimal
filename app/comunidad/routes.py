"""Novedades deportivas y clasificación de participantes (Funciones 12 y 13)."""
from flask import Blueprint, abort, render_template, request

from .. import catalogo, servicios
from ..models import Novedad
from ..utils import login_requerido, usuario_actual

comunidad = Blueprint("comunidad", __name__)

TOP = 20


@comunidad.route("/novedades")
@login_requerido
def novedades():
    tipo = request.args.get("tipo", "")
    q = Novedad.query.filter_by(estado="publicada")
    if tipo in catalogo.TIPOS_NOVEDAD:
        q = q.filter_by(tipo=tipo)
    else:
        tipo = ""
    lista = q.order_by(Novedad.fecha_publicacion.desc()).limit(60).all()
    return render_template("comunidad/novedades.html", novedades=lista, tipo=tipo)


@comunidad.route("/novedades/<int:novedad_id>")
@login_requerido
def novedad(novedad_id):
    n = Novedad.query.filter_by(id=novedad_id, estado="publicada").first()
    if n is None:
        abort(404)
    return render_template("comunidad/novedad.html", n=n)


@comunidad.route("/clasificacion")
@login_requerido
def clasificacion():
    usuario = usuario_actual()
    periodo = "total" if request.args.get("periodo") == "total" else "semana"
    filas = servicios.clasificacion(periodo)
    mia = next((f for f in filas if f["usuario"].id == usuario.id), None)
    visibles = [f for f in filas[:TOP] if f["puntos"] > 0 or f["usuario"].id == usuario.id]
    return render_template("comunidad/clasificacion.html", filas=visibles, mia=mia, periodo=periodo,
                           fuera_del_top=bool(mia and mia not in visibles), total=len(filas))
