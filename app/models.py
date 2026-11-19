"""Modelos de la base de datos de Activate + Chimal."""
from werkzeug.security import check_password_hash, generate_password_hash

from . import tiempo as reloj
from .extensions import db


class Usuario(db.Model):
    __tablename__ = "usuarios"

    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(100), nullable=False)
    apellidos = db.Column(db.String(150), nullable=False, default="")
    correo = db.Column(db.String(150), unique=True, nullable=False, index=True)
    contrasena_hash = db.Column(db.String(255), nullable=False)
    edad = db.Column(db.Integer, nullable=True)
    peso = db.Column(db.Float, nullable=True)       # kg
    estatura = db.Column(db.Float, nullable=True)   # cm
    objetivo = db.Column(db.String(30), nullable=True)   # bajar_peso | ganar_musculo | mantenerse_activo
    frecuencia = db.Column(db.String(20), nullable=False, default="ocasional")  # nunca | ocasional | frecuente
    intentos_fallidos = db.Column(db.Integer, nullable=False, default=0)
    bloqueado_hasta = db.Column(db.DateTime, nullable=True)
    creado_en = db.Column(db.DateTime, nullable=False, default=reloj.ahora)

    actividades = db.relationship("Actividad", backref="usuario", cascade="all, delete-orphan")
    pasos = db.relationship("Paso", backref="usuario", cascade="all, delete-orphan")
    progreso_retos = db.relationship("ProgresoReto", backref="usuario", cascade="all, delete-orphan")
    retos_dia = db.relationship("RetoDia", backref="usuario", cascade="all, delete-orphan")
    codigos = db.relationship("CodigoRecuperacion", backref="usuario", cascade="all, delete-orphan")
    avatar = db.relationship("Avatar", backref="usuario", uselist=False, cascade="all, delete-orphan")
    deportes_favoritos = db.relationship("DeporteFavorito", backref="usuario", cascade="all, delete-orphan")

    def poner_contrasena(self, clave: str) -> None:
        self.contrasena_hash = generate_password_hash(clave)

    def revisar_contrasena(self, clave: str) -> bool:
        return check_password_hash(self.contrasena_hash, clave)

    @property
    def nombre_publico(self) -> str:
        """Nombre + inicial del apellido (para la clasificación)."""
        inicial = f" {self.apellidos.strip()[0].upper()}." if self.apellidos and self.apellidos.strip() else ""
        return f"{self.nombre.strip()}{inicial}"


class Actividad(db.Model):
    __tablename__ = "actividades"

    id = db.Column(db.Integer, primary_key=True)
    usuario_id = db.Column(db.Integer, db.ForeignKey("usuarios.id", ondelete="CASCADE"), nullable=False, index=True)
    actividad = db.Column(db.String(100), nullable=False)
    tiempo = db.Column(db.Integer, nullable=False)          # minutos
    distancia = db.Column(db.Float, nullable=True)          # km
    calorias = db.Column(db.Float, nullable=True)
    esfuerzo = db.Column(db.String(20), nullable=True)      # suave | medio | intenso
    notas = db.Column(db.String(200), nullable=True)
    fecha = db.Column(db.DateTime, nullable=False, default=reloj.ahora, index=True)


class Paso(db.Model):
    """Pasos del día (una fila por usuario y día)."""
    __tablename__ = "pasos"
    __table_args__ = (db.UniqueConstraint("usuario_id", "fecha", name="uq_pasos_usuario_fecha"),)

    id = db.Column(db.Integer, primary_key=True)
    usuario_id = db.Column(db.Integer, db.ForeignKey("usuarios.id", ondelete="CASCADE"), nullable=False, index=True)
    fecha = db.Column(db.Date, nullable=False, default=reloj.hoy)
    cantidad = db.Column(db.Integer, nullable=False, default=0)


class ProgresoReto(db.Model):
    """Repeticiones acumuladas de un ejercicio del reto diario."""
    __tablename__ = "progreso_retos"
    __table_args__ = (db.UniqueConstraint("usuario_id", "fecha", "ejercicio", name="uq_progreso_dia_ejercicio"),)

    id = db.Column(db.Integer, primary_key=True)
    usuario_id = db.Column(db.Integer, db.ForeignKey("usuarios.id", ondelete="CASCADE"), nullable=False, index=True)
    fecha = db.Column(db.Date, nullable=False, default=reloj.hoy)
    ejercicio = db.Column(db.String(40), nullable=False)
    repeticiones = db.Column(db.Integer, nullable=False, default=0)


class RetoDia(db.Model):
    """Resumen del reto de cada día: sirve para historial, rachas y clasificación."""
    __tablename__ = "retos_dia"
    __table_args__ = (db.UniqueConstraint("usuario_id", "fecha", name="uq_reto_dia_usuario_fecha"),)

    id = db.Column(db.Integer, primary_key=True)
    usuario_id = db.Column(db.Integer, db.ForeignKey("usuarios.id", ondelete="CASCADE"), nullable=False, index=True)
    fecha = db.Column(db.Date, nullable=False, default=reloj.hoy)
    objetivo = db.Column(db.String(30), nullable=False)
    porcentaje = db.Column(db.Integer, nullable=False, default=0)
    completado = db.Column(db.Boolean, nullable=False, default=False)


class CodigoRecuperacion(db.Model):
    __tablename__ = "codigos_recuperacion"

    id = db.Column(db.Integer, primary_key=True)
    usuario_id = db.Column(db.Integer, db.ForeignKey("usuarios.id", ondelete="CASCADE"), nullable=False, index=True)
    codigo_hash = db.Column(db.String(64), nullable=False)
    expira_en = db.Column(db.DateTime, nullable=False)
    usado = db.Column(db.Boolean, nullable=False, default=False)
    intentos = db.Column(db.Integer, nullable=False, default=0)
    creado_en = db.Column(db.DateTime, nullable=False, default=reloj.ahora)


class Avatar(db.Model):
    """Personalización del avatar: un JSON validado por `avatar_config.normalizar`."""
    __tablename__ = "avatar_config"

    id = db.Column(db.Integer, primary_key=True)
    usuario_id = db.Column(db.Integer, db.ForeignKey("usuarios.id", ondelete="CASCADE"), unique=True, nullable=False)
    datos = db.Column(db.JSON, nullable=False, default=dict)
    actualizado_en = db.Column(db.DateTime, nullable=False, default=reloj.ahora, onupdate=reloj.ahora)


class DeporteFavorito(db.Model):
    """Deportes marcados como favoritos (criterio 12 de la lista de cotejo)."""
    __tablename__ = "deportes_favoritos"
    __table_args__ = (db.UniqueConstraint("usuario_id", "deporte", name="uq_favorito_usuario_deporte"),)

    id = db.Column(db.Integer, primary_key=True)
    usuario_id = db.Column(db.Integer, db.ForeignKey("usuarios.id", ondelete="CASCADE"), nullable=False, index=True)
    deporte = db.Column(db.String(40), nullable=False)


class Novedad(db.Model):
    __tablename__ = "novedades"

    id = db.Column(db.Integer, primary_key=True)
    titulo = db.Column(db.String(150), nullable=False)
    descripcion = db.Column(db.Text, nullable=False)
    tipo = db.Column(db.String(50), nullable=False)          # noticia | evento | torneo | consejo
    fecha_evento = db.Column(db.DateTime, nullable=True)
    lugar = db.Column(db.String(150), nullable=True)
    estado = db.Column(db.String(20), nullable=False, default="publicada")  # publicada | borrador | archivada
    fecha_publicacion = db.Column(db.DateTime, nullable=False, default=reloj.ahora)
    actualizado_en = db.Column(db.DateTime, nullable=False, default=reloj.ahora, onupdate=reloj.ahora)
    autor_id = db.Column(db.Integer, db.ForeignKey("personal.id", ondelete="SET NULL"), nullable=True)


class Personal(db.Model):
    __tablename__ = "personal"

    id = db.Column(db.Integer, primary_key=True)
    usuario = db.Column(db.String(80), unique=True, nullable=False)
    contrasena_hash = db.Column(db.String(255), nullable=False)
    activo = db.Column(db.Boolean, nullable=False, default=True)

    novedades = db.relationship("Novedad", backref="autor")

    def poner_contrasena(self, clave: str) -> None:
        self.contrasena_hash = generate_password_hash(clave)

    def revisar_contrasena(self, clave: str) -> bool:
        return check_password_hash(self.contrasena_hash, clave)


class Mensaje(db.Model):
    """Mensajes del formulario de contacto (Función 16)."""
    __tablename__ = "mensajes"

    id = db.Column(db.Integer, primary_key=True)
    usuario_id = db.Column(db.Integer, db.ForeignKey("usuarios.id", ondelete="SET NULL"), nullable=True)
    nombre = db.Column(db.String(100), nullable=False)
    correo = db.Column(db.String(150), nullable=False)
    asunto = db.Column(db.String(150), nullable=False)
    mensaje = db.Column(db.Text, nullable=False)
    leido = db.Column(db.Boolean, nullable=False, default=False)
    creado_en = db.Column(db.DateTime, nullable=False, default=reloj.ahora)
