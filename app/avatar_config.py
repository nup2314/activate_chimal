"""Configuración del avatar: validación en el servidor.

La fuente única de verdad es `static/data/avatar_esquema.json` (opciones, rangos, paletas y
valores por defecto). La interfaz lo usa para generarse sola y aquí se usa para validar, así que
para agregar una opción nueva basta con añadirla al JSON (y dibujarla en `avatar-core.js`).
"""
import json
import re
from pathlib import Path

from flask import url_for
from markupsafe import Markup, escape

RUTA_ESQUEMA = Path(__file__).parent / "static" / "data" / "avatar_esquema.json"
ESQUEMA = json.loads(RUTA_ESQUEMA.read_text(encoding="utf-8"))
DEFECTO = ESQUEMA["defecto"]
PATRON_COLOR = re.compile(r"^#[0-9a-fA-F]{6}$")


def _campos() -> dict:
    """campo -> sección del esquema (para saber su tipo, opciones y rango)."""
    campos = {}
    for categoria in ESQUEMA["categorias"]:
        for seccion in categoria["secciones"]:
            campos[seccion["campo"]] = seccion
    return campos


CAMPOS = _campos()


def _valido(seccion: dict, valor):
    """Devuelve el valor limpio o None si no es válido para esa sección."""
    tipo = seccion["tipo"]
    if tipo == "opciones":
        return valor if valor in {o["id"] for o in seccion["opciones"]} else None
    if tipo == "color":
        return valor.lower() if isinstance(valor, str) and PATRON_COLOR.match(valor) else None
    if tipo == "slider":
        if isinstance(valor, bool) or not isinstance(valor, (int, float)):
            return None
        if valor != valor:  # NaN
            return None
        return round(min(max(float(valor), seccion["min"]), seccion["max"]), 3)
    return None


def normalizar(datos) -> dict:
    """Acepta un dict (o texto JSON) y devuelve una configuración completa y segura."""
    if isinstance(datos, str):
        try:
            datos = json.loads(datos)
        except ValueError:
            datos = {}
    if not isinstance(datos, dict):
        datos = {}
    limpio = {}
    for campo, defecto in DEFECTO.items():
        valor = _valido(CAMPOS[campo], datos.get(campo)) if campo in datos else None
        limpio[campo] = defecto if valor is None else valor
    return limpio


def config_de(avatar) -> dict:
    """Configuración completa a partir del modelo `Avatar` (o None)."""
    return normalizar(avatar.datos if avatar is not None else {})


def avatar_ui(avatar, tamano: int = 56, vista: str = "retrato", clase: str = "") -> Markup:
    """HTML de un avatar pequeño. `avatar-core.js` lo dibuja; sin JavaScript se ve la mascota."""
    carga = escape(json.dumps(config_de(avatar), separators=(",", ":")))
    vista = vista if vista in ("retrato", "completo") else "retrato"
    respaldo = url_for("static", filename="img/mascota-cara.png")
    return Markup(
        f'<span class="avatar-ui avatar-ui--{vista} {escape(clase)}" data-avatar="{carga}" '
        f'data-vista="{vista}" style="--tam:{int(tamano)}px">'
        f'<img src="{respaldo}" width="{int(tamano)}" height="{int(tamano)}" alt=""></span>'
    )
