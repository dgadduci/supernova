import os
from pathlib import Path

from dotenv import load_dotenv


PROJECT_ROOT = Path(__file__).resolve().parents[2]

APP_ENV = os.getenv("APP_ENV", "development")

env_file = PROJECT_ROOT / f".env.{APP_ENV}"

if env_file.exists():
    load_dotenv(dotenv_path=env_file, override=False)

DATABASE_URL = os.getenv("DATABASE_URL")

if not DATABASE_URL:
    raise RuntimeError(
        f"DATABASE_URL no está configurada. "
        f"Entorno actual: {APP_ENV}. "
        f"Archivo buscado: {env_file}"
    )