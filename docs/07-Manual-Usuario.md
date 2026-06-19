# 07 — Manual de Usuario

## Introducción

Bienvenido a **Consumo Estratégico**, el sistema de análisis de patrones de compra. Este manual explica cómo usar las funciones principales.

---

## 1. Pantalla Principal

Al ingresar, verás tres opciones:

| Opción | Para qué sirve |
|--------|----------------|
| **Usuarios guardados** | Ver y seleccionar usuarios ya registrados |
| **Usuario nuevo** | Crear un usuario y comenzar a registrar sus compras |
| **Importar datos** | Subir un archivo Excel, CSV o PDF con compras existentes |

---

## 2. Registrar un Usuario Nuevo

1. Haz clic en **"Usuario nuevo"**
2. Ingresa el **Nombre completo** y **Correo electrónico**
3. Haz clic en **"Iniciar registro de compras"**
4. El sistema te llevará directamente al formulario de compras

---

## 3. Registrar una Compra

1. Completa los campos requeridos (*):
   - **Producto** — nombre del artículo comprado
   - **Cantidad** — número de unidades (mayor a 0)
   - **Precio** — precio unitario (mayor o igual a 0)
   - **Fecha y hora** — cuándo se realizó la compra
   - **Método de pago** — Efectivo, Tarjeta o Transferencia
2. Revisa el **Total calculado** automáticamente
3. Haz clic en **"Guardar compra"**
4. Confirma los datos en el resumen y haz clic en **"Confirmar"**

---

## 4. Importar Datos desde Archivo

**Solo disponible para administradores.**

1. Haz clic en **"Importar datos"** en la pantalla principal
2. **Paso 1**: Arrastra o selecciona tu archivo (.xlsx, .csv o .pdf, máx 10 MB)
   - Activa **"Anonimizar datos sensibles"** si deseas ocultar correos
3. **Paso 2**: Asigna cada columna del archivo al campo correcto del sistema
   - Verifica la vista previa con las primeras filas
   - Revisa las filas con errores si las hay
4. **Paso 3**: Haz clic en **"Confirmar importación"**
   - Descarga el reporte de errores si necesitas corregir datos

---

## 5. Exportar Datos

- En la pantalla de registro de compras, haz clic en **"Exportar CSV"**
- Se descargará un archivo con todas las compras del usuario seleccionado

---

## 6. Credenciales de Ejemplo

| Usuario | Correo | Rol |
|---------|--------|-----|
| Admin Principal | admin@consumo.local | admin |
| Ana García | ana@ejemplo.com | analista |
| Carlos López | carlos@ejemplo.com | analista |

> Contraseña inicial de ejemplo: `Consumo2024!` (cambiar en producción)
