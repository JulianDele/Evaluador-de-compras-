"""
Conexión a base de datos con SQLAlchemy.
"""
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from typing import Generator
from app.config import settings
import os
import sys

db_url = os.environ.get("DATABASE_URL") or settings.database_url

try:
    engine = create_engine(
        db_url,
        pool_pre_ping=True,
        pool_size=settings.db_pool_size,
        max_overflow=settings.db_max_overflow,
    )
except Exception as exc:
    # Mensaje claro para errores de parseo de DATABASE_URL en logs
    print(f"FATAL: No se pudo inicializar la conexión a la base de datos. URL usada: {db_url}", file=sys.stderr)
    print(f"Detalle del error: {exc}", file=sys.stderr)
    raise

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def get_db() -> Generator[Session, None, None]:
    """Dependencia de FastAPI para obtener sesión de BD."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
