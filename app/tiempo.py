"""Fechas en hora de México (el servidor suele estar en UTC)."""
from datetime import date, datetime, timedelta, timezone

try:
    from zoneinfo import ZoneInfo
    ZONA = ZoneInfo("America/Mexico_City")
except Exception:  # Windows sin el paquete `tzdata`: se usa UTC-6 fijo (México ya no usa horario de verano)
    ZONA = timezone(timedelta(hours=-6), "CST")


def ahora() -> datetime:
    """Fecha y hora actuales de México, sin zona (como se guarda en la BD)."""
    return datetime.now(ZONA).replace(tzinfo=None)


def hoy() -> date:
    return ahora().date()
