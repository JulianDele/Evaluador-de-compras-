# Consumo Estratégico

**Sistema inteligente de análisis de patrones de compra y hábitos de consumo**

Algoritmo que analiza información de consumo de usuarios para identificar patrones de compra, hábitos y preferencias. Datos en PostgreSQL, procesamiento en Python + React.

---

## Inicio Rápido (30 segundos)

### Con Docker (recomendado)

```bash
# 1. Copia el archivo de configuración
cp .env.example .env

# 2. Inicia todos los servicios
docker-compose up --build

# 3. Abre en navegador
# Frontend:   http://localhost:3000
# API Docs:   http://localhost:8000/docs
```

### Sin Docker

```bash
# Windows
start-dev.bat

# macOS / Linux
chmod +x start-dev.sh && ./start-dev.sh
```

Consulta **[SETUP.md](SETUP.md)** para instrucciones detalladas.

---

## Verificación Rápida

Antes de iniciar, verifica que tienes los requisitos:

```bash
python3 --version    # Debe ser 3.11+
node --version       # Debe ser 18+
psql --version       # Debe ser PostgreSQL 15+ (solo si no usas Docker)
```

O ejecuta el script de validación:

```bash
python3 check-requirements.py
```

---

## Estructura del Proyecto

```
EBD-Evaluar-Compras/
├── backend/           API REST con FastAPI (Python 3.11)
│   ├── app/
│   │   ├── auth/         Autenticación JWT
│   │   ├── users/        Gestión de usuarios
│   │   ├── purchases/    Registro de compras
│   │   ├── imports/      Importación de archivos
│   │   ├── models/       Modelos SQLAlchemy
│   │   └── schemas/      Esquemas Pydantic
│   ├── tests/            Pruebas unitarias
│   ├── requirements.txt   Dependencias Python
│   └── Dockerfile
│
├── frontend/          Aplicación React + TypeScript (Node 18)
│   ├── src/
│   │   ├── components/   Componentes reutilizables
│   │   ├── pages/        Páginas principales
│   │   ├── contexts/     Contextos de React
│   │   └── api.ts        Cliente HTTP
│   ├── package.json      Dependencias Node.js
│   └── Dockerfile
│
├── docs/              Documentación técnica
│   ├── 01-Requerimientos.md
│   ├── 02-Especificacion-UI.md
│   ├── 03-API-Endpoints.md
│   ├── 04-DB-Schema.md
│   ├── 05-Seguridad-Privacidad.md
│   ├── 06-Guia-Despliegue.md
│   └── 07-Manual-Usuario.md
│
├── scripts/           Scripts de utilidad
│   ├── schema.sql        Creación de BD
│   ├── seed_data.py      Datos iniciales
│   └── insert_users.sql  Usuarios de ejemplo
│
├── data-samples/      Archivos de ejemplo para importación
│   └── compras_ejemplo.csv
│
├── docker-compose.yml Orquestación de servicios
├── SETUP.md           Guía completa de instalación
├── start-dev.sh       Script de inicio (Linux/macOS)
├── start-dev.bat      Script de inicio (Windows)
├── check-requirements.py Validación de dependencias
└── README.md          Este archivo
```

---

## Opciones de Despliegue

### 1. Docker Compose (Recomendado para producción)

```bash
# Desarrollo
docker-compose up --build

# Producción (con archivos separados)
docker-compose -f docker-compose.yml up -d
```

**Ventajas:**
- Aislamiento completo de dependencias
- Fácil de desplegar en cualquier servidor
- BD persistente en volúmenes
- Escalable y reproducible

### 2. Instalación Local (Para desarrollo)

```bash
# Backend
cd backend
python -m venv venv
source venv/bin/activate  # o venv\Scripts\activate en Windows
pip install -r requirements.txt
uvicorn app.main:app --reload

# Frontend (en otra terminal)
cd frontend
npm install
npm run dev
```

**Ventajas:**
- ✓ Desarrollo rápido y directo
- ✓ Hot-reload automático
- ✓ Fácil debugging
- ✓ Menor consumo de recursos

---

## 🔐 Seguridad

### Variables de Entorno Sensibles

⚠️ **NUNCA** subas `.env` a Git. Ya está en `.gitignore`.

Genera valores seguros:

```bash
# JWT Secret (64 caracteres)
python -c "import secrets; print(secrets.token_hex(64))"

# BD Password (30 caracteres)
python -c "import secrets; print(secrets.token_urlsafe(30))"
```

### Antes de Producción

1. ✓ Cambia `DEBUG=false`
2. ✓ Usa certificado SSL/TLS
3. ✓ Configura `ENVIRONMENT=production`
4. ✓ Genera nuevas claves JWT
5. ✓ Limita `ALLOWED_ORIGINS` a tu dominio

---

## 👥 Usuarios por Defecto

Después de inicializar la BD, puedes usar:

| Email | Contraseña | Rol |
|-------|------------|-----|
| admin@consumo.local | Consumo2024! | Admin |
| ana@ejemplo.com | Consumo2024! | Analista |
| carlos@ejemplo.com | Consumo2024! | Analista |
| maria@ejemplo.com | Consumo2024! | Analista |

**⚠️ Cambia estas contraseñas en producción**

---

## 📡 API Endpoints

### Autenticación

```http
POST   /api/v1/auth/login              # Obtener token JWT
POST   /api/v1/auth/register           # Crear nuevo usuario
POST   /api/v1/auth/refresh-token      # Renovar token
```

### Usuarios

```http
GET    /api/v1/users/                  # Listar usuarios
GET    /api/v1/users/{id}              # Obtener usuario
POST   /api/v1/users/                  # Crear usuario (admin)
PUT    /api/v1/users/{id}              # Actualizar usuario
DELETE /api/v1/users/{id}              # Eliminar usuario (admin)
```

### Compras

```http
GET    /api/v1/purchases/              # Listar compras del usuario
POST   /api/v1/purchases/              # Registrar compra
GET    /api/v1/purchases/{id}          # Obtener compra
```

### Importación

```http
POST   /api/v1/imports/upload          # Subir archivo (Excel/PDF/CSV)
GET    /api/v1/imports/                # Historial de importaciones
```

Ver documentación completa: http://localhost:8000/docs

---

## Solución de Problemas

### "Connection refused"
PostgreSQL no está corriendo. Inicia el servicio o usa Docker.

### "ModuleNotFoundError"
Instala dependencias: `pip install -r requirements.txt`

### "CORS error"
Edita `ALLOWED_ORIGINS` en `.env` para incluir tu URL

### Puerto ya en uso
Cambia el puerto en docker-compose.yml o en el comando `uvicorn`

Ver **[SETUP.md](SETUP.md)** para más problemas y soluciones.

---

## 📚 Documentación

| Documento | Descripción |
|-----------|-------------|
| [SETUP.md](SETUP.md) | **Guía completa de instalación** ← Comienza aquí |
| [docs/01-Requerimientos.md](docs/01-Requerimientos.md) | Alcance y objetivos del proyecto |
| [docs/02-Especificacion-UI.md](docs/02-Especificacion-UI.md) | Pantallas y flujos de usuario |
| [docs/03-API-Endpoints.md](docs/03-API-Endpoints.md) | Contrato completo de la API |
| [docs/04-DB-Schema.md](docs/04-DB-Schema.md) | Esquema de base de datos |
| [docs/05-Seguridad-Privacidad.md](docs/05-Seguridad-Privacidad.md) | Medidas de seguridad |
| [docs/06-Guia-Despliegue.md](docs/06-Guia-Despliegue.md) | Despliegue en producción |
| [docs/07-Manual-Usuario.md](docs/07-Manual-Usuario.md) | Manual de uso para usuarios finales |

---

## 🛠️ Tech Stack

### Backend
- **Framework**: FastAPI 0.111+
- **Lenguaje**: Python 3.11+
- **BD**: PostgreSQL 15+
- **ORM**: SQLAlchemy 2.0+
- **Autenticación**: JWT con PyJWT
- **Hashing**: Bcrypt
- **Validación**: Pydantic

### Frontend
- **Framework**: React 19+
- **Lenguaje**: TypeScript 6+
- **Build**: Vite 5+
- **Routing**: React Router 7+
- **Forms**: React Hook Form 7+
- **Validación**: Zod 4+
- **HTTP**: Axios 1.18+
- **Notificaciones**: React Hot Toast 2+
- **Servidor**: Nginx

### Infraestructura
- **Containerización**: Docker
- **Orquestación**: Docker Compose
- **Persistencia**: PostgreSQL
- **Volúmenes**: Docker Volumes

---

## 📋 Checklist de Despliegue

- [ ] Verificar Python 3.11+, Node 18+, PostgreSQL 15+
- [ ] Ejecutar `python3 check-requirements.py`
- [ ] Configurar `.env` con valores reales
- [ ] Generar JWT_SECRET_KEY seguro
- [ ] Generar DB_PASSWORD seguro
- [ ] Inicializar base de datos: `docker-compose up db`
- [ ] Cargar esquema: `psql -f scripts/schema.sql`
- [ ] Cargar usuarios: `psql -f scripts/insert_users.sql`
- [ ] Iniciar servicios: `docker-compose up --build`
- [ ] Verificar acceso: http://localhost:3000
- [ ] Probar login con usuario de prueba
- [ ] Revisar logs: `docker-compose logs -f`

---

## 🤝 Contribuciones

1. Fork el proyecto
2. Crea una rama: `git checkout -b feature/nueva-caracteristica`
3. Commit cambios: `git commit -m "Descripción clara"`
4. Push: `git push origin feature/nueva-caracteristica`
5. Pull Request

---

## 📄 Licencia

Este proyecto está bajo licencia MIT.

---

## 📞 Soporte

¿Problemas? Consulta:
1. **[SETUP.md](SETUP.md)** - Guía de instalación
2. **[docs/](docs/)** - Documentación técnica
3. **Logs**: `docker-compose logs -f`

---

**¡Gracias por usar Consumo Estratégico! 🎉**
