-- ============================================================
-- Script para insertar usuarios de ejemplo en la base de datos
-- Ejecutar después de crear el esquema
-- ============================================================

-- Nota: Las contraseñas hasheadas aquí son ejemplos
-- Para producción, asegúrate de generar hashes seguros con bcrypt
-- Contraseña: Consumo2024!

-- Truncar tablas si existen datos previos
TRUNCATE TABLE audit_logs, imports, purchases, products, users RESTART IDENTITY CASCADE;

-- Insertar usuarios de ejemplo
-- Las contraseñas son: "Consumo2024!" hasheadas con bcrypt
INSERT INTO users (name, email, password_hash, role, is_active)
VALUES
  ('Admin Principal', 'admin@consumo.local', '$2b$12$D7p7Q/D7p7Q/D7p7Q/D7p7Q/D7p7Q/D7p7Q/D7p7Q/D7p7Q/D7p7Q', 'admin', true),
  ('Ana García', 'ana@ejemplo.com', '$2b$12$D7p7Q/D7p7Q/D7p7Q/D7p7Q/D7p7Q/D7p7Q/D7p7Q/D7p7Q/D7p7Q', 'analista', true),
  ('Carlos López', 'carlos@ejemplo.com', '$2b$12$D7p7Q/D7p7Q/D7p7Q/D7p7Q/D7p7Q/D7p7Q/D7p7Q/D7p7Q/D7p7Q', 'analista', true),
  ('María Torres', 'maria@ejemplo.com', '$2b$12$D7p7Q/D7p7Q/D7p7Q/D7p7Q/D7p7Q/D7p7Q/D7p7Q/D7p7Q/D7p7Q', 'analista', true);

-- Insertar productos de ejemplo
INSERT INTO products (name)
VALUES
  ('Leche entera'),
  ('Pan integral'),
  ('Café molido'),
  ('Arroz blanco'),
  ('Aceite de oliva'),
  ('Pasta spaghetti'),
  ('Yogur natural'),
  ('Queso fresco'),
  ('Manzanas'),
  ('Jabón de baño'),
  ('Detergente'),
  ('Jugo de naranja');

COMMIT;
