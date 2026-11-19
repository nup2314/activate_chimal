"""Consultar y editar perfil, o eliminar la cuenta (Función 4)."""
from flask import Blueprint, current_app, flash, redirect, render_template, request, session, url_for

from .. import catalogo
from ..extensions import db
from ..models import Usuario
from ..utils import (a_decimal, a_entero, correo_valido, errores_contrasena, login_requerido,
                     usuario_actual)

perfil = Blueprint("perfil", __name__, url_prefix="/perfil")


@perfil.route("/")
@login_requerido
def ver():
    usuario = usuario_actual()
    idx = catalogo.indice_grupo_edad(usuario.edad)
    return render_template("perfil/ver.html", grupo=catalogo.GRUPOS_EDAD[idx],
                           frecuencias=catalogo.FRECUENCIAS)


@perfil.route("/editar", methods=["GET", "POST"])
@login_requerido
def editar():
    usuario = usuario_actual()
    cfg = current_app.config
    if request.method == "POST":
        nombre = request.form.get("nombre", "").strip()
        apellidos = request.form.get("apellidos", "").strip()
        correo = request.form.get("correo", "").strip().lower()
        edad = a_entero(request.form.get("edad"), cfg["EDAD_MINIMA"], cfg["EDAD_MAXIMA"])
        peso_txt = request.form.get("peso", "").strip()
        est_txt = request.form.get("estatura", "").strip()
        peso = a_decimal(peso_txt, 20, 300) if peso_txt else None
        estatura = a_decimal(est_txt, 80, 250) if est_txt else None
        frecuencia = request.form.get("frecuencia", "")
        nueva = request.form.get("contrasena", "")

        error = None
        if not (2 <= len(nombre) <= 100):
            error = "Escribe tu nombre (entre 2 y 100 caracteres)."
        elif not correo_valido(correo):
            error = "Escribe un correo válido."
        elif edad is None:
            error = f"Tu edad debe estar entre {cfg['EDAD_MINIMA']} y {cfg['EDAD_MAXIMA']} años."
        elif peso_txt and peso is None:
            error = "El peso debe estar entre 20 y 300 kg."
        elif est_txt and estatura is None:
            error = "La estatura debe estar entre 80 y 250 cm."
        elif frecuencia not in catalogo.FRECUENCIAS:
            error = "Indica con qué frecuencia haces ejercicio."
        elif nueva:
            error = errores_contrasena(nueva, request.form.get("confirmar", ""))
        if error is None:
            otro = Usuario.query.filter(Usuario.correo == correo, Usuario.id != usuario.id).first()
            if otro:
                error = "Ese correo ya está en uso por otra cuenta."

        if error:
            flash(error, "error")
        else:
            usuario.nombre, usuario.apellidos, usuario.correo = nombre, apellidos, correo
            usuario.edad, usuario.peso, usuario.estatura, usuario.frecuencia = edad, peso, estatura, frecuencia
            if nueva:
                usuario.poner_contrasena(nueva)
            db.session.commit()
            flash("Perfil actualizado.", "ok")
            return redirect(url_for("perfil.ver"))
    return render_template("perfil/editar.html", frecuencias=catalogo.FRECUENCIAS)


@perfil.route("/eliminar", methods=["POST"])
@login_requerido
def eliminar():
    usuario = usuario_actual()
    if request.form.get("confirmar", "").strip().upper() != "ELIMINAR" \
            or not usuario.revisar_contrasena(request.form.get("contrasena", "")):
        flash("No se eliminó la cuenta: escribe ELIMINAR y tu contraseña correcta.", "error")
        return redirect(url_for("perfil.editar") + "#zona-peligro")
    db.session.delete(usuario)
    db.session.commit()
    personal = session.get("personal_id")
    session.clear()
    if personal:
        session["personal_id"] = personal
    flash("Tu cuenta y todos tus datos fueron eliminados.", "ok")
    return redirect(url_for("main.inicio"))
