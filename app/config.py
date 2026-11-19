import os
import secrets


def _url_base_datos() -> str:
    url = os.environ.get("DATABASE_URL", "").strip()
    if not url:
        return "sqlite:///activate_chimal.db"  # queda en la carpeta instance/
    # Forzamos el controlador psycopg2, que es el que está en requirements.txt
    if url.startswith("postgres://"):
        url = url.replace("postgres://", "postgresql+psycopg2://", 1)
    elif url.startswith("postgresql://"):
        url = url.replace("postgresql://", "postgresql+psycopg2://", 1)
    return url


def _bool(nombre: str, defecto: bool = False) -> bool:
    valor = os.environ.get(nombre)
    if valor is None:
        return defecto
    return valor.strip().lower() in {"1", "true", "si", "sí", "yes", "on"}


EN_RENDER = bool(os.environ.get("RENDER"))


class Config:
    # Si no hay SECRET_KEY se genera una temporal (las sesiones se pierden al reiniciar).
    SECRET_KEY = os.environ.get("SECRET_KEY") or secrets.token_hex(32)
    SECRET_KEY_ES_TEMPORAL = not os.environ.get("SECRET_KEY")

    SQLALCHEMY_DATABASE_URI = _url_base_datos()
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    # Neon "duerme" las conexiones inactivas: pre_ping las revive.
    SQLALCHEMY_ENGINE_OPTIONS = {"pool_pre_ping": True, "pool_recycle": 280}
    CREAR_TABLAS_AUTO = _bool("CREAR_TABLAS_AUTO", True)

    # Sesión y cookies
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = "Lax"
    SESSION_COOKIE_SECURE = _bool("COOKIE_SEGURA", EN_RENDER)
    PERMANENT_SESSION_LIFETIME = 60 * 60 * 24 * 14  # 14 días
    CONFIAR_EN_PROXY = _bool("CONFIAR_EN_PROXY", EN_RENDER)

    # Reglas de la aplicación
    MASCOTA_NOMBRE = os.environ.get("MASCOTA_NOMBRE", "Tu guía")   # cámbialo si la mascota tiene nombre
    META_PASOS = 6000                 # Función 9
    CODIGO_VALIDO_MINUTOS = 15        # Función 3
    CODIGO_MAX_INTENTOS = 5
    LOGIN_MAX_INTENTOS = 5            # Mejora futura 3
    LOGIN_BLOQUEO_MINUTOS = 15
    EDAD_MINIMA = 10
    EDAD_MAXIMA = 100

    # Correo (Función 3 / Mejora futura 2). Sin MAIL_SERVER no se envía correo.
    MAIL_SERVER = os.environ.get("MAIL_SERVER", "")
    MAIL_PORT = int(os.environ.get("MAIL_PORT", "587"))
    MAIL_USE_TLS = _bool("MAIL_USE_TLS", True)
    MAIL_USERNAME = os.environ.get("MAIL_USERNAME", "")
    MAIL_PASSWORD = os.environ.get("MAIL_PASSWORD", "")
    MAIL_REMITENTE = os.environ.get("MAIL_REMITENTE", "Activate + Chimal <no-responder@localhost>")
