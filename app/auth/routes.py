"""Cuenta: registro, inicio/cierre de sesión y recuperación de contraseña (Funciones 1-3)."""
import hashlib
import hmac
import secrets
from datetime import timedelta

from flask import (Blueprint, current_app, flash, redirect, render_template, request,
                   session, url_for)

from .. import catalogo, tiempo
from ..extensions import db
from ..models import CodigoRecuperacion, Usuario
from ..utils import (a_entero, correo_configurado, correo_valido, destino_seguro, enviar_correo,
                     errores_contrasena, iniciar_sesion, usuario_actual)

auth = Blueprint("auth", __name__, url_prefix="/cuenta")


# ───────────────────────── Registro ─────────────────────────
@auth.route("/registro", methods=["GET", "POST"])
def registro():
    if usuario_actual():
        return redirect(url_for("main.inicio"))
    cfg = current_app.config
    datos = {}
    if request.method == "POST":
        datos = {k: request.form.get(k, "").strip() for k in
                 ("nombre", "apellidos", "correo", "edad", "frecuencia")}
        datos["correo"] = datos["correo"].lower()
        clave = request.form.get("contrasena", "")
        confirmar = request.form.get("confirmar", "")
        edad = a_entero(datos["edad"], cfg["EDAD_MINIMA"], cfg["EDAD_MAXIMA"])

        error = None
        if not (2 <= len(datos["nombre"]) <= 100):
            error = "Escribe tu nombre (entre 2 y 100 caracteres)."
        elif len(datos["apellidos"]) > 150:
            error = "Los apellidos son demasiado largos."
        elif not correo_valido(datos["correo"]):
            error = "Escribe un correo válido, por ejemplo nombre@correo.com."
        elif edad is None:
            error = f"Tu edad debe estar entre {cfg['EDAD_MINIMA']} y {cfg['EDAD_MAXIMA']} años."
        elif datos["frecuencia"] not in catalogo.FRECUENCIAS:
            error = "Indica si haces ejercicio con frecuencia."
        else:
            error = errores_contrasena(clave, confirmar)
        if error is None and Usuario.query.filter_by(correo=datos["correo"]).first():
            error = "Ese correo ya tiene una cuenta. Inicia sesión o recupera tu contraseña."

        if error:
            flash(error, "error")
        else:
            usuario = Usuario(nombre=datos["nombre"], apellidos=datos["apellidos"], correo=datos["correo"],
                              edad=edad, frecuencia=datos["frecuencia"])
            usuario.poner_contrasena(clave)
            db.session.add(usuario)
            db.session.commit()
            iniciar_sesion(usuario)
            flash(f"¡Bienvenido, {usuario.nombre}! Ahora elige tu objetivo.", "ok")
            return redirect(url_for("actividad.objetivos"))
    return render_template("auth/registro.html", datos=datos, frecuencias=catalogo.FRECUENCIAS)


# ───────────────────────── Inicio y cierre de sesión ─────────────────────────
@auth.route("/entrar", methods=["GET", "POST"])
def login():
    if usuario_actual():
        return redirect(url_for("main.inicio"))
    cfg = current_app.config
    siguiente = request.values.get("siguiente", "")
    if request.method == "POST":
        correo = request.form.get("correo", "").strip().lower()
        clave = request.form.get("contrasena", "")
        usuario = Usuario.query.filter_by(correo=correo).first()
        ahora = tiempo.ahora()

        if usuario and usuario.bloqueado_hasta and usuario.bloqueado_hasta > ahora:
            minutos = int((usuario.bloqueado_hasta - ahora).total_seconds() // 60) + 1
            flash(f"Demasiados intentos fallidos. Inténtalo de nuevo en {minutos} min "
                  "o recupera tu contraseña.", "error")
        elif usuario and usuario.revisar_contrasena(clave):
            usuario.intentos_fallidos = 0
            usuario.bloqueado_hasta = None
            db.session.commit()
            iniciar_sesion(usuario)
            return redirect(destino_seguro(siguiente) or url_for("main.inicio"))
        else:
            if usuario:
                usuario.intentos_fallidos += 1
                if usuario.intentos_fallidos >= cfg["LOGIN_MAX_INTENTOS"]:
                    usuario.bloqueado_hasta = ahora + timedelta(minutes=cfg["LOGIN_BLOQUEO_MINUTOS"])
                    usuario.intentos_fallidos = 0
                db.session.commit()
            flash("Correo o contraseña incorrectos.", "error")
    return render_template("auth/login.html", siguiente=siguiente)


@auth.route("/salir", methods=["POST"])
def logout():
    personal = session.get("personal_id")
    session.clear()
    if personal:
        session["personal_id"] = personal
    flash("Cerraste sesión. ¡Hasta pronto!", "ok")
    return redirect(url_for("auth.login"))


# ───────────────────────── Recuperación de contraseña ─────────────────────────
def _hash_codigo(codigo: str) -> str:
    return hmac.new(current_app.config["SECRET_KEY"].encode(), codigo.encode(), hashlib.sha256).hexdigest()


@auth.route("/recuperar", methods=["GET", "POST"])
def recuperar():
    if request.method == "POST":
        correo = request.form.get("correo", "").strip().lower()
        if not correo_valido(correo):
            flash("Escribe un correo válido.", "error")
            return render_template("auth/recuperar.html")

        usuario = Usuario.query.filter_by(correo=correo).first()
        codigo_dev = None
        if usuario:
            CodigoRecuperacion.query.filter_by(usuario_id=usuario.id, usado=False).update({"usado": True})
            codigo = f"{secrets.randbelow(1_000_000):06d}"
            minutos = current_app.config["CODIGO_VALIDO_MINUTOS"]
            db.session.add(CodigoRecuperacion(usuario_id=usuario.id, codigo_hash=_hash_codigo(codigo),
                                              expira_en=tiempo.ahora() + timedelta(minutes=minutos)))
            db.session.commit()
            cuerpo = (f"Hola {usuario.nombre},\n\nTu código para recuperar tu contraseña de "
                      f"Activate + Chimal es: {codigo}\n\nCaduca en {minutos} minutos. "
                      "Si no lo pediste tú, ignora este mensaje.\n")
            enviado = enviar_correo(usuario.correo, "Tu código de recuperación", cuerpo)
            if not enviado:
                current_app.logger.warning("Código de recuperación NO enviado (correo sin configurar o con error).")
                if current_app.debug and not correo_configurado():
                    codigo_dev = codigo   # solo para pruebas locales
        session["recuperar_correo"] = correo
        flash("Si ese correo está registrado, te enviamos un código de 6 dígitos.", "info")
        if codigo_dev:
            flash(f"Modo desarrollo (sin correo configurado): tu código es {codigo_dev}.", "info")
        return redirect(url_for("auth.verificar_codigo"))
    return render_template("auth/recuperar.html")


@auth.route("/recuperar/codigo", methods=["GET", "POST"])
def verificar_codigo():
    correo = session.get("recuperar_correo")
    if not correo:
        return redirect(url_for("auth.recuperar"))
    if request.method == "POST":
        codigo = request.form.get("codigo", "").strip()
        clave = request.form.get("contrasena", "")
        confirmar = request.form.get("confirmar", "")
        error = errores_contrasena(clave, confirmar)
        if not (codigo.isdigit() and len(codigo) == 6):
            error = "El código tiene 6 dígitos."
        if error:
            flash(error, "error")
            return render_template("auth/codigo.html", correo=correo)

        usuario = Usuario.query.filter_by(correo=correo).first()
        registro = None
        if usuario:
            registro = (CodigoRecuperacion.query.filter_by(usuario_id=usuario.id, usado=False)
                        .order_by(CodigoRecuperacion.creado_en.desc()).first())
        valido = False
        if registro is not None:
            if registro.expira_en < tiempo.ahora() or registro.intentos >= current_app.config["CODIGO_MAX_INTENTOS"]:
                registro.usado = True
            elif hmac.compare_digest(registro.codigo_hash, _hash_codigo(codigo)):
                valido = True
            else:
                registro.intentos += 1
            db.session.commit()

        if not valido:
            flash("El código es incorrecto o ya caducó. Puedes pedir uno nuevo.", "error")
            return render_template("auth/codigo.html", correo=correo)

        registro.usado = True
        usuario.poner_contrasena(clave)
        usuario.intentos_fallidos = 0
        usuario.bloqueado_hasta = None
        db.session.commit()
        session.pop("recuperar_correo", None)
        flash("Contraseña actualizada. Ya puedes iniciar sesión.", "ok")
        return redirect(url_for("auth.login"))
    return render_template("auth/codigo.html", correo=correo)
