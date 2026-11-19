"""Creador de personajes (Función 14). La configuración se guarda completa en la base de datos."""
from flask import Blueprint, flash, jsonify, redirect, render_template, request, url_for

from .. import avatar_config
from ..extensions import db
from ..models import Avatar
from ..utils import login_requerido, usuario_actual

avatar = Blueprint("avatar", __name__, url_prefix="/avatar")


@avatar.route("/", methods=["GET", "POST"])
@login_requerido
def editor():
    usuario = usuario_actual()
    if request.method == "POST":
        datos = avatar_config.normalizar(request.form.get("config", ""))   # se valida todo en el servidor
        if usuario.avatar is None:
            usuario.avatar = Avatar(datos=datos)
        else:
            usuario.avatar.datos = datos
        db.session.commit()
        if request.headers.get("X-Requested-With") == "fetch":              # guardado sin recargar
            return jsonify(ok=True)
        flash("Avatar guardado.", "ok")
        return redirect(url_for("avatar.editor"))
    return render_template("avatar/editor.html", config=avatar_config.config_de(usuario.avatar),
                           esquema=avatar_config.ESQUEMA)
