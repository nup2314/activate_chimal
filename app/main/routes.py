from flask import Blueprint, redirect, render_template, url_for

from .. import catalogo, servicios, tiempo
from ..models import DeporteFavorito, Novedad
from ..utils import usuario_actual

main = Blueprint("main", __name__)


@main.route("/")
def inicio():
    usuario = usuario_actual()
    if usuario is None:
        return render_template("publico/portada.html")
    if not usuario.objetivo:
        return redirect(url_for("actividad.objetivos"))

    reto = servicios.reto_del_dia(usuario)
    pasos = servicios.pasos_de(usuario.id)
    racha, _mejor = servicios.calcular_rachas(servicios.dias_activos(usuario.id), tiempo.hoy())
    novedades = (Novedad.query.filter_by(estado="publicada")
                 .order_by(Novedad.fecha_publicacion.desc()).limit(2).all())
    favoritos = [f.deporte for f in DeporteFavorito.query.filter_by(usuario_id=usuario.id)
                 if f.deporte in catalogo.DEPORTES]
    return render_template("inicio.html", reto=reto, pasos=pasos, racha=racha, novedades=novedades,
                           deportes=catalogo.DEPORTES, favoritos=favoritos)
