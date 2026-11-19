"""Utilidades compartidas: sesión, permisos, validaciones y correo."""
import re
import smtplib
from email.message import EmailMessage
from functools import wraps
from urllib.parse import urlparse

from flask import current_app, flash, g, redirect, request, session, url_for

from .extensions import db
from .models import Personal, Usuario

PATRON_CORREO = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]{2,}$")


# ───────────────────────── Sesión de usuario ─────────────────────────
def usuario_actual():
    """Usuario con sesión iniciada (o None). Se consulta una sola vez por solicitud."""
    if "usuario" not in g:
        g.usuario = None
        uid = session.get("usuario_id")
        if uid:
            g.usuario = db.session.get(Usuario, uid)
            if g.usuario is None:       # la cuenta ya no existe
                session.pop("usuario_id", None)
    return g.usuario


def iniciar_sesion(usuario: Usuario) -> None:
    personal = session.get("personal_id")
    session.clear()                      # evita reutilizar una sesión anterior
    if personal:
        session["personal_id"] = personal
    session["usuario_id"] = usuario.id
    session.permanent = True
    g.pop("usuario", None)


def login_requerido(vista):
    @wraps(vista)
    def envoltura(*args, **kwargs):
        if usuario_actual() is None:
            flash("Inicia sesión para continuar.", "info")
            return redirect(url_for("auth.login", siguiente=request.full_path.rstrip("?")))
        return vista(*args, **kwargs)
    return envoltura


# ───────────────────────── Sesión del personal ─────────────────────────
def personal_actual():
    if "personal" not in g:
        g.personal = None
        pid = session.get("personal_id")
        if pid:
            p = db.session.get(Personal, pid)
            if p and p.activo:
                g.personal = p
            else:
                session.pop("personal_id", None)
    return g.personal


def personal_requerido(vista):
    @wraps(vista)
    def envoltura(*args, **kwargs):
        if personal_actual() is None:
            flash("Este módulo es solo para el personal autorizado.", "info")
            return redirect(url_for("personal.acceso"))
        return vista(*args, **kwargs)
    return envoltura


# ───────────────────────── Validaciones ─────────────────────────
def destino_seguro(destino: str | None) -> str | None:
    """Solo acepta rutas internas (evita redirecciones a sitios externos)."""
    if not destino:
        return None
    partes = urlparse(destino)
    if partes.scheme or partes.netloc or not destino.startswith("/") or destino.startswith("//"):
        return None
    return destino


def correo_valido(correo: str) -> bool:
    return bool(correo) and len(correo) <= 150 and bool(PATRON_CORREO.match(correo))


def a_entero(texto, minimo=None, maximo=None):
    """Convierte a int; devuelve None si está vacío o es inválido/fuera de rango."""
    try:
        valor = int(str(texto).strip())
    except (TypeError, ValueError):
        return None
    if minimo is not None and valor < minimo:
        return None
    if maximo is not None and valor > maximo:
        return None
    return valor


def a_decimal(texto, minimo=None, maximo=None):
    try:
        valor = float(str(texto).strip().replace(",", "."))
    except (TypeError, ValueError):
        return None
    if valor != valor or valor in (float("inf"), float("-inf")):
        return None
    if minimo is not None and valor < minimo:
        return None
    if maximo is not None and valor > maximo:
        return None
    return valor


def errores_contrasena(clave: str, confirmacion: str | None = None) -> str | None:
    if len(clave) < 8:
        return "La contraseña debe tener al menos 8 caracteres."
    if len(clave) > 128:
        return "La contraseña es demasiado larga (máximo 128 caracteres)."
    if clave.isdigit() or clave.isalpha():
        return "Combina letras y números en tu contraseña."
    if confirmacion is not None and clave != confirmacion:
        return "Las contraseñas no coinciden."
    return None


# ───────────────────────── Correo ─────────────────────────
def correo_configurado() -> bool:
    return bool(current_app.config.get("MAIL_SERVER"))


def enviar_correo(destinatario: str, asunto: str, cuerpo: str) -> bool:
    """Envía un correo real por SMTP. Devuelve False si no está configurado o falla."""
    cfg = current_app.config
    if not cfg.get("MAIL_SERVER"):
        return False
    msg = EmailMessage()
    msg["Subject"] = asunto
    msg["From"] = cfg["MAIL_REMITENTE"]
    msg["To"] = destinatario
    msg.set_content(cuerpo)
    try:
        if cfg["MAIL_PORT"] == 465:
            servidor = smtplib.SMTP_SSL(cfg["MAIL_SERVER"], cfg["MAIL_PORT"], timeout=10)
        else:
            servidor = smtplib.SMTP(cfg["MAIL_SERVER"], cfg["MAIL_PORT"], timeout=10)
            if cfg["MAIL_USE_TLS"]:
                servidor.starttls()
        with servidor:
            if cfg["MAIL_USERNAME"]:
                servidor.login(cfg["MAIL_USERNAME"], cfg["MAIL_PASSWORD"])
            servidor.send_message(msg)
        return True
    except Exception:  # noqa: BLE001  (no debe tirar la página si el correo falla)
        current_app.logger.exception("No se pudo enviar el correo a %s", destinatario)
        return False
