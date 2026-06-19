# 📚 Índice de Documentación

Bienvenido a **Consumo Estratégico**. Esta es tu guía para navegar toda la documentación del proyecto.

---

## 🚀 COMIENZA AQUÍ (Pick One)

### Opción A: Inicio Súper Rápido (2 min)

Si tienes prisa y sabes qué haces:

```bash
# 1. Valida que tengas todo
python3 check-requirements.py

# 2. Copia configuración
cp .env.example .env

# 3. Inicia
docker-compose up --build

# 4. Abre navegador
http://localhost:3000
```

**Archivo**: [QUICK_START.sh](QUICK_START.sh)

---

### Opción B: Guía Paso a Paso (10 min)

Si es tu primer despliegue o tienes dudas:

1. Lee: [README.md](README.md) - Visión general
2. Lee: [SETUP.md](SETUP.md) - Instalación completa
3. Ejecuta: `python3 check-requirements.py` - Validación

**Archivo principal**: [SETUP.md](SETUP.md)

---

### Opción C: Instalación Local (Desarrollo)

Si quieres ejecutar sin Docker:

1. Lee: [SETUP.md](SETUP.md#opción-b-instalación-local)
2. Ejecuta: `./start-dev.sh` (macOS/Linux) o `.\start-dev.bat` (Windows)
3. Espera a que se abra en http://localhost:5173

**Archivos**: [start-dev.sh](start-dev.sh) y [start-dev.bat](start-dev.bat)

---

## 📖 Documentación por Tema

### 🎯 Instalación y Despliegue

| Archivo | Para quién | Tiempo |
|---------|-----------|--------|
| [README.md](README.md) | Todos | 3 min |
| **[SETUP.md](SETUP.md)** | **Desarrolladores nuevos** | **10 min** |
| [QUICK_START.sh](QUICK_START.sh) | Usuarios experimentados | 1 min |
| [check-requirements.py](check-requirements.py) | Solucionar problemas | 1 min |
| [CHANGELOG.md](CHANGELOG.md) | Entender qué cambió | 5 min |

### 👥 Gestión de Usuarios

| Archivo | Propósito |
|---------|-----------|
| [AGREGAR_USUARIOS.md](AGREGAR_USUARIOS.md) | Cómo agregar usuarios al sistema |
| [docs/07-Manual-Usuario.md](docs/07-Manual-Usuario.md) | Manual para usuarios finales |

### 🏗️ Arquitectura y Especificación

| Documento | Descripción | Audiencia |
|-----------|-------------|-----------|
| [docs/01-Requerimientos.md](docs/01-Requerimientos.md) | Alcance, objetivos, requisitos | Product Owners, Architects |
| [docs/02-Especificacion-UI.md](docs/02-Especificacion-UI.md) | Pantallas, flujos de usuario | Diseñadores, QA, Frontend |
| [docs/03-API-Endpoints.md](docs/03-API-Endpoints.md) | Contrato REST completo | Desarrolladores Backend/Frontend |
| [docs/04-DB-Schema.md](docs/04-DB-Schema.md) | Estructura de base de datos | DBAs, Backend Developers |
| [docs/05-Seguridad-Privacidad.md](docs/05-Seguridad-Privacidad.md) | Medidas de seguridad | DevOps, Security |
| [docs/06-Guia-Despliegue.md](docs/06-Guia-Despliegue.md) | Despliegue en producción | DevOps, SRE |

---

## 🎓 Guías por Rol

### 👨‍💼 Project Manager

1. Lee: [README.md](README.md) - Contexto general
2. Lee: [docs/01-Requerimientos.md](docs/01-Requerimientos.md) - Alcance del proyecto
3. Lee: [docs/02-Especificacion-UI.md](docs/02-Especificacion-UI.md) - Entrega final

**Tiempo total**: 15 minutos

---

### 👨‍💻 Desarrollador (Primero que todo)

1. **PRIMERO**: [SETUP.md](SETUP.md) - Configura tu entorno
2. **SEGUNDO**: [docs/03-API-Endpoints.md](docs/03-API-Endpoints.md) - Entiende la API
3. **TERCERO**: [docs/04-DB-Schema.md](docs/04-DB-Schema.md) - Estructura de datos

**Tiempo total**: 30 minutos

---

### 🔧 DevOps / SRE

1. **PRIMERO**: [SETUP.md](SETUP.md#opción-a-instalación-rápida-con-docker) - Docker setup
2. **SEGUNDO**: [docker-compose.yml](docker-compose.yml) - Analiza la configuración
3. **TERCERO**: [docs/06-Guia-Despliegue.md](docs/06-Guia-Despliegue.md) - Producción

**Tiempo total**: 20 minutos

---

### 🎨 Designer / UX

1. **PRIMERO**: [docs/02-Especificacion-UI.md](docs/02-Especificacion-UI.md) - Pantallas
2. **SEGUNDO**: [SETUP.md](SETUP.md#opción-c-instalación-local) - Ejecuta localmente
3. **TERCERO**: [docs/07-Manual-Usuario.md](docs/07-Manual-Usuario.md) - Flujos de usuario

**Tiempo total**: 25 minutos

---

### 🧪 QA / Tester

1. **PRIMERO**: [SETUP.md](SETUP.md) - Configura entorno
2. **SEGUNDO**: [docs/02-Especificacion-UI.md](docs/02-Especificacion-UI.md) - Pantallas a probar
3. **TERCERO**: [AGREGAR_USUARIOS.md](AGREGAR_USUARIOS.md) - Crea usuarios de prueba

**Tiempo total**: 20 minutos

---

### 🔒 Security Engineer

1. **PRIMERO**: [docs/05-Seguridad-Privacidad.md](docs/05-Seguridad-Privacidad.md) - Medidas actuales
2. **SEGUNDO**: [backend/.env.example](backend/.env.example) - Configuración sensible
3. **TERCERO**: [docs/06-Guia-Despliegue.md](docs/06-Guia-Despliegue.md) - Consideraciones produc.

**Tiempo total**: 25 minutos

---

## 🔍 Búsqueda Rápida

### Tengo este problema...

**"¿Cómo instalo?"** → [SETUP.md](SETUP.md)

**"¿Cómo agrego usuarios?"** → [AGREGAR_USUARIOS.md](AGREGAR_USUARIOS.md)

**"¿Cuál es la contraseña de admin?"** → [AGREGAR_USUARIOS.md](AGREGAR_USUARIOS.md#usuarios-de-ejemplo-automático) (Consumo2024!)

**"¿Cómo ejecuto localmente?"** → [SETUP.md](SETUP.md#-opción-b-instalación-local) / [start-dev.sh](start-dev.sh)

**"¿Cómo hago deploy a producción?"** → [docs/06-Guia-Despliegue.md](docs/06-Guia-Despliegue.md)

**"¿Cuáles son los endpoints de la API?"** → [docs/03-API-Endpoints.md](docs/03-API-Endpoints.md)

**"¿Cuál es la estructura de la BD?"** → [docs/04-DB-Schema.md](docs/04-DB-Schema.md)

**"¿Qué cambió en el proyecto?"** → [CHANGELOG.md](CHANGELOG.md)

**"¿Me falta alguna dependencia?"** → `python3 check-requirements.py`

**"¿Cómo inicio rápido?"** → [QUICK_START.sh](QUICK_START.sh)

---

## 📊 Árbol de Directorios

```
.
├── 📖 README.md                          ← COMIENZA AQUÍ
├── 📖 SETUP.md                           ← Guía completa instalación
├── 📖 CHANGELOG.md                       ← Cambios realizados
├── 📖 INDEX.md                           ← Este archivo
├── 📖 AGREGAR_USUARIOS.md                ← Gestión de usuarios
│
├── 🚀 QUICK_START.sh                     ← Inicio rápido (copy-paste)
├── 🚀 start-dev.sh                       ← Inicio automático (Linux/macOS)
├── 🚀 start-dev.bat                      ← Inicio automático (Windows)
├── ✓ check-requirements.py               ← Validación de dependencias
│
├── ⚙️  .env.example                       ← Variables de entorno (raíz)
├── ⚙️  .nvmrc                             ← Versión Node.js
├── ⚙️  .python-version                    ← Versión Python
├── ⚙️  .dockerignore                      ← Optimización Docker
│
├── 🐳 docker-compose.yml                 ← Orquestación de servicios
│
├── 📂 backend/
│   ├── ⚙️  .env.example                   ← Variables FastAPI
│   ├── 🚀 requirements.txt                ← Dependencias Python
│   ├── 🐳 Dockerfile                     ← Imagen Docker backend
│   └── 📂 app/
│       ├── main.py                       ← Punto de entrada
│       ├── config.py                     ← Configuración
│       ├── database.py                   ← Conexión BD
│       ├── 📂 auth/                      ← Autenticación JWT
│       ├── 📂 users/                     ← Gestión de usuarios
│       ├── 📂 purchases/                 ← Registro de compras
│       ├── 📂 imports/                   ← Importación de archivos
│       ├── 📂 models/                    ← Modelos SQLAlchemy
│       └── 📂 schemas/                   ← Esquemas Pydantic
│
├── 📂 frontend/
│   ├── ⚙️  .env.example                   ← Variables React
│   ├── 🚀 package.json                   ← Dependencias Node.js
│   ├── 🐳 Dockerfile                     ← Imagen Docker frontend
│   ├── ⚙️  vite.config.ts                 ← Configuración Vite
│   └── 📂 src/
│       ├── main.tsx                      ← Punto de entrada
│       ├── api.ts                        ← Cliente HTTP
│       ├── types.ts                      ← Tipos TypeScript
│       ├── 📂 components/                ← Componentes reutilizables
│       ├── 📂 pages/                     ← Páginas principales
│       └── 📂 contexts/                  ← Contextos de React
│
├── 📂 docs/
│   ├── 01-Requerimientos.md              ← Alcance y objetivos
│   ├── 02-Especificacion-UI.md           ← Pantallas y flujos
│   ├── 03-API-Endpoints.md               ← Contrato de API
│   ├── 04-DB-Schema.md                   ← Esquema de BD
│   ├── 05-Seguridad-Privacidad.md        ← Medidas de seguridad
│   ├── 06-Guia-Despliegue.md             ← Despliegue producción
│   └── 07-Manual-Usuario.md              ← Manual de usuario
│
├── 📂 scripts/
│   ├── schema.sql                        ← Estructura base de datos
│   ├── seed_data.py                      ← Datos iniciales
│   └── insert_users.sql                  ← Usuarios de ejemplo
│
└── 📂 data-samples/
    ├── compras_ejemplo.csv               ← Archivo de ejemplo
    └── README.md                         ← Descripción
```

---

## ⏱️ Tiempo Total Recomendado

| Rol | Lectura | Configuración | Total |
|-----|---------|---------------|-------|
| **Project Manager** | 15 min | - | **15 min** |
| **Desarrollador** | 30 min | 15 min | **45 min** |
| **DevOps/SRE** | 20 min | 15 min | **35 min** |
| **Designer** | 25 min | 10 min | **35 min** |
| **QA** | 20 min | 15 min | **35 min** |
| **Security** | 25 min | - | **25 min** |

---

## 🚀 Siguiente Paso

**¿Por dónde empiezo?**

→ **[README.md](README.md)** (3 minutos)  
→ **[SETUP.md](SETUP.md)** (10 minutos)  
→ **Ejecuta**: `python3 check-requirements.py`  
→ **Inicia**: `./start-dev.sh` o `.\start-dev.bat`  
→ **Accede**: http://localhost:3000

---

**¿Preguntas? Consulta [SETUP.md](SETUP.md#-solución-de-problemas)**

**Última actualización**: 19-06-2026
