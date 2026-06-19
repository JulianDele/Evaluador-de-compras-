# 06 — Guía de Despliegue

## Requisitos del Sistema

| Herramienta | Versión mínima | Comando de verificación |
|-------------|----------------|------------------------|
| Python | 3.11+ | `python --version` |
| Node.js | 18+ | `node --version` |
| PostgreSQL | 15+ | `psql --version` |
| Docker (opcional) | 24+ | `docker --version` |
| Git | 2.40+ | `git --version` |

---

## 1. Instalación Local (Sin Docker)

### Paso 1 — Clonar y preparar
```bash
git clone <url-del-repositorio>
cd EBD-Evaluar-Compras
```

### Paso 2 — Configurar Backend
```bash
cd backend
python -m venv venv

# Windows:
venv\Scripts\activate

# Linux/Mac:
source venv/bin/activate

pip install -r requirements.txt
```

### Paso 3 — Configurar variables de entorno
```bash
# Copiar el archivo de ejemplo
cp .env.example .env

# Editar .env con tus valores reales:
# DATABASE_URL=postgresql://usuario:contraseña@localhost:5432/consumo_estrategico
# JWT_SECRET_KEY=clave_secreta_muy_larga_y_aleatoria
# ENVIRONMENT=development
```

### Paso 4 — Crear base de datos
```bash
# En PostgreSQL
psql -U postgres -c "CREATE DATABASE consumo_estrategico;"
psql -U postgres -c "CREATE USER ce_user WITH PASSWORD 'tu_contraseña';"
psql -U postgres -c "GRANT ALL ON DATABASE consumo_estrategico TO ce_user;"

# Ejecutar migraciones
alembic upgrade head

# Cargar datos de ejemplo
python scripts/seed_data.py
```

### Paso 5 — Iniciar Backend
```bash
# Desde /backend con el entorno virtual activo
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

La API estará disponible en: http://localhost:8000
Documentación Swagger: http://localhost:8000/docs

### Paso 6 — Configurar Frontend
```bash
cd ../frontend
npm install
cp .env.example .env.local
# Editar .env.local: VITE_API_URL=http://localhost:8000/api/v1
```

### Paso 7 — Iniciar Frontend
```bash
npm run dev
# Disponible en: http://localhost:5173
```

---

## 2. Instalación con Docker Compose

```bash
# Desde la raíz del proyecto
cp .env.example .env
# Editar .env con tus valores

docker-compose up --build -d

# Ver logs
docker-compose logs -f

# Detener servicios
docker-compose down
```

Servicios disponibles:
- Frontend: http://localhost:3000
- Backend API: http://localhost:8000
- Swagger UI: http://localhost:8000/docs
- PostgreSQL: localhost:5432

---

## 3. Variables de Entorno

### Backend (.env)
```env
# Base de datos
DATABASE_URL=postgresql://ce_user:contraseña@localhost:5432/consumo_estrategico

# Seguridad
JWT_SECRET_KEY=genera_una_clave_aleatoria_de_64_chars_minimo
JWT_ALGORITHM=HS256
JWT_EXPIRE_HOURS=24

# Archivos
MAX_FILE_SIZE_MB=10
UPLOAD_DIR=/var/app/uploads

# Entorno
ENVIRONMENT=development
DEBUG=true

# CORS
ALLOWED_ORIGINS=http://localhost:5173,http://localhost:3000
```

### Frontend (.env.local)
```env
VITE_API_URL=http://localhost:8000/api/v1
VITE_APP_NAME=Consumo Estratégico
```

---

## 4. Despliegue en Producción

### Consideraciones clave:
1. Configurar certificado TLS/SSL (Let's Encrypt recomendado)
2. Usar `ENVIRONMENT=production` y `DEBUG=false`
3. Generar `JWT_SECRET_KEY` con: `python -c "import secrets; print(secrets.token_hex(64))"`
4. Configurar reverse proxy (Nginx o Caddy)
5. Configurar backups automáticos de la BD (retención 30 días)

### Configuración Nginx básica
```nginx
server {
    listen 443 ssl;
    server_name tu-dominio.com;

    ssl_certificate /etc/letsencrypt/live/tu-dominio.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/tu-dominio.com/privkey.pem;

    # Frontend
    location / {
        proxy_pass http://localhost:3000;
    }

    # API
    location /api/ {
        proxy_pass http://localhost:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

---

## 5. Backups

```bash
# Backup manual de PostgreSQL
pg_dump -U ce_user consumo_estrategico > backup_$(date +%Y%m%d).sql

# Restaurar
psql -U ce_user consumo_estrategico < backup_20240115.sql
```

Ubicación de backups: `/var/backups/consumo-estrategico/`
Retención: 30 días (automatizar con cron)

---

## 6. Checklist de Despliegue

- [ ] Variables de entorno configuradas
- [ ] Base de datos creada y migraciones aplicadas
- [ ] Datos de ejemplo cargados (solo en desarrollo)
- [ ] HTTPS configurado (producción)
- [ ] Backend responde en /health
- [ ] Frontend carga la pantalla principal
- [ ] Login funciona con usuario admin
- [ ] Importación de CSV de prueba funciona
