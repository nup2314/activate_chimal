"""Punto de entrada. Local: `python run.py`  ·  Producción: `gunicorn run:app`."""
from dotenv import load_dotenv

load_dotenv()  # lee .env si existe (no falla si no existe)

from app import create_app  # noqa: E402  (se importa después de cargar .env)

app = create_app()

if __name__ == "__main__":
    app.run(debug=True)
