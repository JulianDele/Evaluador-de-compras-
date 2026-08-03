"""
Script para agregar usuarios a PostgreSQL en Render
Los hashes bcrypt ya están pre-generados
"""
from sqlalchemy import create_engine, text

# URL de Render
DATABASE_URL = "postgresql://ce_user:JQQujV40beK2iN6njtNajPijvFPHIbJo@dpg-d9m2jtu7bikc739vbjlg-a.oregon-postgres.render.com/consumo_estrategico_fark"

# Hash bcrypt de "Consumo2024!" generado con bcrypt
# Para verificar: bcrypt.checkpw(b"Consumo2024!", b"$2b$12$...")
password_hash = "$2b$12$dnoCbF3h4kIjvd0Xlp3Lk.LnzCyEtCru8frvXqtZ7vxV6kL0prxZC"

USERS = [
    {"name": "Admin Principal",  "email": "admin@consumo.local"},
    {"name": "Ana García",       "email": "ana@ejemplo.com"},
    {"name": "Carlos López",     "email": "carlos@ejemplo.com"},
    {"name": "María Torres",     "email": "maria@ejemplo.com"},
]

try:
    print("🔄 Conectando a PostgreSQL en Render...")
    engine = create_engine(DATABASE_URL, echo=False)
    
    with engine.connect() as conn:
        print("✅ Conexión exitosa!\n")
        
        # Verificar que la tabla existe
        result = conn.execute(text("SELECT to_regclass('public.users');"))
        if result.fetchone()[0] is None:
            print("❌ La tabla 'users' no existe en la BD")
            exit(1)
        
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
    print("   1. Tengas conexión a internet")
    print("   2. Las tablas estén creadas en la BD")
    exit(1)
