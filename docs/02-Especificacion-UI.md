# 02 — Especificación UI / UX

## Resumen Ejecutivo

Este documento describe las dos pantallas principales del sistema **Consumo Estratégico**: la **Pantalla Principal** (selector de modo) y la **Pantalla de Registro de Compras**. Se incluyen descripciones visuales detalladas, flujos de navegación y especificaciones de accesibilidad.

---

## 1. Principios de Diseño

- **Limpieza visual**: espaciado generoso, tipografía clara, sin exceso de elementos
- **Responsive**: diseño adaptable a escritorio (1280px), tableta (768px) y móvil (375px)
- **Accesibilidad**: etiquetas ARIA, ratio de contraste mínimo 4.5:1, navegación por teclado
- **Idioma**: 100% en español
- **Colores**: paleta neutra con acento azul corporativo

### Paleta de Colores

| Token | Color | Uso |
|-------|-------|-----|
| `--color-primary` | `#2563EB` | Botones de acción principal |
| `--color-secondary` | `#64748B` | Textos secundarios |
| `--color-success` | `#16A34A` | Mensajes de éxito |
| `--color-danger` | `#DC2626` | Errores y eliminaciones |
| `--color-warning` | `#D97706` | Advertencias |
| `--color-bg` | `#F8FAFC` | Fondo general |
| `--color-surface` | `#FFFFFF` | Tarjetas y paneles |
| `--color-border` | `#E2E8F0` | Bordes sutiles |

---

## 2. Pantalla Principal

### 2.1 Descripción Visual

```
┌──────────────────────────────────────────────────────────────┐
│  🛒 Consumo Estratégico                    [👤 Admin ▼] [↗]  │
│──────────────────────────────────────────────────────────────│
│                                                              │
│         Selecciona una opción para comenzar                  │
│                                                              │
│  ┌─────────────────┐ ┌─────────────────┐ ┌───────────────┐  │
│  │  👥             │ │  ➕             │ │  📂           │  │
│  │                 │ │                 │ │               │  │
│  │ Usuarios        │ │ Usuario         │ │ Importar      │  │
│  │ Guardados       │ │ Nuevo           │ │ Datos         │  │
│  │                 │ │                 │ │               │  │
│  │ Ver y gestionar │ │ Registrar un    │ │ Subir .xlsx   │  │
│  │ usuarios ya     │ │ nuevo usuario   │ │ .csv o .pdf   │  │
│  │ registrados     │ │ en el sistema   │ │               │  │
│  │                 │ │                 │ │               │  │
│  │ [Ver usuarios]  │ │ [Crear usuario] │ │ [Importar]    │  │
│  └─────────────────┘ └─────────────────┘ └───────────────┘  │
│                                                              │
└──────────────────────────────────────────────────────────────┘
```

### 2.2 Panel "Usuarios Guardados" (Modal o Sección Expandible)

```
┌──────────────────────────────────────────────────────────────┐
│  Usuarios registrados                              [✕ Cerrar]│
│──────────────────────────────────────────────────────────────│
│  🔍 Buscar usuario...                                        │
│──────────────────────────────────────────────────────────────│
│  ┌────────────────────────────────────────────────────────┐  │
│  │ Ana García          ana@email.com                      │  │
│  │ 📦 24 compras  💰 $1,450.00            [Seleccionar]   │  │
│  ├────────────────────────────────────────────────────────┤  │
│  │ Carlos López        carlos@email.com                   │  │
│  │ 📦 18 compras  💰 $980.50              [Seleccionar]   │  │
│  ├────────────────────────────────────────────────────────┤  │
│  │ María Torres        maria@email.com                    │  │
│  │ 📦 31 compras  💰 $2,100.75            [Seleccionar]   │  │
│  └────────────────────────────────────────────────────────┘  │
│                                          [+ Agregar usuario] │
└──────────────────────────────────────────────────────────────┘
```

### 2.3 Panel "Usuario Nuevo"

```
┌──────────────────────────────────────────┐
│  Registrar nuevo usuario         [✕]     │
│──────────────────────────────────────────│
│                                          │
│  Nombre completo *                       │
│  ┌──────────────────────────────────┐    │
│  │ Ej: Ana García                   │    │
│  └──────────────────────────────────┘    │
│                                          │
│  Correo electrónico *                    │
│  ┌──────────────────────────────────┐    │
│  │ Ej: ana@correo.com               │    │
│  └──────────────────────────────────┘    │
│                                          │
│  ┌──────────────────────────────────┐    │
│  │     Iniciar registro de compras  │    │
│  └──────────────────────────────────┘    │
│                                          │
│  ⚠ Los campos marcados con * son         │
│    obligatorios                          │
└──────────────────────────────────────────┘
```

### 2.4 Panel "Importar Datos" (Wizard de 3 Pasos)

**Paso 1 — Subir archivo**
```
┌──────────────────────────────────────────────────────────────┐
│  Importar datos                    ●——○——○  Paso 1 de 3      │
│──────────────────────────────────────────────────────────────│
│                                                              │
│   ┌──────────────────────────────────────────────────────┐   │
│   │                                                      │   │
│   │        📂  Arrastra o selecciona un archivo          │   │
│   │             .xlsx, .csv o .pdf                       │   │
│   │                                                      │   │
│   │         Tamaño máximo: 10 MB                         │   │
│   │                                                      │   │
│   │              [Seleccionar archivo]                   │   │
│   └──────────────────────────────────────────────────────┘   │
│                                                              │
│  ☐ Anonimizar datos sensibles (correos → hash)              │
│                                                              │
│                                         [Cancelar] [Siguiente►]│
└──────────────────────────────────────────────────────────────┘
```

**Paso 2 — Mapeo de columnas y vista previa**
```
┌──────────────────────────────────────────────────────────────┐
│  Importar datos                    ●——●——○  Paso 2 de 3      │
│──────────────────────────────────────────────────────────────│
│  Archivo: ventas_enero.xlsx  (245 filas detectadas)          │
│──────────────────────────────────────────────────────────────│
│  Mapeo de columnas:                                          │
│  Nombre     → [Col A: "cliente"    ▼]                        │
│  Producto   → [Col B: "item"       ▼]                        │
│  Cantidad   → [Col C: "qty"        ▼]                        │
│  Fecha      → [Col D: "fecha"      ▼]                        │
│  Precio     → [Col E: "monto"      ▼]                        │
│──────────────────────────────────────────────────────────────│
│  Vista previa (primeras 5 filas):                            │
│  ┌──────────┬──────────┬──────┬────────────┬────────┐        │
│  │ Nombre   │ Producto │ Cant │ Fecha      │ Precio │        │
│  ├──────────┼──────────┼──────┼────────────┼────────┤        │
│  │ Ana G.   │ Leche    │ 2    │ 2024-01-05 │ 45.00  │        │
│  │ Carlos L.│ Pan      │ 3    │ 2024-01-05 │ 30.00  │        │
│  └──────────┴──────────┴──────┴────────────┴────────┘        │
│  ✅ 238 filas válidas   ⚠ 7 filas con errores [Ver errores]  │
│                                    [◄Atrás] [Confirmar importación]│
└──────────────────────────────────────────────────────────────┘
```

**Paso 3 — Resultado**
```
┌──────────────────────────────────────────────────────────────┐
│  Importar datos                    ●——●——●  Completado        │
│──────────────────────────────────────────────────────────────│
│                                                              │
│   ✅ Importación completada: 238 filas insertadas,           │
│      7 filas con errores                                     │
│                                                              │
│   [📥 Descargar reporte de errores]                          │
│                                                              │
│                            [Volver a pantalla principal]     │
└──────────────────────────────────────────────────────────────┘
```

---

## 3. Pantalla de Registro de Compras

### 3.1 Descripción Visual

```
┌──────────────────────────────────────────────────────────────┐
│  🛒 Consumo Estratégico            [👤 Ana García ▼] [↗]    │
│──────────────────────────────────────────────────────────────│
│  [◄ Volver]  Registrar compra — Ana García                   │
│──────────────────────────────────────────────────────────────│
│                                                              │
│  ┌─────────────────────────────────────────────────────────┐ │
│  │  DATOS DE LA COMPRA                                     │ │
│  │─────────────────────────────────────────────────────────│ │
│  │                                                         │ │
│  │  Usuario (no editable)           Método de pago *       │ │
│  │  ┌─────────────────────┐         ┌─────────────────┐    │ │
│  │  │ Ana García          │         │ Efectivo      ▼ │    │ │
│  │  └─────────────────────┘         └─────────────────┘    │ │
│  │                                                         │ │
│  │  Producto *                      Cantidad *             │ │
│  │  ┌─────────────────────┐         ┌─────────────────┐    │ │
│  │  │ Ej: Leche entera    │         │ 1               │    │ │
│  │  └─────────────────────┘         └─────────────────┘    │ │
│  │                                                         │ │
│  │  Precio unitario ($) *           Total calculado        │ │
│  │  ┌─────────────────────┐         ┌─────────────────┐    │ │
│  │  │ 0.00                │         │ $0.00           │    │ │
│  │  └─────────────────────┘         └─────────────────┘    │ │
│  │                                                         │ │
│  │  Fecha de compra *               Hora de compra *       │ │
│  │  ┌─────────────────────┐         ┌─────────────────┐    │ │
│  │  │ 2024-01-15   📅     │         │ 14:30      🕐   │    │ │
│  │  └─────────────────────┘         └─────────────────┘    │ │
│  │                                                         │ │
│  │         [Guardar compra]   [Exportar CSV]               │ │
│  └─────────────────────────────────────────────────────────┘ │
│                                                              │
│  ┌─────────────────────────────────────────────────────────┐ │
│  │  HISTORIAL RECIENTE (últimas 5 compras)                 │ │
│  │─────────────────────────────────────────────────────────│ │
│  │  Fecha       Producto     Cant  Precio  Método          │ │
│  │  2024-01-14  Café molido  2     $89.00  Tarjeta         │ │
│  │  2024-01-12  Leche        3     $45.00  Efectivo        │ │
│  │  ─────────────────────────────────────────────────────  │ │
│  │  Total gastado: $1,450.00   Total compras: 24           │ │
│  └─────────────────────────────────────────────────────────┘ │
└──────────────────────────────────────────────────────────────┘
```

### 3.2 Modal de Confirmación de Compra

```
┌──────────────────────────────────────────┐
│  Confirmar compra                  [✕]   │
│──────────────────────────────────────────│
│                                          │
│  Por favor revisa los datos:             │
│                                          │
│  Usuario:    Ana García                  │
│  Producto:   Leche entera                │
│  Cantidad:   2 unidades                  │
│  Precio:     $45.00 c/u                  │
│  Total:      $90.00                      │
│  Fecha:      2024-01-15 14:30            │
│  Método:     Efectivo                    │
│                                          │
│  ┌──────────┐           ┌─────────────┐  │
│  │ Cancelar │           │  ✅ Confirmar│  │
│  └──────────┘           └─────────────┘  │
└──────────────────────────────────────────┘
```

---

## 4. Mensajes de Error y Éxito

| Situación | Mensaje |
|-----------|---------|
| Campo vacío | "Campo requerido" |
| Correo inválido | "Ingresa un correo electrónico válido" |
| Cantidad ≤ 0 | "La cantidad debe ser mayor a 0" |
| Precio negativo | "El precio no puede ser negativo" |
| Archivo no permitido | "Archivo no válido. Usa .xlsx, .csv o .pdf" |
| Archivo muy grande | "El archivo supera el límite de 10 MB" |
| Importación exitosa | "Importación completada: X filas insertadas, Y filas con errores" |
| Usuario ya existe | "Ya existe un usuario con ese correo electrónico" |
| Compra guardada | "Compra registrada correctamente" |
| Error de servidor | "Error inesperado. Inténtalo de nuevo o contacta al administrador" |

---

## 5. Flujo de Navegación

```
Pantalla Principal
├── [Usuarios guardados]
│   ├── Lista de usuarios
│   └── [Seleccionar] → Pantalla de Registro de Compras
│                          ├── [Guardar compra] → Modal Confirmación → Lista actualizada
│                          ├── [Exportar CSV] → Descarga archivo
│                          └── [Volver] → Pantalla Principal
├── [Usuario nuevo]
│   ├── Formulario (Nombre + Correo)
│   └── [Iniciar registro] → Pantalla de Registro de Compras
└── [Importar datos]
    ├── Paso 1: Subir archivo
    ├── Paso 2: Mapeo + Vista previa
    └── Paso 3: Confirmación → Pantalla Principal
```

---

## 6. Checklist de Pruebas — UI/UX

- [ ] Pantalla principal muestra las 3 opciones claramente
- [ ] Botón "Seleccionar" en usuario abre pantalla de compras con nombre bloqueado
- [ ] Formulario "Usuario nuevo" valida correo antes de continuar
- [ ] Drag & drop de archivo funciona en importación
- [ ] Vista previa muestra exactamente 10 filas (o menos si el archivo es más pequeño)
- [ ] Modal de confirmación muestra todos los datos antes de guardar
- [ ] Mensajes de error aparecen en rojo debajo del campo correspondiente
- [ ] Navegación por teclado funciona en todos los formularios
- [ ] Interfaz es usable en pantalla de 375px de ancho
