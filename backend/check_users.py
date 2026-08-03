#!/usr/bin/env python3
"""Verificar usuarios en base de datos Render."""

from sqlalchemy import create_engine, text

DATABASE_URL = "postgresql://ce_user:JQQujV40beK2iN6njtNajPijvFPHIbJo@dpg-d9m2jtu7bikc739vbjlg-a.oregon-postgres.render.com/consumo_estrategico_fark"
engine = create_engine(DATABASE_URL)

with engine.connect() as conn:
    result = conn.execute(text("SELECT id, name, email, password_hash FROM users ORDER BY id"))
    print("=== USUARIOS EN BASE DE DATOS ===")
    for id, name, email, pwd_hash in result:
        print(f"ID: {id} | Nombre: {name} | Email: {email}")
        print(f"  Hash: {pwd_hash[:50]}...")
        print()

engine.dispose()
