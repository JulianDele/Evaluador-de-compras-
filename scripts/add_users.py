"""
Script para agregar usuarios a PostgreSQL en Render
Uso: python add_users.py "postgresql://evaluadorcomprasdb_1moi_user:H3kIijyzTYAHFmHBk3rDaj5kEiBOVKbE@dpg-d8sg8t7avr4c73fomscg-a.oregon-postgres.render.com/consumo_estrategico"
"""
import sys
from passlib.context import CryptContext
from sqlalchemy import create_engine, text

# Verificar que se pasó la URL
if len(sys.argv) < 2:
    print("❌ Error: Debes proporcionar la DATABASE_URL")
    print("\nUso: python add_users.py \"postgresql://user:pass@host:port/db\"")
    print("\nPara obtener la URL:")
    print("1. Ve a: https://dashboard.render.com/")
    print("2. Click en 'evaluador-compras-db'")
    print("3. Copia el 'External Database URL' de la sección 'Connections'")
    sys.exit(1)

DATABASE_URL = sys.argv[1]

# Generar hash bcrypt para "Consumo2024!"
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
password_hash = pwd_context.hash("Consumo2024!")

USERS = [
    {"name": "Admin Principal",  "email": "admin@consumo.local"},
    {"name": "Ana García",       "email": "ana@ejemplo.com"},
    {"name": "Carlos López",     "email": "carlos@ejemplo.com"},
    {"name": "María Torres",     "email": "maria@ejemplo.com"},
]

try:
    print("🔄 Conectando a PostgreSQL en Render...")
    engine = create_engine(DATABASE_URL)
    
    with engine.connect() as conn:
        print("✅ Conexión exitosa!\n")
        
        # Verificar que la tabla existe
        result = conn.execute(text("SELECT to_regclass('public.users');"))
        if result.fetchone()[0] is None:
            print("❌ La tabla 'users' no existe en la BD")
            sys.exit(1)
        
        # Limpiar usuarios existentes
        print("🗑️  Limpiando usuarios existentes...")
        emails = ", ".join(f"'{u['email']}'" for u in USERS)
        conn.execute(text(f"DELETE FROM users WHERE email IN ({emails})"))
        conn.commit()
        
        # Insertar nuevos usuarios
        print("📝 Agregando usuarios...\n")
        for user in USERS:
            conn.execute(text("""
                INSERT INTO users (name, email, password_hash, is_active, created_at, updated_at)
                VALUES (:name, :email, :password_hash, true, NOW(), NOW())
            """), {
                "name": user["name"],
                "email": user["email"],
                "password_hash": password_hash,
            })
        conn.commit()
        
        # Verificar
        result = conn.execute(text("SELECT COUNT(*) FROM users"))
        count = result.fetchone()[0]
        
        print(f"✅ ¡Usuarios agregados exitosamente!")
        print(f"📊 Total de usuarios en BD: {count}\n")
        print("=" * 60)
        print("📝 CREDENCIALES PARA LOGUEARSE:")
        print("=" * 60)
        for user in USERS:
            print(f"Email:      {user['email']}")
            print(f"Contraseña: Consumo2024!")
            print()

except Exception as e:
    print(f"❌ Error: {e}")
    print("\n⚠️  Verifica que:")
    print("   1. La DATABASE_URL sea correcta")
    print("   2. Tengas conexión a internet")
    print("   3. Las tablas estén creadas en la BD")
    sys.exit(1)
