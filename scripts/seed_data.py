"""
Script de carga de datos iniciales (seeds) para desarrollo.
Ejecutar desde la raíz del proyecto:
    python scripts/seed_data.py

Requiere que la base de datos ya tenga el esquema aplicado.
"""

import sys
import os

# Agregar el directorio backend al path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'backend'))

from passlib.context import CryptContext
from sqlalchemy import create_engine, text
from dotenv import load_dotenv

load_dotenv(os.path.join(os.path.dirname(__file__), '..', 'backend', '.env'))

DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql://ce_user:contraseña@localhost:5432/consumo_estrategico"
)

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
engine = create_engine(DATABASE_URL)

USERS = [
    {"name": "Admin Principal",  "email": "admin@consumo.local", "password": "Consumo2024!"},
    {"name": "Ana García",       "email": "ana@ejemplo.com",     "password": "Consumo2024!"},
    {"name": "Carlos López",     "email": "carlos@ejemplo.com",  "password": "Consumo2024!"},
    {"name": "María Torres",     "email": "maria@ejemplo.com",   "password": "Consumo2024!"},
]

PRODUCTS = [
    "Leche entera", "Pan integral", "Café molido", "Arroz blanco",
    "Aceite de oliva", "Pasta spaghetti", "Yogur natural", "Queso fresco",
    "Manzanas", "Jabón de baño", "Detergente", "Jugo de naranja",
]

# Compras de ejemplo: (user_index, product_index, qty, price, date, time, method)
PURCHASES = [
    # Ana García (user 2)
    (2, 1, 2, 45.00, "2024-01-05", "10:30", "Efectivo"),
    (2, 2, 1, 30.00, "2024-01-05", "10:31", "Efectivo"),
    (2, 3, 1, 89.00, "2024-01-08", "09:00", "Tarjeta"),
    (2, 7, 4, 25.00, "2024-01-10", "16:45", "Tarjeta"),
    (2, 1, 3, 45.00, "2024-01-12", "11:00", "Efectivo"),
    (2, 4, 2, 35.00, "2024-01-14", "14:20", "Transferencia"),
    (2, 3, 1, 89.00, "2024-01-20", "09:15", "Tarjeta"),
    (2, 9, 5, 12.00, "2024-01-22", "17:30", "Efectivo"),
    # Carlos López (user 3)
    (3, 5, 2, 120.00, "2024-01-03", "12:00", "Tarjeta"),
    (3, 6, 3, 28.00,  "2024-01-07", "13:30", "Efectivo"),
    (3, 8, 1, 55.00,  "2024-01-10", "10:00", "Tarjeta"),
    (3, 2, 2, 30.00,  "2024-01-15", "08:45", "Efectivo"),
    (3, 12, 1, 75.00, "2024-01-18", "19:00", "Tarjeta"),
    # María Torres (user 4)
    (4, 11, 2, 65.00, "2024-01-06", "10:00", "Tarjeta"),
    (4, 1,  4, 45.00, "2024-01-09", "09:30", "Efectivo"),
    (4, 4,  3, 35.00, "2024-01-13", "15:00", "Transferencia"),
    (4, 7,  6, 25.00, "2024-01-17", "12:45", "Tarjeta"),
    (4, 3,  2, 89.00, "2024-01-21", "08:15", "Tarjeta"),
]


def seed():
    with engine.connect() as conn:
        # Truncar tablas en orden correcto (respetando FK)
        conn.execute(text("TRUNCATE TABLE audit_logs, imports, purchases, products, users RESTART IDENTITY CASCADE"))
        conn.commit()

        # Insertar usuarios
        user_ids = {}
        for i, user in enumerate(USERS, start=1):
            password_hash = pwd_context.hash(user["password"])
            result = conn.execute(
                text("""
                    INSERT INTO users (name, email, password_hash)
                    VALUES (:name, :email, :hash)
                    RETURNING id
                """),
                {"name": user["name"], "email": user["email"], "hash": password_hash}
            )
            user_ids[i] = result.scalar_one()
        conn.commit()
        print(f"✅ {len(USERS)} usuarios creados")

        # Insertar productos
        product_ids = {}
        for i, name in enumerate(PRODUCTS, start=1):
            result = conn.execute(
                text("INSERT INTO products (name) VALUES (:name) RETURNING id"),
                {"name": name}
            )
            product_ids[i] = result.scalar_one()
        conn.commit()
        print(f"✅ {len(PRODUCTS)} productos creados")

        # Insertar compras
        for purchase in PURCHASES:
            user_idx, prod_idx, qty, price, date, time, method = purchase
            conn.execute(
                text("""
                    INSERT INTO purchases (user_id, product_id, quantity, price, purchase_date, purchase_time, payment_method)
                    VALUES (:uid, :pid, :qty, :price, :date, :time, :method)
                """),
                {
                    "uid": user_ids[user_idx],
                    "pid": product_ids[prod_idx],
                    "qty": qty,
                    "price": price,
                    "date": date,
                    "time": time,
                    "method": method,
                }
            )
        conn.commit()
        print(f"✅ {len(PURCHASES)} compras de ejemplo creadas")

    print("\n✅ Datos de ejemplo cargados correctamente")
    print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
    print("Credenciales de acceso:")
    for user in USERS:
        print(f"  {user['email']:25} | {user['password']}")


if __name__ == "__main__":
    seed()
