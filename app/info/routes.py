"""Prevención de adicciones, contacto y tutorial (Funciones 15-17)."""
from flask import Blueprint, flash, redirect, render_template, request, url_for

from .. import catalogo
from ..extensions import db
from ..models import Mensaje
from ..utils import correo_valido, login_requerido, usuario_actual

info = Blueprint("info", __name__)


@info.route("/prevencion")
@login_requerido
def prevencion():
    return render_template("info/prevencion.html", temas=catalogo.PREVENCION,
                           formas=catalogo.FORMAS_DE_DECIR_NO, ayuda=catalogo.AYUDA_MEXICO)


@info.route("/alimentacion")
@login_requerido
def alimentacion():
    usuario = usuario_actual()
    datos = catalogo.ALIMENTACION
    grupo = request.args.get("grupo", "")
    if grupo not in datos["grupos"]:
        grupo = ""
    alimentos = [a for a in datos["alimentos"] if not grupo or a["grupo"] == grupo]
    clave = usuario.objetivo if usuario.objetivo in datos["objetivos"] else "mantenerse_activo"
    return render_template("info/alimentacion.html", datos=datos, grupo=grupo, alimentos=alimentos,
                           clave=clave, consejos=datos["objetivos"][clave],
                           menor_de_edad=bool(usuario.edad and usuario.edad < 18))


@info.route("/contacto", methods=["GET", "POST"])
@login_requerido
def contacto():
    usuario = usuario_actual()
    datos = {"nombre": f"{usuario.nombre} {usuario.apellidos}".strip(), "correo": usuario.correo,
             "asunto": "", "mensaje": ""}
    if request.method == "POST":
        datos = {k: request.form.get(k, "").strip() for k in ("nombre", "correo", "asunto", "mensaje")}
        if not (2 <= len(datos["nombre"]) <= 100):
            error = "Escribe tu nombre."
        elif not correo_valido(datos["correo"]):
            error = "Escribe un correo válido para poder responderte."
        elif not (3 <= len(datos["asunto"]) <= 150):
            error = "El asunto debe tener entre 3 y 150 caracteres."
        elif not (10 <= len(datos["mensaje"]) <= 3000):
            error = "El mensaje debe tener entre 10 y 3,000 caracteres."
        else:
            error = None
        if error:
            flash(error, "error")
        else:
            db.session.add(Mensaje(usuario_id=usuario.id, **datos))
            db.session.commit()
            flash("Mensaje enviado. Te responderemos al correo que indicaste.", "ok")
            return redirect(url_for("info.contacto"))
    return render_template("info/contacto.html", datos=datos)


@info.route("/tutorial")
@login_requerido
def tutorial():
    return render_template("info/tutorial.html", pasos=catalogo.PASOS_TUTORIAL)
