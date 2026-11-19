"""Estadísticas e historial (Funciones 10 y 11)."""
from datetime import datetime

from flask import Blueprint, render_template, request

from .. import servicios, tiempo
from ..utils import login_requerido, usuario_actual

seguimiento = Blueprint("seguimiento", __name__)

POR_PAGINA = 25


@seguimiento.route("/estadisticas")
@login_requerido
def estadisticas():
    usuario = usuario_actual()
    return render_template("seguimiento/estadisticas.html", r=servicios.resumen(usuario))


def _fecha(texto):
    try:
        return datetime.strptime(texto, "%Y-%m-%d").date()
    except (TypeError, ValueError):
        return None


@seguimiento.route("/historial")
@login_requerido
def historial():
    usuario = usuario_actual()
    tipo = request.args.get("tipo", "todo")
    if tipo not in ("todo", "actividades", "retos", "pasos"):
        tipo = "todo"
    desde, hasta = _fecha(request.args.get("desde")), _fecha(request.args.get("hasta"))
    pagina = max(1, request.args.get("pagina", 1, type=int) or 1)

    eventos = servicios.historial(usuario.id, desde, hasta, tipo)
    total = len(eventos)
    paginas = max(1, -(-total // POR_PAGINA))
    pagina = min(pagina, paginas)
    visibles = eventos[(pagina - 1) * POR_PAGINA: pagina * POR_PAGINA]

    # Agrupar por fecha para mostrar "un día = un bloque"
    grupos = []
    for e in visibles:
        if not grupos or grupos[-1]["fecha"] != e["fecha"]:
            grupos.append({"fecha": e["fecha"], "eventos": []})
        grupos[-1]["eventos"].append(e)

    filtros = {"tipo": tipo, "desde": desde.isoformat() if desde else "", "hasta": hasta.isoformat() if hasta else ""}
    return render_template("seguimiento/historial.html", grupos=grupos, filtros=filtros, total=total,
                           pagina=pagina, paginas=paginas, hoy=tiempo.hoy())
