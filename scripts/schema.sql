-- ============================================================
-- Consumo Estratégico — Creación completa del esquema
-- PostgreSQL 15+
-- Ejecutar como: psql -U postgres -d consumo_estrategico -f schema.sql
-- ============================================================

-- Extensiones
CREATE EXTENSION IF NOT EXISTS "pgcrypto";

-- ============================================================
-- TABLA: users
-- ============================================================
CREATE TABLE IF NOT EXISTS users (
    id              SERIAL PRIMARY KEY,
    name            VARCHAR(200) NOT NULL,
    email           VARCHAR(320) NOT NULL,
    password_hash   VARCHAR(255) NOT NULL,
    is_active       BOOLEAN NOT NULL DEFAULT TRUE,
    created_at      TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at      TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE UNIQUE INDEX IF NOT EXISTS idx_users_email ON users (LOWER(email));

-- ============================================================
-- TABLA: products
-- ============================================================
CREATE TABLE IF NOT EXISTS products (
    id          SERIAL PRIMARY KEY,
    name        VARCHAR(300) NOT NULL,
    created_at  TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE UNIQUE INDEX IF NOT EXISTS idx_products_name ON products (LOWER(name));

-- ============================================================
-- TABLA: purchases
-- ============================================================
CREATE TABLE IF NOT EXISTS purchases (
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

CREATE INDEX IF NOT EXISTS idx_purchases_user_id    ON purchases (user_id);
CREATE INDEX IF NOT EXISTS idx_purchases_date       ON purchases (purchase_date);
CREATE INDEX IF NOT EXISTS idx_purchases_user_date  ON purchases (user_id, purchase_date DESC);
CREATE INDEX IF NOT EXISTS idx_purchases_product_id ON purchases (product_id);

-- ============================================================
-- TABLA: imports
-- ============================================================
CREATE TABLE IF NOT EXISTS imports (
    id                  SERIAL PRIMARY KEY,
    filename            VARCHAR(255) NOT NULL,
    original_filename   VARCHAR(255) NOT NULL,
    file_size_bytes     INTEGER,
    uploader_user_id    INTEGER REFERENCES users(id) ON DELETE SET NULL,
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

CREATE INDEX IF NOT EXISTS idx_imports_uploader ON imports (uploader_user_id);
CREATE INDEX IF NOT EXISTS idx_imports_status   ON imports (status);
CREATE INDEX IF NOT EXISTS idx_imports_created  ON imports (created_at DESC);

-- ============================================================
-- TABLA: audit_logs
-- ============================================================
CREATE TABLE IF NOT EXISTS audit_logs (
    id          BIGSERIAL PRIMARY KEY,
    user_id     INTEGER REFERENCES users(id) ON DELETE SET NULL,
    action      VARCHAR(50) NOT NULL,
    entity_type VARCHAR(50),
    entity_id   INTEGER,
    details     JSONB,
    ip_address  INET,
    created_at  TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_audit_user_id ON audit_logs (user_id);
CREATE INDEX IF NOT EXISTS idx_audit_created ON audit_logs (created_at DESC);
CREATE INDEX IF NOT EXISTS idx_audit_entity  ON audit_logs (entity_type, entity_id);
CREATE INDEX IF NOT EXISTS idx_audit_action  ON audit_logs (action);

-- ============================================================
-- FUNCIÓN Y TRIGGER: actualizar updated_at
-- ============================================================
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

DROP TRIGGER IF EXISTS trg_users_updated_at ON users;
CREATE TRIGGER trg_users_updated_at
    BEFORE UPDATE ON users
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- ============================================================
-- VISTAS ÚTILES
-- ============================================================

-- Resumen de compras por usuario
CREATE OR REPLACE VIEW v_user_purchase_summary AS
SELECT
    u.id                                AS user_id,
    u.name                              AS user_name,
    u.email,
    COUNT(p.id)                         AS total_purchases,
    COALESCE(SUM(p.total), 0)           AS total_spent,
    COALESCE(AVG(p.total), 0)           AS avg_per_purchase,
    MAX(p.purchase_date)                AS last_purchase_date
FROM users u
LEFT JOIN purchases p ON p.user_id = u.id
GROUP BY u.id, u.name, u.email;

-- Top productos por usuario
CREATE OR REPLACE VIEW v_top_products_by_user AS
SELECT
    p.user_id,
    u.name          AS user_name,
    pr.name         AS product_name,
    COUNT(p.id)     AS purchase_count,
    SUM(p.total)    AS total_spent
FROM purchases p
JOIN users u    ON u.id = p.user_id
JOIN products pr ON pr.id = p.product_id
GROUP BY p.user_id, u.name, pr.name;

SELECT 'Esquema creado correctamente' AS resultado;
