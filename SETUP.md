# 📋 Guía de Instalación — Consumo Estratégico

## ⚠️ Requisitos Previos

Verifica que tengas instalados:

```bash
# Backend (Python)
python --version        # Debe ser 3.11 o superior

# Frontend (Node.js)  
node --version          # Debe ser 18 o superior
npm --version           # Incluido con Node.js

# Base de datos
psql --version          # Debe ser PostgreSQL 15 o superior
```

Si falta alguno, descárgalos desde:
- **Python 3.11+**: https://www.python.org/downloads/
- **Node.js 18+**: https://nodejs.org/
- **PostgreSQL 15+**: https://www.postgresql.org/download/

---

## 🚀 Opción A: Instalación Rápida con Docker (Recomendado)

La forma más fácil. Docker se encarga de todo.

### 1️⃣ Prepara las variables de entorno

```bash
# En la raíz del proyecto
cp .env.example .env

# Edita .env y cambia:
# - DB_PASSWORD: Contraseña para PostgreSQL
# - JWT_SECRET_KEY: Ejecuta el comando que aparece ahí
```

### 2️⃣ Inicia los servicios

```bash
docker-compose up --build
```

Espera a que termine. Verás mensajes como:
```
ce_backend  | Application startup complete [uvicorn]
ce_frontend | ✓ built in X.XXs
```

### 3️⃣ Accede a la aplicación

- **Frontend**: http://localhost:3000
- **API Docs**: http://localhost:8000/docs
- **Base de datos**: localhost:5432

### 4️⃣ Carga usuarios de ejemplo

```bash
# Opción A: Desde pgAdmin (GUI en http://localhost:5050)
# Opción B: Desde línea de comandos
psql -h localhost -U ce_user -d consumo_estrategico -f scripts/insert_users.sql
```

Usuarios por defecto:
- **admin@consumo.local** / **Consumo2024!** (Admin)
- **ana@ejemplo.com** / **Consumo2024!** (Analista)

---

## 🛠️ Opción B: Instalación Local (Sin Docker)

Para desarrollo más detallado o si Docker no funciona.

### 1️⃣ Configura la base de datos

```bash
# En PostgreSQL (como admin):
psql -U postgres

# Copia y pega esto en psql:
CREATE DATABASE consumo_estrategico;
CREATE USER ce_user WITH PASSWORD 'tu_contraseña';
GRANT ALL PRIVILEGES ON DATABASE consumo_estrategico TO ce_user;
\q
```

### 2️⃣ Carga el esquema

```bash
psql -U ce_user -d consumo_estrategico -f scripts/schema.sql
```

### 3️⃣ Configura Backend

```bash
cd backend

# Crear entorno virtual
python -m venv venv

# Activar (elige tu SO):
# Windows:
venv\Scripts\activate
# macOS/Linux:
source venv/bin/activate

# Instalar dependencias
pip install -r requirements.txt

# Configurar variables de entorno
cp .env.example .env

# Edita backend/.env y rellena todos los valores
```

### 4️⃣ Inicia Backend

```bash
# Desde backend/ con venv activado
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

Verás: `Application startup complete [uvicorn]`

### 5️⃣ Configura Frontend

```bash
cd frontend

# Instalar dependencias
npm install

# Configurar variables de entorno
cp .env.example .env.local

# Edita si es necesario (por defecto está bien para local)
```

### 6️⃣ Inicia Frontend

```bash
# Desde frontend/
npm run dev
```

Verás: `VITE v5.3.3  ready in XXX ms`

### 7️⃣ Carga datos iniciales

```bash
# Desde la raíz del proyecto
python scripts/seed_data.py
```

O inserta usuarios manualmente:
```bash
psql -U ce_user -d consumo_estrategico -f scripts/insert_users.sql
```

---

## ✅ Verificación de Instalación

Una vez todo inicializado, verifica:

### Backend

```bash
# El servidor responde
curl http://localhost:8000/health
# Debe retornar: {"status":"ok","version":"1.0.0"}

# Documentación interactiva disponible
# Abre: http://localhost:8000/docs
```

### Frontend

```bash
# Accede desde navegador
# http://localhost:5173 (desarrollo local)
# http://localhost:3000 (con Docker)
```

### Base de datos

```bash
# Verifica conexión
psql -U ce_user -d consumo_estrategico -c "SELECT COUNT(*) FROM users;"
# Debe retornar 4 usuarios (o los que agregaste)
```

---

## 🔧 Solución de Problemas

### ❌ "Connection refused en localhost:5432"
**Causa**: PostgreSQL no está corriendo
- En Windows: Abre Services (services.msc) y busca "PostgreSQL"
- En macOS: `brew services start postgresql`
- En Linux: `sudo systemctl start postgresql`

### ❌ "ModuleNotFoundError: No module named 'sqlalchemy'"
**Causa**: No instalaste dependencias
```bash
# Desde backend/ (con venv activado):
pip install -r requirements.txt
```

### ❌ "Error: ENOENT: no such file or directory"
**Causa**: Falta instalar dependencias de Node.js
```bash
# Desde frontend/:
npm install
```

### ❌ "JWT_SECRET_KEY is not set"
**Causa**: No hay archivo .env o está mal configurado
```bash
# Backend: Copia .env.example a .env y configura
cp backend/.env.example backend/.env
```

### ❌ "CORS error: Origin not allowed"
**Causa**: El frontend está en un origen no permitido
- Edita `backend/.env`
- Agrega tu URL a `ALLOWED_ORIGINS`
- Ejemplo: `http://localhost:3000,http://localhost:5173`

### ❌ "Puerto 8000 ya está en uso"
**Causa**: Otro proceso usa el puerto
```bash
# Encuentra qué usa el puerto (macOS/Linux):
lsof -i :8000

# Cambia el puerto en el comando:
uvicorn app.main:app --port 8001
```

---

## 📁 Estructura de Carpetas Importante

```
backend/
├── .env                  ← CREAR AQUÍ (copiar de .env.example)
├── app/
│   ├── main.py          ← Punto de entrada
│   ├── config.py        ← Lee variables de entorno
│   └── ...
└── requirements.txt     ← Dependencias Python

frontend/
├── .env.local           ← CREAR AQUÍ (copiar de .env.example)
├── src/
│   ├── main.tsx         ← Punto de entrada
│   ├── api.ts           ← Cliente HTTP
│   └── ...
└── package.json         ← Dependencias Node.js

.env                      ← CREAR AQUÍ (copiar de .env.example)
                          Para Docker Compose

scripts/
├── schema.sql           ← Estructura de base de datos
├── seed_data.py         ← Datos iniciales
└── insert_users.sql     ← Usuarios de ejemplo
```

---

## 🚢 Despliegue en Producción

### ⚠️ Cambios Necesarios

1. **Copia `.env.example` a `.env.prod`**
   ```bash
   cp .env.example .env.prod
   ```

2. **Edita `.env.prod`** y configura:
   ```env
   ENVIRONMENT=production
   DEBUG=false
   DB_PASSWORD=generar_contraseña_muy_segura
   JWT_SECRET_KEY=generar_con_python_comando_arriba_UNICO
   ```

3. **Genera nuevas claves seguras**:
   ```bash
   # JWT
   python -c "import secrets; print(secrets.token_hex(64))"
   
   # BD (30 caracteres alphanumericos)
   python -c "import secrets; print(secrets.token_urlsafe(30))"
   ```

4. **Configura certificado SSL/TLS**:
   - Usa Let's Encrypt (gratuito)
   - Configura en tu servidor web (Nginx, Apache)

5. **Usa dominio en lugar de localhost**:
   ```env
   ALLOWED_ORIGINS=https://app.ejemplo.com,https://www.ejemplo.com
   VITE_API_URL=https://api.ejemplo.com/api/v1
   ```

6. **Ejecuta con Docker Compose en producción**:
   ```bash
   docker-compose -f docker-compose.yml up -d
   ```

---

## 📞 Soporte

Si encuentras problemas:

1. Revisa los logs:
   ```bash
   # Con Docker:
   docker-compose logs backend
   docker-compose logs frontend
   docker-compose logs db
   
   # Local:
   # Mira la salida de la terminal donde ejecutaste el comando
   ```

2. Verifica que todos los requisitos estén instalados
3. Consulta la documentación en `docs/`
4. Abre un issue con:
   - El error exacto
   - Tu sistema operativo
   - Versiones instaladas (`python --version`, etc)

---

**¡Tu aplicación está lista! 🎉**
