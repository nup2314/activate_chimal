"""Application Factory de Activate + Chimal."""
import logging

import click
from flask import Flask, render_template, request
from flask_wtf.csrf import CSRFError
from werkzeug.middleware.proxy_fix import ProxyFix

from . import avatar_config, catalogo, tiempo
from .config import Config
from .extensions import csrf, db, migrate


def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    if app.config["CONFIAR_EN_PROXY"]:  # Render entrega HTTPS a través de un proxy
        app.wsgi_app = ProxyFix(app.wsgi_app, x_for=1, x_proto=1, x_host=1)

    db.init_app(app)
    migrate.init_app(app, db)
    csrf.init_app(app)

    from . import models  # noqa: F401  (registra las tablas)

    _registrar_blueprints(app)
    _registrar_contexto(app)
    _registrar_errores(app)
    _registrar_comandos(app)

    if app.config["SECRET_KEY_ES_TEMPORAL"]:
        app.logger.warning("SECRET_KEY no está definida: se usa una clave temporal. "
                           "Defínela en .env o en las variables de entorno de Render.")
    if app.config["CREAR_TABLAS_AUTO"]:
        with app.app_context():
            db.create_all()

    if not app.debug:
        logging.basicConfig(level=logging.INFO)
    return app


def _registrar_blueprints(app):
    from .actividad.routes import actividad
    from .auth.routes import auth
    from .avatar.routes import avatar
    from .comunidad.routes import comunidad
    from .info.routes import info
    from .main.routes import main
    from .perfil.routes import perfil
    from .personal.routes import personal
    from .seguimiento.routes import seguimiento

    for bp in (main, auth, perfil, actividad, seguimiento, comunidad, avatar, info, personal):
        app.register_blueprint(bp)


def _registrar_contexto(app):
    from .utils import personal_actual, usuario_actual

    @app.context_processor
    def inyectar():
        return {
            "usuario_actual": usuario_actual(),
            "personal_actual": personal_actual(),
            "meta_pasos": app.config["META_PASOS"],
            "hoy": tiempo.hoy(),
            "avatar_ui": avatar_config.avatar_ui,
            "rango": catalogo.rango,
            "OBJETIVOS": catalogo.OBJETIVOS,
            "TIPOS_NOVEDAD": catalogo.TIPOS_NOVEDAD,
        }

    app.jinja_env.globals["mascota_nombre"] = app.config["MASCOTA_NOMBRE"]

    @app.template_filter("miles")
    def miles(valor):
        try:
            return f"{int(valor):,}"
        except (TypeError, ValueError):
            return valor

    @app.template_filter("fecha")
    def fecha(valor, formato="corta"):
        if valor is None:
            return ""
        meses = ["ene", "feb", "mar", "abr", "may", "jun", "jul", "ago", "sep", "oct", "nov", "dic"]
        base = f"{valor.day} {meses[valor.month - 1]} {valor.year}"
        if formato == "hora" and hasattr(valor, "hour"):
            return f"{base}, {valor.hour:02d}:{valor.minute:02d}"
        return base

    @app.after_request
    def cabeceras(resp):
        resp.headers.setdefault("X-Content-Type-Options", "nosniff")
        resp.headers.setdefault("X-Frame-Options", "DENY")
        resp.headers.setdefault("Referrer-Policy", "strict-origin-when-cross-origin")
        if request.endpoint and request.endpoint != "static":
            resp.headers.setdefault("Cache-Control", "no-store")
        return resp


def _registrar_errores(app):
    def pagina(codigo, titulo, texto):
        return render_template("error.html", codigo=codigo, titulo=titulo, texto=texto), codigo

    @app.errorhandler(404)
    def no_encontrada(_e):
        return pagina(404, "No encontramos esa página", "Revisa la dirección o vuelve al inicio.")

    @app.errorhandler(403)
    def prohibida(_e):
        return pagina(403, "No tienes acceso", "Esta sección no está disponible para tu cuenta.")

    @app.errorhandler(CSRFError)
    def csrf_vencido(_e):
        return pagina(400, "El formulario caducó",
                      "Por seguridad, vuelve atrás, recarga la página e inténtalo de nuevo.")

    @app.errorhandler(500)
    def error_servidor(_e):
        db.session.rollback()
        return pagina(500, "Algo salió mal", "Ya quedó registrado. Inténtalo de nuevo en unos minutos.")


def _registrar_comandos(app):
    from .models import Novedad, Personal

    @app.cli.command("crear-personal")
    @click.argument("usuario")
    @click.option("--contrasena", prompt=True, hide_input=True, confirmation_prompt=True)
    def crear_personal(usuario, contrasena):
        """Crea (o reactiva y actualiza) una cuenta del personal: flask crear-personal maria"""
        usuario = usuario.strip().lower()
        if len(contrasena) < 8:
            raise click.ClickException("La contraseña debe tener al menos 8 caracteres.")
        persona = Personal.query.filter_by(usuario=usuario).first()
        if persona is None:
            persona = Personal(usuario=usuario)
            db.session.add(persona)
        persona.poner_contrasena(contrasena)
        persona.activo = True
        db.session.commit()
        click.echo(f"Cuenta de personal lista: {usuario}")

    @app.cli.command("desactivar-personal")
    @click.argument("usuario")
    def desactivar_personal(usuario):
        """Desactiva una cuenta del personal sin borrar sus novedades."""
        persona = Personal.query.filter_by(usuario=usuario.strip().lower()).first()
        if persona is None:
            raise click.ClickException("No existe ese usuario del personal.")
        persona.activo = False
        db.session.commit()
        click.echo("Cuenta desactivada.")

    @app.cli.command("cargar-demo")
    def cargar_demo():
        """Agrega novedades de ejemplo si todavía no hay ninguna."""
        if Novedad.query.count():
            click.echo("Ya hay novedades; no se agregó nada.")
            return
        ejemplos = [
            ("Arranca la liga vecinal de fútbol 7", "evento",
             "Inscripciones abiertas para equipos mixtos. Los partidos serán los sábados por la mañana. "
             "Lleva tu credencial y agua.", "Unidad deportiva de la colonia"),
            ("Cinco hábitos para llegar a tu meta de 6,000 pasos", "consejo",
             "Baja una parada antes, camina mientras hablas por teléfono, usa escaleras, "
             "sal a caminar 10 minutos después de comer y organiza reuniones de pie.", None),
            ("Torneo relámpago de voleibol", "torneo",
             "Equipos de 6 jugadores. Cupo limitado a 8 equipos. Premios para los tres primeros lugares.",
             "Cancha techada del centro comunitario"),
        ]
        for titulo, tipo, desc, lugar in ejemplos:
            db.session.add(Novedad(titulo=titulo, tipo=tipo, descripcion=desc, lugar=lugar, estado="publicada"))
        db.session.commit()
        click.echo("Novedades de ejemplo creadas.")
