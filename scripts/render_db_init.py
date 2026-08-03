"""
Inicializa y siembra la base de datos de Render.
Uso:
  python scripts/render_db_init.py "postgresql://user:pass@host:port/db"

El script:
- valida la conexión
- crea el esquema si no existe
- inserta usuarios de ejemplo
- muestra el recuento de usuarios
"""
import os
import sys
from pathlib import Path

from passlib.context import CryptContext
from sqlalchemy import create_engine, text
from sqlalchemy.engine import Engine
from sqlalchemy.exc import SQLAlchemyError

SCRIPT_DIR = Path(__file__).resolve().parent
SCHEMA_FILE = SCRIPT_DIR / "schema.sql"

PWD_CONTEXT = CryptContext(schemes=["bcrypt"], deprecated="auto")
USER_PASSWORD = "Consumo2024!"

USERS = [
    {"name": "Admin Principal", "email": "admin@consumo.local"},
    {"name": "Ana García", "email": "ana@ejemplo.com"},
    {"name": "Carlos López", "email": "carlos@ejemplo.com"},
    {"name": "María Torres", "email": "maria@ejemplo.com"},
]


def usage() -> None:
    print("Uso: python scripts/render_db_init.py \"postgresql://user:pass@host:port/db\"")
    print("O bien, exporta DATABASE_URL y ejecuta: python scripts/render_db_init.py")
    sys.exit(1)


def load_database_url() -> str:
    if len(sys.argv) >= 2:
        return sys.argv[1]
    env_url = os.environ.get("DATABASE_URL")
    if env_url:
        return env_url
    usage()


def create_render_engine(database_url: str) -> Engine:
    print("🔄 Creando motor SQLAlchemy...")
    # Evitar forzar SSL para conexiones locales (localhost/127.0.0.1)
    if "localhost" in database_url or "127.0.0.1" in database_url:
        return create_engine(database_url, future=True)
    return create_engine(database_url, connect_args={"sslmode": "require"}, future=True)


def check_connection(engine: Engine) -> None:
    print("🔌 Verificando conexión a la base de datos...")
    with engine.connect() as conn:
        version = conn.execute(text("SELECT version();")).scalar_one()
        print(f"✅ Conectado a PostgreSQL: {version}")


def print_tables(engine: Engine) -> None:
    with engine.connect() as conn:
        rows = conn.execute(text(
            "SELECT table_name FROM information_schema.tables "
            "WHERE table_schema='public' ORDER BY table_name"
        )).all()
        if rows:
            print("📚 Tablas existentes en public:")
            for row in rows:
                print(f" - {row[0]}")
        else:
            print("📚 No hay tablas en el esquema public.")


def apply_schema(engine: Engine) -> None:
    if not SCHEMA_FILE.exists():
        raise FileNotFoundError(f"No se encontró schema.sql en {SCHEMA_FILE}")

    print("📄 Aplicando esquema SQL (IF NOT EXISTS)...")
    # Leer en binario y decodificar intentando UTF-8 primero, luego Latin-1
    raw = SCHEMA_FILE.read_bytes()
    try:
        sql_text = raw.decode("utf-8")
    except UnicodeDecodeError:
        print("⚠️  schema.sql no está en UTF-8, intentando Latin-1...")
        sql_text = raw.decode("latin-1")
    with engine.begin() as conn:
        conn.exec_driver_sql(sql_text)
    print("✅ Esquema aplicado / verificado.")


def seed_users(engine: Engine) -> None:
    hashed_password = PWD_CONTEXT.hash(USER_PASSWORD)
    print("👥 Insertando usuarios de ejemplo...")

    with engine.begin() as conn:
        for user in USERS:
            existing = conn.execute(text(
                "SELECT id FROM users WHERE LOWER(email) = LOWER(:email)"
            ), {"email": user["email"]}).fetchone()

            if existing:
                conn.execute(text(
                    "UPDATE users SET name = :name, password_hash = :password_hash, is_active = TRUE, updated_at = NOW() WHERE id = :id"
                ), {
                    "name": user["name"],
                    "password_hash": hashed_password,
                    "id": existing[0],
                })
                print(f"  🔄 Usuario existente actualizado: {user['email']}")
            else:
                conn.execute(text(
                    "INSERT INTO users (name, email, password_hash, is_active, created_at, updated_at) "
                    "VALUES (:name, :email, :password_hash, TRUE, NOW(), NOW())"
                ), {
                    "name": user["name"],
                    "email": user["email"],
                    "password_hash": hashed_password,
                })
                print(f"  ✅ Usuario creado: {user['email']}")

    total = engine.connect().execute(text("SELECT COUNT(*) FROM users")).scalar_one()
    print(f"📊 Total de usuarios en la base de datos: {total}")
    print("🔐 Contraseña común para usuarios: Consumo2024!")


if __name__ == "__main__":
    try:
        database_url = load_database_url()
        engine = create_render_engine(database_url)
        check_connection(engine)
        print_tables(engine)
        apply_schema(engine)
        seed_users(engine)
        print("\n✅ Inicialización y siembra completadas.")
    except Exception as exc:
        print(f"❌ Error: {exc}")
        sys.exit(1)
