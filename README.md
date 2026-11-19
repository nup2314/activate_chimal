# Activate + Chimal

Aplicación web en **Flask** para moverte a tu ritmo: reto diario por edad y objetivo, deportes,
pasos, estadísticas, clasificación, avatar y un módulo de personal para publicar novedades.
Reescritura completa a partir del manual del proyecto y de la *Lista general de funciones*.

## Ejecutar en tu computadora (VS Code)

```bash
python -m venv venv
venv\Scripts\activate          # Windows      ·  source venv/bin/activate  (Mac/Linux)
pip install -r requirements.txt
copy .env.example .env         # (cp en Mac/Linux) y cambia SECRET_KEY
python run.py                  # http://127.0.0.1:5000
```

Sin `DATABASE_URL` usa SQLite (`instance/activate_chimal.db`). Las tablas se crean solas.

### Comandos útiles
```bash
flask --app run crear-personal maria     # crea una cuenta del personal (pide contraseña)
flask --app run cargar-demo              # 3 novedades de ejemplo
flask --app run desactivar-personal maria
pytest -q                                # pruebas
```
El módulo de personal está en `/personal/acceso`.

## Estructura

```
run.py  Procfile  requirements.txt  .env.example
app/
  __init__.py      create_app(), errores, filtros, comandos flask
  config.py        SECRET_KEY, DATABASE_URL, reglas (meta 6,000 pasos, código 15 min…)
  models.py        Usuario, Actividad, Paso, ProgresoReto, RetoDia, CodigoRecuperacion,
                   Avatar, Novedad, Personal, Mensaje
  catalogo.py      deportes, objetivos, ejercicios, 7 grupos de edad, prevención, tutorial
  servicios.py     reto diario, pasos, rachas, estadísticas, historial, clasificación
  avatar_svg.py    dibujo del avatar por capas (SVG)
  auth/ perfil/ actividad/ seguimiento/ comunidad/ avatar/ info/ personal/ main/   (Blueprints)
  templates/  static/
tests/
```

## Las 21 funciones y dónde están

| # | Función | Ruta | Código |
|---|---|---|---|
| 1 | Registro | `/cuenta/registro` | `auth/routes.py` |
| 2 | Inicio y cierre de sesión | `/cuenta/entrar`, `/cuenta/salir` | `auth/routes.py` |
| 3 | Recuperación (código 6 dígitos, 15 min, correo SMTP) | `/cuenta/recuperar` | `auth/routes.py`, `utils.enviar_correo` |
| 4 | Perfil: ver, editar, eliminar cuenta | `/perfil/` | `perfil/routes.py` |
| 5 | Deportes (6) | `/deportes` | `actividad/routes.py`, `catalogo.DEPORTES` |
| 6 | Objetivos + ejercicios por 7 grupos de edad | `/objetivos` | `catalogo.py` |
| 7 | Reto diario (repeticiones acumulables) | `/reto` | `servicios.reto_del_dia` |
| 8 | Registrar actividades | `/actividades/nueva` | `actividad/routes.py` |
| 9 | Pasos (meta 6,000) | `/pasos` | `servicios.guardar_pasos` |
| 10 | Mi progreso (estadísticas y rachas) | `/estadisticas` | `servicios.resumen` |
| 11 | Historial | `/historial` | `servicios.historial` |
| 12 | Novedades deportivas | `/novedades` | `comunidad/routes.py` |
| 13 | Clasificación | `/clasificacion` | `servicios.clasificacion` |
| 14 | Avatar: un astro del sistema solar (planeta, anillos, lunas, atmósfera...) en la BD | `/avatar/` | `avatar/routes.py`, `avatar_svg.py` |
| 15 | Prevención de adicciones | `/prevencion` | `info/routes.py` |
| 16 | Contacto | `/contacto` | `info/routes.py` |
| 17 | Tutorial | `/tutorial` | `info/routes.py` |
| 18 | Navegación (barra inferior + menú) | todas | `templates/base.html` |
| 19 | Acceso exclusivo del personal | `/personal/acceso` | `personal/routes.py` |
| 20 | Administrar novedades (crear, editar, publicar, archivar, eliminar) | `/personal/novedades` | `personal/routes.py` |
| 21 | Administración general de contenido (panel + mensajes) | `/personal/` | `personal/routes.py` |

### Mejoras futuras (ya incluidas)
1. **Contador automático de pasos** con el acelerómetro: beta en `/pasos` (estimación; solo funciona con la página abierta).
2. **Envío real de códigos**: SMTP con `MAIL_*`. Sin correo configurado, en modo debug el código aparece en pantalla.
3. **Límite de intentos de inicio de sesión**: 5 fallos = bloqueo de 15 minutos.
4. **Avatar completo en la BD**: tabla `avatares` y dibujo SVG generado en el servidor.

## Puntos de diseño
- **Racha**: un día cuenta si registras actividad, llegas a 6,000 pasos o completas el reto.
- **Puntos de clasificación**: 1 por minuto, 1 por cada 100 pasos, 30 por reto completado.
- **Reto**: meta de cada ejercicio = base del objetivo × factor del grupo de edad × factor de frecuencia de ejercicio.
- **Seguridad**: CSRF en todos los formularios, contraseñas con hash, cookies `HttpOnly/SameSite`, redirecciones solo internas, salida solo por POST.

## Desplegar en Render + Neon
1. Sube el proyecto a GitHub (`.env` y `*.db` están en `.gitignore`).
2. Neon: crea la base y copia su cadena de conexión.
3. Render → *New Web Service*: Build `pip install -r requirements.txt` · Start `gunicorn run:app`.
4. Variables: `SECRET_KEY` (larga y aleatoria), `DATABASE_URL` (Neon), y `MAIL_*` si quieres correo real.
5. Crea el personal desde el *Shell* de Render: `flask --app run crear-personal usuario`.

Cuando cambies los modelos en producción usa migraciones: `flask --app run db init` (una vez), `db migrate`, `db upgrade`.
Las líneas de ayuda de la sección de prevención deben revisarse periódicamente.

## Tema "Sistema solar"
- `static/css/espacio.css` se carga después de `app.css` (en `base.html`). Para volver al diseño claro, borra esa línea `<link>`.
- Cada deporte es un planeta (`catalogo.DEPORTES[...]["planeta"]`), la clasificación usa rangos (`catalogo.RANGOS`: polvo estelar, asteroide, luna, planeta, estrella) y el avatar es un astro del sistema solar que se personaliza.

## Lista de cotejo de Figma (pantallas sugeridas)
Inicio de sesión · Registro · Menú principal · Actividad física · Deportes (con **favoritos** ⭐) · **Alimentación** (`/alimentacion`) · Mi progreso · Perfil.
La alimentación incluye consejos por objetivo, un día de ejemplo, el plato del bien comer, información nutricional aproximada de 15 alimentos comunes e hidratación.

## Mascota e ícono
- La imagen de la mascota está en `app/static/img/` (`mascota.webp` completa, `mascota-cara.png` redonda, favicon, `apple-touch-icon.png`, `icon-192.png` e `icon-512.png`).
- Se usa como logo de la barra, favicon, ícono al "Añadir a pantalla de inicio", figura de la portada y en burbujas de diálogo (inicio, reto, inicio de sesión, registro, tutorial y errores).
- Para ponerle nombre: variable de entorno `MASCOTA_NOMBRE` (por defecto "Tu guía") o `MASCOTA_NOMBRE` en `config.py`.
- Para cambiar la imagen, reemplaza esos archivos conservando los nombres.

## Animaciones
`static/css/animaciones.css` + el final de `static/js/app.js`. Se desactivan solas si el dispositivo tiene "reducir movimiento"; para quitarlas del todo, borra el `<link>` de `animaciones.css` en `base.html`.
Incluye: onda y efecto de presionado al tocar, entrada escalonada de tarjetas, anillos/barras que se llenan, números que suben, estrella de favorito sin recargar, botón "enviando", destello del ejercicio actualizado, mascota que salta al tocarla y confeti al completar el reto o la meta de pasos.


## Creador de avatar (rediseño)
Arquitectura en tres piezas, sin código duplicado:

| Pieza | Archivo | Qué hace |
|---|---|---|
| Esquema (fuente única) | `app/static/data/avatar_esquema.json` | Categorías, opciones, rangos de deslizadores, paletas y valores por defecto |
| Validación | `app/avatar_config.py` | Lee el esquema y limpia lo que llega del navegador (opciones, colores `#rrggbb`, números en rango) |
| Dibujo | `app/static/js/avatar-core.js` | Única implementación del avatar (SVG por capas): 12 astros (Sol, 8 planetas, Luna, Plutón, asteroide) con 8 texturas, 4 tipos de anillos, hasta 3 lunas con órbita, atmósfera, carita, fondo espacial y acompañantes… Lo usan el creador y los avatares pequeños del sitio |
| Interfaz | `app/static/js/avatar-editor.js` + `css/avatar-creador.css` + `templates/avatar/editor.html` | Se genera sola desde el esquema: categorías, miniaturas, colores, deslizadores, deshacer, aleatorio, zoom y guardado |

**Agregar una opción nueva** (por ejemplo una textura): 1) añade su `id` a la sección `textura` del esquema; 2) dibújala en la tabla `TEXTURAS` de `avatar-core.js`. La interfaz, la validación y la miniatura salen solas. La prueba `test_toda_opcion_del_esquema_esta_dibujada...` avisa si olvidas el paso 2.

**Agregar un astro nuevo** (por ejemplo Ceres): añade su `id` a la sección `astro` y su receta en `presets_astro` del esquema (colores, textura, anillos, lunas y atmósfera). No hace falta tocar `avatar-core.js`; solo el Sol (`sol`) y el asteroide (`asteroide`) tienen un dibujo especial. La prueba `test_cada_astro_predefinido_es_valido` revisa que la receta sea válida.

**Cómo funcionan los astros:** al elegir uno en el creador se aplican sus colores, textura, anillos, lunas y atmósfera reales (Saturno con anillos, la Tierra con su Luna, Júpiter con su gran mancha...); después se puede cambiar cada detalle. El botón de dado crea un astro real al azar o, a veces, un mundo inventado.

La configuración se guarda como JSON en la tabla `avatar_config` (la tabla anterior `avatares` ya no se usa y puede borrarse).

**Avatares guardados antes del cambio** (los de persona: piel, cabello, ropa...): sus campos ya no existen, así que `avatar_config.normalizar` los descarta y se muestran como el astro por defecto (la Tierra con su Luna) hasta que la persona los vuelva a editar. No hace falta migrar la base de datos.
