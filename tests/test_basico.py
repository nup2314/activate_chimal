"""Pruebas básicas. Ejecuta con:  pip install pytest  y luego  pytest -q"""
import pytest

from app import create_app
from app.config import Config
from app.extensions import db
from app.models import Personal, Usuario


class ConfigPrueba(Config):
    TESTING = True
    SQLALCHEMY_DATABASE_URI = "sqlite:///:memory:"
    WTF_CSRF_ENABLED = False
    SECRET_KEY = "clave-de-pruebas"
    SESSION_COOKIE_SECURE = False


@pytest.fixture()
def app():
    app = create_app(ConfigPrueba)
    with app.app_context():
        db.create_all()
        yield app
        db.session.remove()
        db.drop_all()


@pytest.fixture()
def cliente(app):
    return app.test_client()


DATOS = {"nombre": "Ana", "apellidos": "López", "correo": "ana@correo.com", "edad": "16",
         "frecuencia": "ocasional", "contrasena": "Clave1234", "confirmar": "Clave1234"}


def registrar(cliente, **extra):
    return cliente.post("/cuenta/registro", data={**DATOS, **extra}, follow_redirects=True)


def test_portada_publica(cliente):
    assert cliente.get("/").status_code == 200


def test_rutas_privadas_piden_sesion(cliente):
    for ruta in ("/reto", "/pasos", "/estadisticas", "/perfil/", "/clasificacion"):
        r = cliente.get(ruta)
        assert r.status_code == 302 and "/cuenta/entrar" in r.headers["Location"]


def test_registro_y_login(cliente, app):
    r = registrar(cliente)
    assert r.status_code == 200
    u = Usuario.query.filter_by(correo="ana@correo.com").first()
    assert u is not None and u.contrasena_hash != "Clave1234" and u.revisar_contrasena("Clave1234")
    cliente.post("/cuenta/salir")
    r = cliente.post("/cuenta/entrar", data={"correo": "ana@correo.com", "contrasena": "Clave1234"})
    assert r.status_code == 302


def test_registro_rechaza_datos_invalidos(cliente):
    registrar(cliente, edad="5")
    registrar(cliente, contrasena="corta", confirmar="corta")
    assert Usuario.query.count() == 0


def test_correo_duplicado(cliente):
    registrar(cliente)
    cliente.post("/cuenta/salir")
    registrar(cliente)
    assert Usuario.query.count() == 1


def test_bloqueo_por_intentos(cliente, app):
    registrar(cliente)
    cliente.post("/cuenta/salir")
    for _ in range(app.config["LOGIN_MAX_INTENTOS"]):
        cliente.post("/cuenta/entrar", data={"correo": "ana@correo.com", "contrasena": "mala"})
    r = cliente.post("/cuenta/entrar", data={"correo": "ana@correo.com", "contrasena": "Clave1234"})
    assert r.status_code == 200  # sigue bloqueada aunque la clave sea correcta


def test_reto_se_acumula_hasta_100(cliente):
    registrar(cliente)
    cliente.post("/objetivos", data={"objetivo": "mantenerse_activo"})
    u = Usuario.query.first()
    from app import servicios
    for e in servicios.reto_del_dia(u)["ejercicios"]:
        servicios.cambiar_progreso(u, e["clave"], "sumar", e["meta"])
    assert servicios.reto_del_dia(u)["porcentaje"] == 100


def test_pasos_y_meta(cliente):
    registrar(cliente)
    cliente.post("/pasos", data={"cantidad": "4000", "modo": "sumar"})
    cliente.post("/pasos", data={"cantidad": "2500", "modo": "sumar"})
    from app import servicios
    assert servicios.pasos_de(Usuario.query.first().id) == 6500


def test_actividad_y_historial(cliente):
    registrar(cliente)
    r = cliente.post("/actividades/nueva", data={"tipo": "Correr", "tiempo": "30", "esfuerzo": "medio",
                                                 "fecha": __import__("app.tiempo", fromlist=["x"]).hoy().isoformat()})
    assert r.status_code == 302
    assert b"Correr" in cliente.get("/historial").data


def test_personal_no_entra_como_usuario(cliente):
    assert cliente.get("/personal/").status_code == 302
    p = Personal(usuario="maria"); p.poner_contrasena("Personal123"); db.session.add(p); db.session.commit()
    r = cliente.post("/personal/acceso", data={"usuario": "maria", "contrasena": "Personal123"})
    assert r.status_code == 302
    assert cliente.get("/personal/").status_code == 200


def test_eliminar_cuenta(cliente):
    registrar(cliente)
    cliente.post("/perfil/eliminar", data={"confirmar": "ELIMINAR", "contrasena": "Clave1234"})
    assert Usuario.query.count() == 0


def test_favoritos_de_deportes(cliente):
    registrar(cliente)
    from app.models import DeporteFavorito
    cliente.post("/deportes/futbol/favorito")
    assert DeporteFavorito.query.count() == 1
    assert b"Mis favoritos (1)" in cliente.get("/deportes").data
    cliente.post("/deportes/futbol/favorito")          # segunda vez lo quita
    assert DeporteFavorito.query.count() == 0
    assert cliente.post("/deportes/no_existe/favorito").status_code == 404


def test_alimentacion_y_nombre_mi_progreso(cliente):
    registrar(cliente)
    cliente.post("/objetivos", data={"objetivo": "ganar_musculo"})
    r = cliente.get("/alimentacion")
    assert r.status_code == 200 and "Para ganar masa muscular".encode() in r.data
    assert cliente.get("/alimentacion?grupo=proteina").status_code == 200
    assert b"Mi progreso" in cliente.get("/estadisticas").data


def test_favorito_responde_json_para_el_javascript(cliente):
    registrar(cliente)
    r = cliente.post("/deportes/tenis/favorito", headers={"X-Requested-With": "fetch"})
    assert r.status_code == 200 and r.get_json() == {"favorito": True, "total": 1}
    r = cliente.post("/deportes/tenis/favorito", headers={"X-Requested-With": "fetch"})
    assert r.get_json() == {"favorito": False, "total": 0}


# ───────── Avatar (astros del sistema solar) ─────────
def test_avatar_normaliza_y_rechaza_valores_peligrosos():
    from app import avatar_config
    D = avatar_config.DEFECTO
    sucio = {"astro": "<script>", "color_base": "rojo", "tamano": 99, "orbita": "x", "color_luna": "#ABCDEF",
             "anillos": "doble", "extra": 1, "cabello": "afro"}
    limpio = avatar_config.normalizar(sucio)
    assert limpio["astro"] == D["astro"]                                  # opción inválida -> valor por defecto
    assert limpio["color_base"] == D["color_base"]                        # color inválido
    assert limpio["tamano"] == avatar_config.CAMPOS["tamano"]["max"]      # número fuera de rango -> se recorta
    assert limpio["orbita"] == D["orbita"]                                # tipo incorrecto
    assert limpio["color_luna"] == "#abcdef" and limpio["anillos"] == "doble"
    assert limpio["extra"] == D["extra"]                                  # tipo incorrecto en una opción
    assert "cabello" not in limpio and set(limpio) == set(D)              # los campos del avatar anterior se descartan
    assert avatar_config.normalizar("no es json") == D


def test_cada_astro_predefinido_es_valido():
    """Los valores de `presets_astro` deben pasar la validación sin que se corrija nada."""
    from app import avatar_config
    for astro, preset in avatar_config.ESQUEMA["presets_astro"].items():
        esperado = {**avatar_config.DEFECTO, **preset, "astro": astro}
        assert avatar_config.normalizar(esperado) == esperado, astro


def test_guardar_avatar_y_mostrarlo(cliente):
    import json
    from app.models import Avatar
    registrar(cliente)
    r = cliente.post("/avatar/", data={"config": json.dumps({"astro": "saturno", "anillos": "ancho", "color_base": "#E3CB8F"})},
                     headers={"X-Requested-With": "fetch"})
    assert r.status_code == 200 and r.get_json() == {"ok": True}
    datos = Avatar.query.first().datos
    assert datos["astro"] == "saturno" and datos["anillos"] == "ancho" and datos["color_base"] == "#e3cb8f"
    assert b"avatar-creador.css" in cliente.get("/avatar/").data
    assert b'data-avatar=' in cliente.get("/perfil/").data


def test_toda_opcion_del_esquema_esta_dibujada_en_el_renderizador():
    """Si añades una opción al JSON y olvidas dibujarla en avatar-core.js, esta prueba falla."""
    import re
    from pathlib import Path
    from app import avatar_config
    js = (Path(avatar_config.__file__).parent / "static" / "js" / "avatar-core.js").read_text(encoding="utf-8")
    sin_dibujo = []
    for campo in ("textura", "anillos", "lunas", "atmosfera", "cara", "fondo", "extra"):
        for op in avatar_config.CAMPOS[campo]["opciones"]:
            if op["id"] not in ("ninguno", "ninguna") and not re.search(rf"\b{op['id']}\b", js):
                sin_dibujo.append((campo, op["id"]))
    assert not sin_dibujo, sin_dibujo
