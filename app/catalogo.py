"""Contenido fijo de la aplicación: deportes, objetivos, ejercicios y rutinas.

Todo vive aquí (y no en la base de datos) para poder leerlo y editarlo fácilmente.
"""

# ───────────────────────── Frecuencia de ejercicio (registro) ─────────────────────────
FRECUENCIAS = {
    "nunca":     {"nombre": "Casi nunca",              "factor": 0.7},
    "ocasional": {"nombre": "De vez en cuando",        "factor": 1.0},
    "frecuente": {"nombre": "Sí, con frecuencia",      "factor": 1.3},
}

# ───────────────────────── 7 grupos de edad ─────────────────────────
GRUPOS_EDAD = [
    {"clave": "g1", "nombre": "10 a 12 años", "min": 10, "max": 12,  "factor": 0.60,
     "nota": "Que sea un juego. Descansa cuando lo pidas y toma agua."},
    {"clave": "g2", "nombre": "13 a 15 años", "min": 13, "max": 15,  "factor": 0.80,
     "nota": "Cuida la técnica antes de subir repeticiones."},
    {"clave": "g3", "nombre": "16 a 17 años", "min": 16, "max": 17,  "factor": 0.95,
     "nota": "Tu cuerpo aún está creciendo: alterna días fuertes con días suaves."},
    {"clave": "g4", "nombre": "18 a 25 años", "min": 18, "max": 25,  "factor": 1.00,
     "nota": "Rutina base. Sube poco a poco cuando te sientas cómodo."},
    {"clave": "g5", "nombre": "26 a 35 años", "min": 26, "max": 35,  "factor": 0.90,
     "nota": "Calienta 5 minutos antes de empezar."},
    {"clave": "g6", "nombre": "36 a 50 años", "min": 36, "max": 50,  "factor": 0.75,
     "nota": "Prioriza la movilidad y haz pausas entre series."},
    {"clave": "g7", "nombre": "51 años o más", "min": 51, "max": 120, "factor": 0.60,
     "nota": "Ve a tu ritmo. Si algo duele o te marea, detente y consulta a tu médico."},
]

# ───────────────────────── Objetivos personales ─────────────────────────
OBJETIVOS = {
    "bajar_peso": {
        "nombre": "Bajar de peso",
        "resumen": "Cardio y movimientos de cuerpo completo para gastar más energía.",
        "icono": "☀️",
        "color": "#FFB020",
        "ejercicios": [("jumping_jacks", 40), ("sentadillas", 20), ("escaladores", 30),
                       ("rodillas_altas", 45), ("burpees", 10), ("plancha", 30)],
    },
    "ganar_musculo": {
        "nombre": "Ganar masa muscular",
        "resumen": "Fuerza con tu propio peso para trabajar piernas, pecho, espalda y abdomen.",
        "icono": "💪",
        "color": "#E2563B",
        "ejercicios": [("flexiones", 15), ("sentadillas", 25), ("zancadas", 20),
                       ("fondos_silla", 12), ("puente_gluteo", 20), ("superman", 15), ("plancha", 40)],
    },
    "mantenerse_activo": {
        "nombre": "Mantenerse activo",
        "resumen": "Una mezcla ligera de cardio, fuerza y estiramiento para moverte cada día.",
        "icono": "🌍",
        "color": "#3DDC97",
        "ejercicios": [("jumping_jacks", 30), ("sentadillas", 15), ("flexiones_rodillas", 10),
                       ("zancadas", 12), ("plancha", 20), ("estiramiento", 60)],
    },
}

# ───────────────────────── Ejercicios ─────────────────────────
# unidad: rep (repeticiones) · seg (segundos) · min (minutos)
EJERCICIOS = {
    "jumping_jacks":     {"nombre": "Saltos de tijera",     "unidad": "rep", "grupo": "Cardio",
                          "como": "De pie, salta abriendo piernas y brazos a la vez; vuelve a juntar."},
    "sentadillas":       {"nombre": "Sentadillas",          "unidad": "rep", "grupo": "Piernas",
                          "como": "Pies al ancho de hombros, baja la cadera como si te sentaras y sube empujando el piso."},
    "escaladores":       {"nombre": "Escaladores",          "unidad": "rep", "grupo": "Cardio y abdomen",
                          "como": "En posición de plancha, lleva una rodilla al pecho y cambia de pierna con ritmo."},
    "rodillas_altas":    {"nombre": "Rodillas altas",       "unidad": "seg", "grupo": "Cardio",
                          "como": "Trota en el lugar subiendo las rodillas a la altura de la cadera."},
    "burpees":           {"nombre": "Burpees",              "unidad": "rep", "grupo": "Cuerpo completo",
                          "como": "Agáchate, lanza los pies atrás, regresa y salta con los brazos arriba."},
    "plancha":           {"nombre": "Plancha",              "unidad": "seg", "grupo": "Abdomen",
                          "como": "Apoya antebrazos y puntas de los pies; mantén el cuerpo recto como una tabla."},
    "flexiones":         {"nombre": "Flexiones",            "unidad": "rep", "grupo": "Pecho y brazos",
                          "como": "Manos bajo los hombros, baja el pecho al piso y empuja hacia arriba."},
    "flexiones_rodillas":{"nombre": "Flexiones con rodillas", "unidad": "rep", "grupo": "Pecho y brazos",
                          "como": "Igual que una flexión, pero con las rodillas apoyadas en el piso."},
    "zancadas":          {"nombre": "Zancadas",             "unidad": "rep", "grupo": "Piernas",
                          "como": "Da un paso largo al frente, baja la rodilla de atrás y regresa. Alterna piernas."},
    "fondos_silla":      {"nombre": "Fondos en silla",      "unidad": "rep", "grupo": "Brazos (tríceps)",
                          "como": "Manos en el borde de una silla firme; baja y sube flexionando los codos hacia atrás."},
    "puente_gluteo":     {"nombre": "Puente de glúteo",     "unidad": "rep", "grupo": "Glúteos",
                          "como": "Boca arriba con rodillas dobladas, sube la cadera y aprieta glúteos arriba."},
    "superman":          {"nombre": "Superman",             "unidad": "rep", "grupo": "Espalda",
                          "como": "Boca abajo, levanta brazos y piernas a la vez y sostén un segundo."},
    "estiramiento":      {"nombre": "Estiramiento general", "unidad": "seg", "grupo": "Movilidad",
                          "como": "Estira cuello, hombros, espalda y piernas sin rebotes; respira profundo."},
}

UNIDADES = {
    "rep": {"singular": "repetición", "plural": "repeticiones", "corto": "rep"},
    "seg": {"singular": "segundo", "plural": "segundos", "corto": "s"},
    "min": {"singular": "minuto", "plural": "minutos", "corto": "min"},
}

# Valores rápidos de los botones "+" según la unidad
INCREMENTOS = {"rep": (5, 10), "seg": (15, 30), "min": (5, 10)}


# ───────────────────────── Funciones de ayuda ─────────────────────────
def indice_grupo_edad(edad):
    """Devuelve el índice (0-6) del grupo de edad. Sin edad se usa el grupo base (18-25)."""
    if not edad:
        return 3
    for i, g in enumerate(GRUPOS_EDAD):
        if g["min"] <= edad <= g["max"]:
            return i
    return 3 if edad > 0 else 0


def _redondear(n: float) -> int:
    if n < 20:
        return max(5, round(n))
    return int(round(n / 5.0) * 5)


def meta_ejercicio(base: int, factor_edad: float, factor_frecuencia: float) -> int:
    return _redondear(base * factor_edad * factor_frecuencia)


def rutina(objetivo: str, indice_edad: int, frecuencia: str = "ocasional"):
    """Lista de ejercicios con su meta diaria para un objetivo, grupo de edad y frecuencia."""
    obj = OBJETIVOS.get(objetivo) or OBJETIVOS["mantenerse_activo"]
    f_edad = GRUPOS_EDAD[indice_edad]["factor"]
    f_frec = FRECUENCIAS.get(frecuencia, FRECUENCIAS["ocasional"])["factor"]
    salida = []
    for clave, base in obj["ejercicios"]:
        e = EJERCICIOS[clave]
        salida.append({
            "clave": clave, "nombre": e["nombre"], "unidad": e["unidad"],
            "grupo": e["grupo"], "como": e["como"],
            "meta": meta_ejercicio(base, f_edad, f_frec),
        })
    return salida


def rutina_para_usuario(objetivo, edad, frecuencia):
    return rutina(objetivo or "mantenerse_activo", indice_grupo_edad(edad), frecuencia or "ocasional")


def rutinas_por_grupo(objetivo: str, frecuencia: str = "ocasional"):
    """Las 7 listas de ejercicios (una por grupo de edad) de un objetivo."""
    return [{"grupo": g, "ejercicios": rutina(objetivo, i, frecuencia)} for i, g in enumerate(GRUPOS_EDAD)]


def texto_meta(unidad: str, cantidad: int) -> str:
    u = UNIDADES[unidad]
    return f"{cantidad} {u['singular'] if cantidad == 1 else u['plural']}"


# ───────────────────────── Deportes ─────────────────────────
# met: equivalente metabólico para estimar calorías (MET × 3.5 × kg / 200 × minutos)
DEPORTES = {
    "futbol": {
        "nombre": "Fútbol", "icono": "⚽", "color": "#3B8EEA", "planeta": "Tierra", "met": 7.0,
        "resumen": "Dos equipos de 11 jugadores buscan meter el balón en la portería rival.",
        "reglas": [
            "Se juega con los pies; solo el portero puede usar las manos dentro de su área.",
            "Un partido dura 90 minutos, en dos tiempos de 45.",
            "Gana quien anota más goles; si hay empate, puede haber tiempo extra o penales.",
            "El fuera de lugar y las faltas se sancionan con tiros libres, penales o tarjetas.",
        ],
        "beneficios": ["Mejora la resistencia cardiovascular", "Fortalece piernas y equilibrio",
                       "Se aprende el trabajo en equipo", "Se puede jugar casi en cualquier lugar"],
        "equipo": ["Balón", "Espinilleras", "Tenis o tachones", "Ropa cómoda y agua"],
        "practica": ["Pases con la cara interna del pie contra la pared (3 × 20)",
                     "Conducción de balón entre conos o botellas",
                     "Tiros a portería con ambas piernas"],
    },
    "basquetbol": {
        "nombre": "Básquetbol", "icono": "🏀", "color": "#E2563B", "planeta": "Marte", "met": 6.5,
        "resumen": "Dos equipos de 5 jugadores encestan el balón en el aro contrario.",
        "reglas": [
            "Para avanzar con el balón hay que botarlo; no se puede caminar con él en las manos.",
            "Una canasta vale 2 puntos; desde detrás de la línea de tres, 3; un tiro libre, 1.",
            "El partido se divide en cuatro cuartos.",
            "Se pita falta por contacto ilegal y el jugador afectado puede tirar libres.",
        ],
        "beneficios": ["Trabaja coordinación mano-ojo", "Mejora salto y velocidad",
                       "Entrena la toma rápida de decisiones", "Cuida la salud del corazón"],
        "equipo": ["Balón de básquetbol", "Tenis con buen soporte de tobillo", "Aro o cancha", "Agua"],
        "practica": ["Bote con mano derecha e izquierda caminando (5 min)",
                     "Tiros libres: 3 series de 10",
                     "Entradas a canasta alternando lados"],
    },
    "natacion": {
        "nombre": "Natación", "icono": "🏊", "color": "#5B7CFA", "planeta": "Neptuno", "met": 6.0,
        "resumen": "Desplazarte en el agua usando brazos, piernas y respiración coordinada.",
        "reglas": [
            "Los cuatro estilos son libre, dorso, pecho y mariposa.",
            "En competencia hay que respetar el estilo y tocar la pared al girar y al llegar.",
            "Nunca nades solo ni sin supervisión.",
            "Entra al agua después de calentar y evita comer pesado justo antes.",
        ],
        "beneficios": ["Ejercicio completo de bajo impacto", "Cuida articulaciones y espalda",
                       "Mejora la capacidad pulmonar", "Ideal para todas las edades"],
        "equipo": ["Traje de baño", "Gorra y googles", "Toalla", "Agua para después"],
        "practica": ["Patada con tabla: 4 × 25 m",
                     "Respiración lateral: 10 repeticiones por lado",
                     "Nado suave continuo: 10 minutos"],
    },
    "voleibol": {
        "nombre": "Voleibol", "icono": "🏐", "color": "#F0A04B", "planeta": "Venus", "met": 4.0,
        "resumen": "Dos equipos de 6 pasan el balón sobre la red y evitan que toque su cancha.",
        "reglas": [
            "Cada equipo tiene máximo 3 toques para devolver el balón.",
            "Un mismo jugador no puede tocar el balón dos veces seguidas.",
            "Los sets se juegan a 25 puntos con diferencia de 2; gana quien consigue 3 sets.",
            "Los jugadores rotan una posición cada vez que recuperan el saque.",
        ],
        "beneficios": ["Mejora salto y coordinación", "Fortalece hombros y piernas",
                       "Fomenta la comunicación en equipo", "Poco contacto físico"],
        "equipo": ["Balón de voleibol", "Red", "Rodilleras (opcional)", "Tenis ligeros"],
        "practica": ["Toque de dedos contra la pared (3 × 20)",
                     "Antebrazos en parejas: 5 minutos",
                     "Saques desde la línea: 20 intentos"],
    },
    "box": {
        "nombre": "Box", "icono": "🥊", "color": "#C98B5B", "planeta": "Júpiter", "met": 7.8,
        "resumen": "Dos boxeadores se enfrentan en un ring por rounds, usando solo los puños con técnica y control.",
        "reglas": [
            "Solo se golpea con la parte frontal del guante y por encima de la cintura.",
            "Está prohibido golpear la nuca, la espalda, abajo del cinturón o a un rival caído.",
            "El combate se divide en rounds con descansos entre ellos; en amateur suelen ser 3 rounds de 3 minutos.",
            "Se ganan puntos por golpes limpios y gana quien suma más, o por decisión del árbitro si hay riesgo.",
        ],
        "beneficios": ["Mejora la resistencia y quema muchas calorías", "Desarrolla reflejos y coordinación",
                       "Fortalece hombros, core y piernas", "Ayuda a liberar el estrés y a ganar disciplina"],
        "equipo": ["Guantes", "Vendas para las manos", "Protector bucal", "Ropa cómoda, tenis y agua"],
        "practica": ["Boxeo de sombra: 3 rounds de 2 minutos frente al espejo",
                     "Postura y desplazamientos: pasos laterales y hacia atrás (5 min)",
                     "Jab y cruzado al costal: 3 series de 1 minuto con descanso",
                     "Salto de cuerda: 3 series de 1 minuto"],
    },
}

# Actividades que se pueden registrar (Función 8) con su MET
TIPOS_ACTIVIDAD = {
    **{d["nombre"]: d["met"] for d in DEPORTES.values()},
    "Caminar": 3.5, "Correr": 8.0, "Bicicleta": 6.0,
    "Ejercicio en casa": 5.0, "Gimnasio": 5.0, "Otra actividad": 4.0,
}

ESFUERZOS = {"suave": 0.85, "medio": 1.0, "intenso": 1.2}


def calorias_estimadas(tipo: str, minutos: int, peso_kg, esfuerzo: str = "medio") -> float:
    met = TIPOS_ACTIVIDAD.get(tipo, 4.0) * ESFUERZOS.get(esfuerzo, 1.0)
    peso = peso_kg if peso_kg else 70
    return round(met * 3.5 * peso / 200 * minutos, 1)


# ───────────────────────── Novedades ─────────────────────────
TIPOS_NOVEDAD = {
    "noticia": "Noticia", "evento": "Evento", "torneo": "Torneo", "consejo": "Consejo",
}
ESTADOS_NOVEDAD = {"publicada": "Publicada", "borrador": "Borrador", "archivada": "Archivada"}


# ───────────────────────── Prevención de adicciones ─────────────────────────
PREVENCION = [
    {"clave": "alcohol", "titulo": "Alcohol",
     "resumen": "Es la sustancia más normalizada y por eso se subestima.",
     "puntos": [
         "Afecta la coordinación, la memoria y la toma de decisiones, incluso en pocas cantidades.",
         "En personas menores de 18 años interfiere con el desarrollo del cerebro.",
         "Beber y hacer deporte no se llevan: deshidrata y aumenta el riesgo de lesiones.",
     ],
     "senales": ["Beber para sentirte bien o para relajarte todos los días",
                 "Faltar a clases, entrenamientos o al trabajo por la resaca",
                 "Mentir sobre cuánto se consume"]},
    {"clave": "tabaco", "titulo": "Tabaco y vapeadores",
     "resumen": "Los vapeadores no son inofensivos: casi todos contienen nicotina.",
     "puntos": [
         "La nicotina genera dependencia rápido, también en formato de vapeador.",
         "Reduce la capacidad pulmonar: lo notas al correr o subir escaleras.",
         "El aerosol de los vapeadores contiene sustancias que irritan y dañan los pulmones.",
     ],
     "senales": ["Sentir ansiedad o irritabilidad si pasas un rato sin fumar o vapear",
                 "Cansarte mucho más rápido al hacer ejercicio",
                 "Fumar o vapear a escondidas"]},
    {"clave": "drogas", "titulo": "Drogas ilegales y medicamentos sin receta",
     "resumen": "Probar una vez ya es un riesgo: no sabes qué contiene lo que te dan.",
     "puntos": [
         "Muchas sustancias se mezclan con otras que aumentan el riesgo de sobredosis.",
         "Los medicamentos controlados sin receta también pueden generar dependencia.",
         "La mayoría de las personas jóvenes no consume; la presión de grupo se siente mayor de lo que es.",
     ],
     "senales": ["Cambios bruscos de humor, sueño o amistades",
                 "Dejar de disfrutar actividades que antes te gustaban",
                 "Pedir dinero con frecuencia sin explicar para qué"]},
    {"clave": "pantallas", "titulo": "Pantallas, videojuegos y redes",
     "resumen": "No es una sustancia, pero también puede volverse una dependencia.",
     "puntos": [
         "Es un problema cuando desplaza el sueño, el estudio, el movimiento o la convivencia.",
         "Las apuestas en línea y los gastos dentro de juegos pueden convertirse en un hábito difícil de controlar.",
         "Poner horarios sin pantalla y salir a moverte ayuda a recuperar el equilibrio.",
     ],
     "senales": ["Sentir enojo o angustia al no tener el celular",
                 "Dormir menos de lo necesario por jugar o navegar",
                 "Gastar dinero en juegos o apuestas a escondidas"]},
]

FORMAS_DE_DECIR_NO = [
    "Di “no, gracias” con calma y sigue en lo tuyo; no necesitas dar explicaciones largas.",
    "Propón otro plan: “Mejor vamos a jugar fut o a caminar”.",
    "Usa una excusa que funcione: “Tengo entrenamiento mañana temprano”.",
    "Aléjate de la situación. Irte también es una respuesta válida.",
    "Cuéntale a una persona de confianza lo que pasó; no tienes que cargarlo solo.",
]

AYUDA_MEXICO = {
    "nombre": "Línea de la Vida",
    "telefono": "800 911 2000",
    "descripcion": "Atención gratuita y confidencial sobre salud mental y adicciones, las 24 horas. "
                   "Verifica el número vigente en el sitio oficial de la Secretaría de Salud.",
}

# ───────────────────────── Tutorial ─────────────────────────
PASOS_TUTORIAL = [
    {"titulo": "Crea tu cuenta y elige tu objetivo",
     "texto": "Al registrarte indica tu edad y si haces ejercicio con frecuencia. Después elige si quieres bajar de peso, ganar masa muscular o mantenerte activo.",
     "icono": "user"},
    {"titulo": "Haz tu reto diario",
     "texto": "En «Reto diario» verás tus ejercicios de hoy. Suma repeticiones durante el día, en tandas, hasta llegar al 100 %.",
     "icono": "reto"},
    {"titulo": "Conoce los deportes",
    "texto": "En «Deportes» encuentras reglas, beneficios y ejercicios de práctica de fútbol, básquetbol, voleibol, natación y box.",
     "icono": "deportes"},
    {"titulo": "Anota tus pasos",
     "texto": "En «Pasos» captura cuántos diste hoy. La meta diaria es de 6,000.",
     "icono": "pasos"},
    {"titulo": "Revisa tu rutina",
     "texto": "«Mi rutina» muestra los ejercicios de tu objetivo para cada grupo de edad, con tu grupo resaltado.",
     "icono": "rutina"},
    {"titulo": "Mide tu progreso",
     "texto": "En «Mi progreso» ves tu racha, tus minutos y tus calorías. El historial guarda cada día.",
     "icono": "chart"},
    {"titulo": "Cuida tu alimentación",
     "texto": "En «Alimentación» encuentras ideas de comidas para tu objetivo, información nutricional de alimentos comunes y consejos para hidratarte. En «Deportes» puedes marcar tus favoritos con la estrella.",
     "icono": "alimentacion"},
    {"titulo": "Compite y personaliza",
     "texto": "Mira tu lugar en la «Clasificación» y crea tu personaje en «Avatar».",
     "icono": "trophy"},
    {"titulo": "Usa el menú",
     "texto": "El botón de arriba a la derecha abre el menú con Perfil, Clasificación, Avatar, Mi progreso, Alimentación, Prevención, Contacto, Tutorial y Salir.",
     "icono": "menu"},
]


# ───────────────────────── Tema espacial: rangos de la clasificación ─────────────────────────
RANGOS = [(800, "Estrella", "⭐"), (400, "Planeta", "🪐"), (150, "Luna", "🌙"),
          (50, "Asteroide", "☄️"), (0, "Polvo estelar", "🌌")]


def rango(puntos: int) -> dict:
    for minimo, nombre, icono in RANGOS:
        if puntos >= minimo:
            return {"nombre": nombre, "icono": icono, "minimo": minimo}
    return {"nombre": "Polvo estelar", "icono": "🌌", "minimo": 0}


# ───────────────────────── Alimentación ─────────────────────────
# Valores aproximados por 100 g (tablas de composición de alimentos); cambian según la preparación.
ALIMENTACION = {
    "grupos": {
        "energia": "Energía (cereales)",
        "proteina": "Proteínas",
        "frutas_verduras": "Frutas y verduras",
        "grasas": "Grasas saludables",
    },
    "alimentos": [
        {"nombre": "Tortilla de maíz", "grupo": "energia", "emoji": "🫓", "kcal": 218, "proteina": 5.7, "carbos": 44.6, "grasa": 2.9,
         "porcion": "2 o 3 tortillas", "nota": "Aporta energía y fibra; combina bien con frijoles."},
        {"nombre": "Arroz cocido", "grupo": "energia", "emoji": "🍚", "kcal": 130, "proteina": 2.7, "carbos": 28.0, "grasa": 0.3,
         "porcion": "½ taza", "nota": "Fuente rápida de energía antes de entrenar."},
        {"nombre": "Avena (hojuelas)", "grupo": "energia", "emoji": "🥣", "kcal": 389, "proteina": 16.9, "carbos": 66.0, "grasa": 6.9,
         "porcion": "½ taza cruda", "nota": "Tiene fibra que sacia; agrégale fruta en lugar de azúcar."},
        {"nombre": "Huevo cocido", "grupo": "proteina", "emoji": "🥚", "kcal": 155, "proteina": 13.0, "carbos": 1.1, "grasa": 11.0,
         "porcion": "1 o 2 piezas", "nota": "Proteína completa y fácil de preparar."},
        {"nombre": "Pechuga de pollo cocida", "grupo": "proteina", "emoji": "🍗", "kcal": 165, "proteina": 31.0, "carbos": 0.0, "grasa": 3.6,
         "porcion": "1 palma de la mano", "nota": "Mucha proteína con poca grasa; mejor asada o cocida."},
        {"nombre": "Atún en agua", "grupo": "proteina", "emoji": "🐟", "kcal": 116, "proteina": 25.5, "carbos": 0.0, "grasa": 0.8,
         "porcion": "1 lata pequeña", "nota": "Práctico para llevar; escurre bien el agua."},
        {"nombre": "Frijoles cocidos", "grupo": "proteina", "emoji": "🫘", "kcal": 127, "proteina": 8.7, "carbos": 22.8, "grasa": 0.5,
         "porcion": "½ taza", "nota": "Proteína vegetal, fibra y hierro a bajo costo."},
        {"nombre": "Lentejas cocidas", "grupo": "proteina", "emoji": "🥘", "kcal": 116, "proteina": 9.0, "carbos": 20.1, "grasa": 0.4,
         "porcion": "½ taza", "nota": "Se cocinan rápido y rinden mucho."},
        {"nombre": "Yogur natural", "grupo": "proteina", "emoji": "🥛", "kcal": 61, "proteina": 3.5, "carbos": 4.7, "grasa": 3.3,
         "porcion": "1 vaso chico", "nota": "Elige el natural sin azúcar y ponle fruta."},
        {"nombre": "Plátano", "grupo": "frutas_verduras", "emoji": "🍌", "kcal": 89, "proteina": 1.1, "carbos": 22.8, "grasa": 0.3,
         "porcion": "1 pieza", "nota": "Buena colación antes o después de hacer ejercicio."},
        {"nombre": "Manzana", "grupo": "frutas_verduras", "emoji": "🍎", "kcal": 52, "proteina": 0.3, "carbos": 13.8, "grasa": 0.2,
         "porcion": "1 pieza", "nota": "Con cáscara aporta fibra."},
        {"nombre": "Papaya", "grupo": "frutas_verduras", "emoji": "🧡", "kcal": 43, "proteina": 0.5, "carbos": 10.8, "grasa": 0.3,
         "porcion": "1 taza picada", "nota": "Hidrata y ayuda a la digestión."},
        {"nombre": "Nopal cocido", "grupo": "frutas_verduras", "emoji": "🌵", "kcal": 22, "proteina": 2.0, "carbos": 4.9, "grasa": 0.4,
         "porcion": "1 taza", "nota": "Muy ligero y con fibra; va bien en ensaladas y guisados."},
        {"nombre": "Aguacate", "grupo": "grasas", "emoji": "🥑", "kcal": 160, "proteina": 2.0, "carbos": 8.5, "grasa": 14.7,
         "porcion": "⅓ de pieza", "nota": "Grasa saludable; es calórico, así que con moderación."},
        {"nombre": "Cacahuate natural", "grupo": "grasas", "emoji": "🥜", "kcal": 567, "proteina": 25.8, "carbos": 16.1, "grasa": 49.2,
         "porcion": "un puñito", "nota": "Mucha energía en poco volumen; mejor sin sal ni azúcar."},
    ],
    "plato": [
        {"nombre": "Verduras y frutas", "color": "#3DDC97", "texto": "Llena una parte de tu plato; varía colores."},
        {"nombre": "Cereales", "color": "#FFC93C", "texto": "Tortilla, arroz, avena o pan; mejor integrales."},
        {"nombre": "Leguminosas y alimentos de origen animal", "color": "#E2563B", "texto": "Frijoles, lentejas, huevo, pollo, pescado o lácteos."},
    ],
    "objetivos": {
        "bajar_peso": {
            "titulo": "Para bajar de peso",
            "puntos": [
                "Come tres comidas al día y no te saltes el desayuno: llegar con mucha hambre hace comer de más.",
                "Llena la mitad del plato con verduras y toma agua en lugar de refrescos y jugos.",
                "Sirve porciones moderadas, come despacio y evita repetir por costumbre.",
                "Cambia las frituras y los dulces por fruta, jícama o yogur natural.",
                "Evita dietas extremas o dejar de comer: bajan tu energía y te quitan ganas de moverte.",
            ],
            "dia": [("Desayuno", "Avena con manzana picada y un huevo cocido."),
                    ("Comida", "Pollo asado, ensalada de nopales y una tortilla."),
                    ("Colación", "Jícama o papaya con limón."),
                    ("Cena", "Frijoles con verduras y una tortilla.")],
        },
        "ganar_musculo": {
            "titulo": "Para ganar masa muscular",
            "puntos": [
                "Incluye una fuente de proteína en cada comida: huevo, pollo, atún, frijoles, lentejas o lácteos.",
                "No olvides los cereales: dan la energía para entrenar y recuperarte.",
                "Come algo después de entrenar, con proteína y carbohidratos.",
                "Agrega grasas saludables, como aguacate o cacahuates, sin pasarte.",
                "Duerme bien: el músculo se recupera mientras descansas.",
            ],
            "dia": [("Desayuno", "Huevos con frijoles, tortillas y fruta."),
                    ("Comida", "Pollo con arroz, verduras y aguacate."),
                    ("Colación", "Yogur natural con plátano y avena."),
                    ("Cena", "Atún o lentejas con verduras y tortilla.")],
        },
        "mantenerse_activo": {
            "titulo": "Para mantenerte activo",
            "puntos": [
                "Arma tu plato con verduras o frutas, un cereal y una leguminosa o proteína animal.",
                "Come a tus horas y varía: así recibes distintos nutrientes.",
                "Toma agua a lo largo del día, no solo cuando tienes sed.",
                "Deja los dulces, las frituras y los refrescos para ocasiones especiales.",
                "Come con calma y escucha cuándo tienes hambre y cuándo ya estás satisfecho.",
            ],
            "dia": [("Desayuno", "Yogur natural con avena y plátano."),
                    ("Comida", "Frijoles, arroz, verduras y un huevo."),
                    ("Colación", "Una fruta de temporada."),
                    ("Cena", "Quesadilla de nopales con tortilla de maíz.")],
        },
    },
    "hidratacion": [
        "Toma agua natural a lo largo del día; no esperes a tener mucha sed.",
        "Bebe un poco más cuando haga calor o cuando hagas ejercicio, antes, durante y después.",
        "Si tu orina es muy oscura o te duele la cabeza, probablemente necesitas más agua.",
        "Los refrescos, jugos y bebidas energéticas llevan mucha azúcar; el agua es la mejor opción.",
        "Si sudas mucho durante más de una hora, consulta a un profesional sobre cómo reponer líquidos.",
    ],
}
