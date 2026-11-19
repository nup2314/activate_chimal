"""Lógica de negocio: reto diario, pasos, rachas, estadísticas y clasificación."""
from collections import defaultdict
from datetime import datetime, time, timedelta

from flask import current_app
from sqlalchemy import func

from . import catalogo, tiempo
from .extensions import db
from .models import Actividad, Paso, ProgresoReto, RetoDia, Usuario


# ───────────────────────── Reto diario (Funciones 6 y 7) ─────────────────────────
def reto_del_dia(usuario: Usuario, fecha=None) -> dict:
    fecha = fecha or tiempo.hoy()
    plan = catalogo.rutina_para_usuario(usuario.objetivo, usuario.edad, usuario.frecuencia)
    hechos = {p.ejercicio: p.repeticiones for p in
              ProgresoReto.query.filter_by(usuario_id=usuario.id, fecha=fecha)}
    items = []
    for e in plan:
        hecho = hechos.get(e["clave"], 0)
        pct = min(100, round(hecho * 100 / e["meta"])) if e["meta"] else 0
        items.append({**e, "hecho": hecho, "pct": pct, "completo": hecho >= e["meta"],
                      "incrementos": catalogo.INCREMENTOS[e["unidad"]],
                      "texto_meta": catalogo.texto_meta(e["unidad"], e["meta"])})
    total = round(sum(i["pct"] for i in items) / len(items)) if items else 0
    objetivo = catalogo.OBJETIVOS.get(usuario.objetivo or "mantenerse_activo")
    return {"ejercicios": items, "porcentaje": total, "completo": total >= 100 and bool(items),
            "objetivo": objetivo, "grupo_edad": catalogo.GRUPOS_EDAD[catalogo.indice_grupo_edad(usuario.edad)]}


def cambiar_progreso(usuario: Usuario, clave: str, accion: str, cantidad: int = 0) -> bool:
    """Suma, resta o reinicia las repeticiones de un ejercicio del día. Devuelve True si se guardó."""
    reto = reto_del_dia(usuario)
    if clave not in {i["clave"] for i in reto["ejercicios"]}:
        return False
    fila = ProgresoReto.query.filter_by(usuario_id=usuario.id, fecha=tiempo.hoy(), ejercicio=clave).first()
    if fila is None:
        fila = ProgresoReto(usuario_id=usuario.id, fecha=tiempo.hoy(), ejercicio=clave, repeticiones=0)
        db.session.add(fila)
    if accion == "sumar":
        fila.repeticiones = min(fila.repeticiones + cantidad, 9999)
    elif accion == "restar":
        fila.repeticiones = max(fila.repeticiones - cantidad, 0)
    elif accion == "reiniciar":
        fila.repeticiones = 0
    else:
        return False
    db.session.flush()
    _guardar_resumen_reto(usuario)
    db.session.commit()
    return True


def _guardar_resumen_reto(usuario: Usuario) -> None:
    reto = reto_del_dia(usuario)
    fila = RetoDia.query.filter_by(usuario_id=usuario.id, fecha=tiempo.hoy()).first()
    if fila is None:
        fila = RetoDia(usuario_id=usuario.id, fecha=tiempo.hoy())
        db.session.add(fila)
    fila.objetivo = usuario.objetivo or "mantenerse_activo"
    fila.porcentaje = reto["porcentaje"]
    fila.completado = reto["completo"]


# ───────────────────────── Pasos (Función 9) ─────────────────────────
def pasos_de(usuario_id: int, fecha=None) -> int:
    fila = Paso.query.filter_by(usuario_id=usuario_id, fecha=fecha or tiempo.hoy()).first()
    return fila.cantidad if fila else 0


def guardar_pasos(usuario_id: int, cantidad: int, modo: str = "sumar", fecha=None) -> int:
    fecha = fecha or tiempo.hoy()
    fila = Paso.query.filter_by(usuario_id=usuario_id, fecha=fecha).first()
    if fila is None:
        fila = Paso(usuario_id=usuario_id, fecha=fecha, cantidad=0)
        db.session.add(fila)
    fila.cantidad = min(cantidad if modo == "fijar" else fila.cantidad + cantidad, 200000)
    db.session.commit()
    return fila.cantidad


# ───────────────────────── Rachas ─────────────────────────
def dias_activos(usuario_id: int) -> set:
    """Un día cuenta si hay una actividad registrada, se llegó a la meta de pasos o se completó el reto."""
    meta = current_app.config["META_PASOS"]
    dias = {f.date() for (f,) in db.session.query(Actividad.fecha).filter(Actividad.usuario_id == usuario_id)}
    dias |= {f for (f,) in db.session.query(Paso.fecha).filter(Paso.usuario_id == usuario_id, Paso.cantidad >= meta)}
    dias |= {f for (f,) in db.session.query(RetoDia.fecha).filter(RetoDia.usuario_id == usuario_id,
                                                                  RetoDia.completado.is_(True))}
    return dias


def calcular_rachas(dias: set, hoy) -> tuple[int, int]:
    if not dias:
        return 0, 0
    cursor = hoy if hoy in dias else hoy - timedelta(days=1)
    actual = 0
    while cursor in dias:
        actual += 1
        cursor -= timedelta(days=1)
    mejor = corrida = 0
    previo = None
    for d in sorted(dias):
        corrida = corrida + 1 if previo is not None and d - previo == timedelta(days=1) else 1
        mejor = max(mejor, corrida)
        previo = d
    return actual, mejor


# ───────────────────────── Estadísticas (Función 10) ─────────────────────────
def resumen(usuario: Usuario) -> dict:
    uid = usuario.id
    meta = current_app.config["META_PASOS"]
    hoy = tiempo.hoy()
    total_act, minutos, calorias, distancia = db.session.query(
        func.count(Actividad.id), func.coalesce(func.sum(Actividad.tiempo), 0),
        func.coalesce(func.sum(Actividad.calorias), 0), func.coalesce(func.sum(Actividad.distancia), 0),
    ).filter(Actividad.usuario_id == uid).one()
    pasos_total = db.session.query(func.coalesce(func.sum(Paso.cantidad), 0)).filter(Paso.usuario_id == uid).scalar()
    dias_meta = db.session.query(func.count(Paso.id)).filter(Paso.usuario_id == uid, Paso.cantidad >= meta).scalar()
    retos_ok = db.session.query(func.count(RetoDia.id)).filter(
        RetoDia.usuario_id == uid, RetoDia.completado.is_(True)).scalar()
    dias = dias_activos(uid)
    actual, mejor = calcular_rachas(dias, hoy)
    por_deporte = db.session.query(Actividad.actividad, func.count(Actividad.id), func.sum(Actividad.tiempo)) \
        .filter(Actividad.usuario_id == uid).group_by(Actividad.actividad) \
        .order_by(func.sum(Actividad.tiempo).desc()).all()
    return {
        "actividades": total_act, "minutos": int(minutos), "calorias": round(float(calorias)),
        "distancia": round(float(distancia), 1), "pasos_total": int(pasos_total),
        "dias_meta_pasos": dias_meta, "retos_completados": retos_ok,
        "dias_activos": len(dias), "racha": actual, "mejor_racha": mejor,
        "por_deporte": [{"nombre": n, "veces": v, "minutos": int(m or 0)} for n, v, m in por_deporte],
        "semana": serie_semana(uid),
    }


def serie_semana(usuario_id: int, dias: int = 7) -> list[dict]:
    hoy = tiempo.hoy()
    inicio = hoy - timedelta(days=dias - 1)
    nombres = ["lun", "mar", "mié", "jue", "vie", "sáb", "dom"]
    minutos = defaultdict(int)
    for f, t in db.session.query(Actividad.fecha, Actividad.tiempo).filter(
            Actividad.usuario_id == usuario_id, Actividad.fecha >= datetime.combine(inicio, time.min)):
        minutos[f.date()] += t
    pasos = {f: c for f, c in db.session.query(Paso.fecha, Paso.cantidad).filter(
        Paso.usuario_id == usuario_id, Paso.fecha >= inicio)}
    retos = {f: p for f, p in db.session.query(RetoDia.fecha, RetoDia.porcentaje).filter(
        RetoDia.usuario_id == usuario_id, RetoDia.fecha >= inicio)}
    meta = current_app.config["META_PASOS"]
    salida = []
    for i in range(dias):
        d = inicio + timedelta(days=i)
        salida.append({"fecha": d, "dia": nombres[d.weekday()], "es_hoy": d == hoy,
                       "minutos": minutos.get(d, 0), "pasos": pasos.get(d, 0),
                       "pasos_pct": min(100, round(pasos.get(d, 0) * 100 / meta)),
                       "reto": retos.get(d, 0)})
    return salida


# ───────────────────────── Historial (Función 11) ─────────────────────────
def historial(usuario_id: int, desde=None, hasta=None, tipo: str = "todo") -> list[dict]:
    """Eventos del usuario (actividades, retos y pasos) ordenados del más reciente al más antiguo."""
    eventos = []
    if tipo in ("todo", "actividades"):
        q = Actividad.query.filter_by(usuario_id=usuario_id)
        if desde:
            q = q.filter(Actividad.fecha >= datetime.combine(desde, time.min))
        if hasta:
            q = q.filter(Actividad.fecha <= datetime.combine(hasta, time.max))
        for a in q:
            eventos.append({"tipo": "actividad", "fecha": a.fecha.date(), "orden": a.fecha, "obj": a})
    if tipo in ("todo", "retos"):
        q = RetoDia.query.filter_by(usuario_id=usuario_id).filter(RetoDia.porcentaje > 0)
        if desde:
            q = q.filter(RetoDia.fecha >= desde)
        if hasta:
            q = q.filter(RetoDia.fecha <= hasta)
        for r in q:
            eventos.append({"tipo": "reto", "fecha": r.fecha, "orden": datetime.combine(r.fecha, time(12)), "obj": r})
    if tipo in ("todo", "pasos"):
        q = Paso.query.filter_by(usuario_id=usuario_id).filter(Paso.cantidad > 0)
        if desde:
            q = q.filter(Paso.fecha >= desde)
        if hasta:
            q = q.filter(Paso.fecha <= hasta)
        for p in q:
            eventos.append({"tipo": "pasos", "fecha": p.fecha, "orden": datetime.combine(p.fecha, time(6)), "obj": p})
    eventos.sort(key=lambda e: e["orden"], reverse=True)
    return eventos


# ───────────────────────── Clasificación (Función 13) ─────────────────────────
def clasificacion(periodo: str = "semana") -> list[dict]:
    """Puntos = 1 por minuto de actividad + 1 por cada 100 pasos + 30 por reto completado."""
    hoy = tiempo.hoy()
    desde = hoy - timedelta(days=6) if periodo == "semana" else None

    q_min = db.session.query(Actividad.usuario_id, func.sum(Actividad.tiempo)).group_by(Actividad.usuario_id)
    q_pas = db.session.query(Paso.usuario_id, func.sum(Paso.cantidad)).group_by(Paso.usuario_id)
    q_ret = db.session.query(RetoDia.usuario_id, func.count(RetoDia.id)) \
        .filter(RetoDia.completado.is_(True)).group_by(RetoDia.usuario_id)
    if desde:
        q_min = q_min.filter(Actividad.fecha >= datetime.combine(desde, time.min))
        q_pas = q_pas.filter(Paso.fecha >= desde)
        q_ret = q_ret.filter(RetoDia.fecha >= desde)
    minutos = {u: int(v or 0) for u, v in q_min}
    pasos = {u: int(v or 0) for u, v in q_pas}
    retos = {u: int(v or 0) for u, v in q_ret}
    hoy_pct = {u: p for u, p in db.session.query(RetoDia.usuario_id, RetoDia.porcentaje).filter(RetoDia.fecha == hoy)}

    filas = []
    for u in Usuario.query.all():
        m, p, r = minutos.get(u.id, 0), pasos.get(u.id, 0), retos.get(u.id, 0)
        filas.append({"usuario": u, "minutos": m, "pasos": p, "retos": r,
                      "reto_hoy": hoy_pct.get(u.id, 0), "puntos": m + p // 100 + r * 30})
    filas.sort(key=lambda f: (-f["puntos"], f["usuario"].nombre.lower(), f["usuario"].id))
    for i, f in enumerate(filas, start=1):
        f["posicion"] = i
    return filas
