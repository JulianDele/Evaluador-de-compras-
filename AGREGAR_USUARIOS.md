# 👥 Agregar Usuarios

Después de inicializar la aplicación, necesitas agregar usuarios a la base de datos para poder acceder.

> **ℹ️ Nota**: Los usuarios de ejemplo se cargan automáticamente en los primeros despliegues. Esta guía es para agregar usuarios adicionales.

---

## Opción 1: Usuarios de Ejemplo (Automático)

Después de ejecutar `docker-compose up --build`, los usuarios por defecto se crean automáticamente:

| Email | Contraseña |
|-------|------------|
| admin@consumo.local | Consumo2024! |
| ana@ejemplo.com | Consumo2024! |
| carlos@ejemplo.com | Consumo2024! |
| maria@ejemplo.com | Consumo2024! |

**Simplemente usa cualquiera de estas credenciales para loguear.**

---

## Opción 2: Agregar Nuevo Usuario (Interfaz Web)

Si eres **Admin**:

1. Inicia sesión con credenciales de admin
2. Abre: http://localhost:3000 (o tu URL)
3. Haz clic en **"Agregar Usuarios"**
4. Completa el formulario:
   - Email
   - Nombre completo
5. Haz clic en **"Guardar"**

---

## Opción 3: Insertar Manualmente en BD

Si necesitas insertar usuarios directamente en PostgreSQL:

### Con SQL directo

```bash
# Conectar a la BD
psql -U ce_user -d consumo_estrategico -h localhost

# Dentro de psql:
-- Generar hash de contraseña: cambiar_esto_por_un_hash_bcrypt
-- O usa: python -c "from passlib.context import CryptContext; pwd_context = CryptContext(schemes=['bcrypt']); print(pwd_context.hash('MiContraseña123'))"

INSERT INTO users (name, email, password_hash) VALUES (
  'Juan Pérez',
  'juan@ejemplo.com',
  '$2b$12$...'  -- Hash bcrypt aquí
);

-- Verificar
SELECT * FROM users;
```

### Usando el script SQL

```bash
# Edita scripts/insert_users.sql y agrega líneas similares
# Luego ejecuta:
psql -U ce_user -d consumo_estrategico -f scripts/insert_users.sql
```

---

## Opción 4: API REST (Programáticamente)

Usa el endpoint de registro:

```bash
curl -X POST http://localhost:8000/api/v1/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "email": "nuevo@ejemplo.com",
    "password": "ContraseñaSegura123!",
    "full_name": "Nombre Completo"
  }'
```

O consulta la documentación interactiva:
- **http://localhost:8000/docs**

---

## ✅ Verificar Usuarios

```bash
# Conectar a BD
psql -U ce_user -d consumo_estrategico

# Ver todos los usuarios
SELECT id, name, email, is_active FROM users;

# Ver usuarios activos
SELECT * FROM users WHERE is_active = TRUE;
```

---

## 🔒 Cambiar Contraseña

### Desde la interfaz web

1. Inicia sesión
2. Abre el perfil de usuario
3. Haz clic en "Cambiar Contraseña"
4. Ingresa contraseña actual y nueva
5. Guarda

### Desde la API

```bash
# Requiere token JWT
curl -X PUT http://localhost:8000/api/v1/auth/change-password \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer TU_TOKEN_JWT" \
  -d '{
    "current_password": "ContraseñaActual",
    "new_password": "NuevaContraseña123!"
  }'
```

---

## ❌ Eliminar Usuario

### Desde la interfaz (requiere Admin)

1. Inicia sesión como Admin
2. Ve a "Usuarios"
3. Localiza el usuario
4. Haz clic en "Eliminar"
5. Confirma

### Desde la API

```bash
# Requiere permisos de admin
curl -X DELETE http://localhost:8000/api/v1/users/{id} \
  -H "Authorization: Bearer TU_TOKEN_JWT"
```

### Desactivar (sin eliminar)

```sql
UPDATE users SET is_active = FALSE WHERE id = 1;
```

---

## 💡 Consejos

- **Usa contraseñas fuertes**: Mínimo 8 caracteres, con números y símbolos
- **Auditoría**: Verifica quién accede en los logs: `docker-compose logs backend`
- **Datos sensibles**: No subas usuarios de producción a Git

---

## 🆘 Problemas

### "Usuario ya existe"
- Verifica que el email no esté duplicado
- Los emails son únicos en la BD

### "Contraseña inválida"
- Debe tener mínimo 8 caracteres

### "No puedo agregar usuarios"
- Verifica que eres Admin
- Consulta los permisos en la BD

---

**¿Necesitas más ayuda?** Consulta [SETUP.md](SETUP.md) o [docs/](docs/)
2. Conéctate a la base de datos PostgreSQL
3. Crea una nueva consulta SQL
4. Copia el contenido de `scripts/insert_users.sql`
5. Ejecuta la consulta

---

## Opción 4: Script Python (Si otras opciones no funcionan)

```bash
cd "C:\Users\alvar\Documents\EBD-Evaluar-Compras\backend"

# Instala las dependencias
pip install sqlalchemy psycopg2-binary passlib bcrypt

# Ejecuta el script seed
python ../scripts/seed_data.py
```

---

## Contenido del Script SQL

El archivo `scripts/insert_users.sql` contiene:

```sql
-- Limpiar datos previos
TRUNCATE TABLE audit_logs, imports, purchases, products, users RESTART IDENTITY CASCADE;

-- Insertar usuarios
INSERT INTO users (name, email, password_hash, is_active) VALUES
  ('Admin Principal', 'admin@consumo.local', '[hash bcrypt]', true),
  ('Ana García', 'ana@ejemplo.com', '[hash bcrypt]', true),
  ('Carlos López', 'carlos@ejemplo.com', '[hash bcrypt]', true),
  ('María Torres', 'maria@ejemplo.com', '[hash bcrypt]', true);

-- Insertar productos de ejemplo
INSERT INTO products (name) VALUES
  ('Leche entera'), ('Pan integral'), ('Café molido'), ('Arroz blanco'),
  ('Aceite de oliva'), ('Pasta spaghetti'), ('Yogur natural'), ('Queso fresco'),
  ('Manzanas'), ('Jabón de baño'), ('Detergente'), ('Jugo de naranja');
```

---

##  Verificación

Una vez ejecutado el script, verifica que los datos se insertaron:

```sql
-- Ver usuarios
SELECT id, name, email FROM users;

-- Ver productos
SELECT COUNT(*) as total_productos FROM products;
```

Deberías ver:
- 4 usuarios
- 12 productos

---

## Próximos Pasos

1. ✅ Usuarios agregados
2. Inicia la aplicación:
   ```bash
   docker-compose up
   ```
3. Abre http://localhost (frontend)
4. Inicia sesión con uno de los usuarios de ejemplo
5. ¡Comienza a registrar compras!

---

## Solución de Problemas

**Error: "usuario ce_user no existe"**
- La contraseña puede ser diferente
- Intenta con usuario `postgres` en lugar de `ce_user`

**Error: "base de datos consumo_estrategico no existe"**
- Primero ejecuta: `psql -U postgres -d postgres -f scripts/schema.sql`
- Crea la base de datos manualmente si es necesario

**Error: "conexión rechazada"**
- PostgreSQL no está corriendo
- Verifica: `netstat -an | findstr "5432"`

---

Para más ayuda, consulta los logs de Docker:
```bash
docker-compose logs backend
docker-compose logs
```
