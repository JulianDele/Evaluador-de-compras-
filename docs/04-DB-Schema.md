# 04 — Esquema de Base de Datos y Migraciones

## Resumen Ejecutivo

Este documento define el esquema relacional de **Consumo Estratégico**. Se recomienda **PostgreSQL 15+** por su soporte a tipos de datos avanzados, integridad referencial y funciones analíticas superiores. El esquema es compatible con MySQL 8+ con mínimas adaptaciones.

---

## 1. Diagrama ERD

```
┌─────────────┐       ┌──────────────────┐       ┌─────────────┐
│    users    │       │    purchases     │       │  products   │
│─────────────│       │──────────────────│       │─────────────│
│ id (PK)     │──┐    │ id (PK)          │    ┌──│ id (PK)     │
│ name        │  └───>│ user_id (FK)     │    │  │ name        │
│ email       │       │ product_id (FK)  │<───┘  │ created_at  │
│ password_h..│       │ quantity         │       └─────────────┘
│ role        │       │ price            │
│ created_at  │       │ purchase_date    │
└─────────────┘       │ purchase_time    │
                      │ payment_method   │
       ┌──────────────│ created_at       │
       │              └──────────────────┘
       │
       │   ┌──────────────────┐
       │   │     imports      │
       │   │──────────────────│
       └──>│ id (PK)          │
           │ filename         │
           │ uploader_user_id │
           │ rows_detected    │
           │ rows_imported    │
           │ rows_skipped     │
           │ status           │
           │ anonymized       │
           │ created_at       │
           └──────────────────┘

       ┌──────────────────────┐
       │     audit_logs       │
       │──────────────────────│
       │ id (PK)              │
       │ user_id (FK)         │
       │ action               │
       │ entity_type          │
       │ entity_id            │
       │ details (JSONB)      │
       │ ip_address           │
       │ created_at           │
       └──────────────────────┘
```

---

## 2. Script de Creación — PostgreSQL

```sql
-- ============================================================
-- Consumo Estratégico — Esquema de Base de Datos
-- PostgreSQL 15+
-- ============================================================

-- Extensiones útiles
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pgcrypto";

-- ============================================================
-- Tabla: users
-- ============================================================
CREATE TABLE users (
    id              SERIAL PRIMARY KEY,
    name            VARCHAR(200) NOT NULL,
    email           VARCHAR(320) NOT NULL,
    password_hash   VARCHAR(255) NOT NULL,
    role            VARCHAR(20)  NOT NULL DEFAULT 'analista'
                    CHECK (role IN ('admin', 'analista')),
    is_active       BOOLEAN NOT NULL DEFAULT TRUE,
    created_at      TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at      TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- Índice único en email (case-insensitive)
CREATE UNIQUE INDEX idx_users_email ON users (LOWER(email));

COMMENT ON TABLE users IS 'Usuarios del sistema con autenticación y roles';
COMMENT ON COLUMN users.password_hash IS 'Hash bcrypt de la contraseña — nunca texto plano';
COMMENT ON COLUMN users.role IS 'admin: acceso total | analista: acceso limitado';

-- ============================================================
-- Tabla: products
-- ============================================================
CREATE TABLE products (
    id          SERIAL PRIMARY KEY,
    name        VARCHAR(300) NOT NULL,
    created_at  TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE UNIQUE INDEX idx_products_name ON products (LOWER(name));

COMMENT ON TABLE products IS 'Catálogo de productos; se crea automáticamente al registrar compras';

-- ============================================================
-- Tabla: purchases
-- ============================================================
CREATE TABLE purchases (
    id              SERIAL PRIMARY KEY,
    user_id         INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    product_id      INTEGER NOT NULL REFERENCES products(id) ON DELETE RESTRICT,
    quantity        INTEGER NOT NULL CHECK (quantity > 0),
    price           NUMERIC(12, 2) NOT NULL CHECK (price >= 0),
    total           NUMERIC(12, 2) GENERATED ALWAYS AS (quantity * price) STORED,
    purchase_date   DATE NOT NULL,
    purchase_time   TIME NOT NULL,
    payment_method  VARCHAR(20) NOT NULL
                    CHECK (payment_method IN ('Efectivo', 'Tarjeta', 'Transferencia')),
    created_at      TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- Índices para consultas frecuentes
CREATE INDEX idx_purchases_user_id     ON purchases (user_id);
CREATE INDEX idx_purchases_date        ON purchases (purchase_date);
CREATE INDEX idx_purchases_user_date   ON purchases (user_id, purchase_date DESC);
CREATE INDEX idx_purchases_product_id  ON purchases (product_id);

COMMENT ON TABLE purchases IS 'Registro individual de cada compra';
COMMENT ON COLUMN purchases.total IS 'Calculado automáticamente: quantity * price';

-- ============================================================
-- Tabla: imports
-- ============================================================
CREATE TABLE imports (
    id                  SERIAL PRIMARY KEY,
    filename            VARCHAR(255) NOT NULL,
    original_filename   VARCHAR(255) NOT NULL,
    file_size_bytes     INTEGER,
    uploader_user_id    INTEGER NOT NULL REFERENCES users(id) ON DELETE SET NULL,
    rows_detected       INTEGER DEFAULT 0,
    rows_imported       INTEGER DEFAULT 0,
    rows_skipped        INTEGER DEFAULT 0,
    status              VARCHAR(20) NOT NULL DEFAULT 'pending'
                        CHECK (status IN ('pending', 'processing', 'completed', 'failed')),
    anonymized          BOOLEAN NOT NULL DEFAULT FALSE,
    error_log           JSONB,
    created_at          TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    completed_at        TIMESTAMPTZ
);

CREATE INDEX idx_imports_uploader ON imports (uploader_user_id);
CREATE INDEX idx_imports_status   ON imports (status);

COMMENT ON TABLE imports IS 'Registro de cada importación masiva de archivo';

-- ============================================================
-- Tabla: audit_logs
-- ============================================================
CREATE TABLE audit_logs (
    id          BIGSERIAL PRIMARY KEY,
    user_id     INTEGER REFERENCES users(id) ON DELETE SET NULL,
    action      VARCHAR(50) NOT NULL,   -- 'CREATE', 'UPDATE', 'DELETE', 'LOGIN', 'IMPORT'
    entity_type VARCHAR(50),            -- 'user', 'purchase', 'import'
    entity_id   INTEGER,
    details     JSONB,
    ip_address  INET,
    created_at  TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_audit_user_id   ON audit_logs (user_id);
CREATE INDEX idx_audit_created   ON audit_logs (created_at DESC);
CREATE INDEX idx_audit_entity    ON audit_logs (entity_type, entity_id);

COMMENT ON TABLE audit_logs IS 'Registro de auditoría de todas las acciones del sistema';

-- ============================================================
-- Función: actualizar updated_at automáticamente
-- ============================================================
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trg_users_updated_at
    BEFORE UPDATE ON users
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
```

---

## 3. Script de Datos de Ejemplo (Seeds)

```sql
-- ============================================================
-- Datos de ejemplo para desarrollo y pruebas
-- ============================================================

-- Contraseñas de ejemplo (hash bcrypt de "Consumo2024!")
-- En producción usar bcrypt real desde el backend

INSERT INTO users (name, email, password_hash, role) VALUES
('Admin Principal',  'admin@consumo.local',  '$2b$12$EJEMPLO_HASH_ADMIN',   'admin'),
('Ana García',       'ana@ejemplo.com',       '$2b$12$EJEMPLO_HASH_ANA',     'analista'),
('Carlos López',     'carlos@ejemplo.com',    '$2b$12$EJEMPLO_HASH_CARLOS',  'analista'),
('María Torres',     'maria@ejemplo.com',     '$2b$12$EJEMPLO_HASH_MARIA',   'analista');

INSERT INTO products (name) VALUES
('Leche entera'),
('Pan integral'),
('Café molido'),
('Arroz blanco'),
('Aceite de oliva'),
('Pasta spaghetti'),
('Yogur natural'),
('Queso fresco'),
('Manzanas'),
('Jabón de baño');

-- Compras de ejemplo para Ana García (user_id=2)
INSERT INTO purchases (user_id, product_id, quantity, price, purchase_date, purchase_time, payment_method) VALUES
(2, 1, 2, 45.00, '2024-01-05', '10:30', 'Efectivo'),
(2, 2, 1, 30.00, '2024-01-05', '10:31', 'Efectivo'),
(2, 3, 1, 89.00, '2024-01-08', '09:00', 'Tarjeta'),
(2, 7, 4, 25.00, '2024-01-10', '16:45', 'Tarjeta'),
(2, 1, 3, 45.00, '2024-01-12', '11:00', 'Efectivo'),
(2, 4, 2, 35.00, '2024-01-14', '14:20', 'Transferencia'),
(2, 3, 1, 89.00, '2024-01-20', '09:15', 'Tarjeta'),
(2, 9, 5, 12.00, '2024-01-22', '17:30', 'Efectivo');

-- Compras de ejemplo para Carlos López (user_id=3)
INSERT INTO purchases (user_id, product_id, quantity, price, purchase_date, purchase_time, payment_method) VALUES
(3, 5, 2, 120.00, '2024-01-03', '12:00', 'Tarjeta'),
(3, 6, 3, 28.00,  '2024-01-07', '13:30', 'Efectivo'),
(3, 8, 1, 55.00,  '2024-01-10', '10:00', 'Tarjeta'),
(3, 2, 2, 30.00,  '2024-01-15', '08:45', 'Efectivo');
```

---

## 4. Script de Migración (Alembic)

Los scripts de migración se encuentran en `/scripts/migrations/`. Para ejecutarlos:

```bash
# Desde la carpeta /backend
alembic upgrade head          # Aplica todas las migraciones pendientes
alembic downgrade -1          # Revierte la última migración
alembic revision --autogenerate -m "descripcion_del_cambio"  # Nueva migración
```

---

## 5. Compatibilidad MySQL 8+

Para usar MySQL en lugar de PostgreSQL, reemplazar:

| PostgreSQL | MySQL |
|------------|-------|
| `SERIAL` | `INT AUTO_INCREMENT` |
| `TIMESTAMPTZ` | `DATETIME` |
| `NUMERIC(12,2)` | `DECIMAL(12,2)` |
| `JSONB` | `JSON` |
| `INET` | `VARCHAR(45)` |
| `GENERATED ALWAYS AS ... STORED` | `AS (quantity * price) STORED` |
| `BIGSERIAL` | `BIGINT AUTO_INCREMENT` |

---

## 6. Índices y Rendimiento

| Índice | Tabla | Columnas | Justificación |
|--------|-------|----------|---------------|
| `idx_users_email` | users | LOWER(email) | Búsqueda de login y unicidad |
| `idx_purchases_user_id` | purchases | user_id | Filtrar compras por usuario |
| `idx_purchases_date` | purchases | purchase_date | Filtros por rango de fechas |
| `idx_purchases_user_date` | purchases | user_id, purchase_date DESC | Historial paginado de usuario |
| `idx_purchases_product_id` | purchases | product_id | Análisis por producto |
| `idx_imports_status` | imports | status | Consultar importaciones pendientes |

---

## 7. Checklist de Pruebas — Base de Datos

- [ ] Script de creación ejecuta sin errores en PostgreSQL 15
- [ ] Datos de ejemplo (seeds) se insertan correctamente
- [ ] `CHECK (quantity > 0)` rechaza quantity = 0 o negativo
- [ ] `CHECK (price >= 0)` rechaza precios negativos
- [ ] `ON DELETE CASCADE` en purchases al eliminar usuario funciona
- [ ] Índice único en email impide duplicados (case-insensitive)
- [ ] Campo `total` se calcula automáticamente
- [ ] Trigger `updated_at` actualiza la fecha al modificar un usuario
