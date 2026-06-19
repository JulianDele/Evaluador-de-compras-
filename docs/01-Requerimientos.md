# 01 — Requerimientos y Alcance

## Resumen Ejecutivo

**Consumo Estratégico** es un sistema de análisis inteligente diseñado para identificar patrones de compra, hábitos de consumo y preferencias de los usuarios a partir de sus datos de compras. El sistema permite registrar compras manualmente, importar datos masivos desde Excel/CSV/PDF y generar análisis estadísticos con Pandas y NumPy.

---

## 1. Objetivos del Proyecto

| Objetivo | Descripción |
|----------|-------------|
| Primario | Analizar patrones de compra y hábitos de consumo por usuario |
| Secundario | Facilitar la importación masiva de datos históricos de compras |
| Terciario | Proveer visualizaciones y resúmenes del comportamiento de consumo |

---

## 2. Alcance

### Incluido en el MVP (Primera Iteración)

- [ ] Pantalla principal con 3 opciones de acceso
- [ ] Registro y autenticación de usuarios (roles: admin, analista)
- [ ] Formulario de registro de compras individuales
- [ ] Importación de datos desde Excel (.xlsx), CSV y PDF
- [ ] Vista previa y validación antes de importar
- [ ] Análisis básico: total de gasto, número de compras, producto más comprado
- [ ] API REST completa con autenticación JWT
- [ ] Base de datos relacional (PostgreSQL recomendado / MySQL compatible)
- [ ] Exportación de datos en CSV

### Excluido del MVP

- Análisis predictivos avanzados (Machine Learning)
- Notificaciones por correo electrónico
- Aplicación móvil nativa
- Integración con pasarelas de pago externas

---

## 3. Requisitos Funcionales

### RF-01: Pantalla Principal

| ID | Requisito | Prioridad |
|----|-----------|-----------|
| RF-01.1 | Mostrar 3 opciones: Usuarios guardados, Usuario nuevo, Importar datos | Alta |
| RF-01.2 | Sección "Usuarios guardados": lista con nombre, correo, nº compras, gasto total | Alta |
| RF-01.3 | Botón "Seleccionar" en cada usuario para abrir su historial | Alta |
| RF-01.4 | Sección "Usuario nuevo": formulario con Nombre y Correo electrónico | Alta |
| RF-01.5 | Sección "Importar datos": subida de .xlsx, .csv, .pdf (máx. 10 MB) | Alta |
| RF-01.6 | Confirmación antes de sobrescribir datos existentes | Media |

### RF-02: Registro de Compras

| ID | Requisito | Prioridad |
|----|-----------|-----------|
| RF-02.1 | Campos: Nombre usuario, Fecha, Hora, Producto, Cantidad, Precio, Método de pago | Alta |
| RF-02.2 | Validación: cantidad > 0, precio >= 0, fecha/hora ISO, correo válido | Alta |
| RF-02.3 | Vista de confirmación antes de guardar | Alta |
| RF-02.4 | Botón "Exportar vista actual" en CSV | Media |
| RF-02.5 | Nombre del usuario no editable si viene del selector | Alta |

### RF-03: Importación de Archivos

| ID | Requisito | Prioridad |
|----|-----------|-----------|
| RF-03.1 | Soporte para .xlsx, .csv, .pdf | Alta |
| RF-03.2 | Mapeo manual de columnas: Nombre, Producto, Cantidad, Fecha, Hora, Precio | Alta |
| RF-03.3 | Vista previa con primeras 10 filas | Alta |
| RF-03.4 | Reporte de filas válidas e inválidas antes de insertar | Alta |
| RF-03.5 | Opción para anonimizar datos (reemplazar correos por hash) | Media |
| RF-03.6 | Solo rol "admin" puede importar masivamente | Alta |

### RF-04: Análisis de Datos

| ID | Requisito | Prioridad |
|----|-----------|-----------|
| RF-04.1 | Resumen por usuario: gasto total, nº compras, producto favorito | Alta |
| RF-04.2 | Análisis de frecuencia de compra por período | Media |
| RF-04.3 | Comparación de métodos de pago utilizados | Media |
| RF-04.4 | Top 5 productos más comprados | Media |

---

## 4. Requisitos No Funcionales

| ID | Requisito | Métrica |
|----|-----------|---------|
| RNF-01 | Tiempo de respuesta API | < 500 ms para consultas simples |
| RNF-02 | Disponibilidad | 99% en horario laboral |
| RNF-03 | Seguridad | Contraseñas con bcrypt, JWT expiry 24h |
| RNF-04 | Tamaño máximo de archivo importable | 10 MB |
| RNF-05 | Compatibilidad de navegadores | Chrome 90+, Firefox 88+, Edge 90+ |
| RNF-06 | Idioma de la interfaz | Español |

---

## 5. Roles de Usuario

| Rol | Permisos |
|-----|----------|
| **admin** | CRUD completo, importación masiva, eliminación de datos, gestión de usuarios |
| **analista** | Ver usuarios, registrar compras propias, ver análisis, exportar CSV |

---

## 6. Restricciones Técnicas

- **Backend**: Python 3.11+ con FastAPI
- **Base de datos**: PostgreSQL 15+ (MySQL 8+ como alternativa)
- **Frontend**: React 18+ con TypeScript
- **Procesamiento de datos**: Pandas 2.x, NumPy 1.x
- **Autenticación**: JWT (JSON Web Tokens)
- **Despliegue**: Docker + docker-compose

---

## 7. Checklist de Pruebas — Requerimientos

- [ ] Pantalla principal carga en < 2 segundos
- [ ] Formulario de usuario nuevo valida correo inválido
- [ ] Importación rechaza archivos > 10 MB
- [ ] Importación rechaza tipos de archivo no permitidos
- [ ] Usuario "analista" no puede acceder a importación masiva
- [ ] Usuario "admin" puede eliminar datos
- [ ] Datos de ejemplo se cargan correctamente al seleccionar usuario
