# 03 — API Endpoints (Contratos REST / OpenAPI)

## Resumen Ejecutivo

Este documento describe todos los endpoints REST de la API de **Consumo Estratégico**, incluyendo ejemplos de request/response, códigos de estado y requisitos de autenticación.

**Base URL**: `https://api.consumo-estrategico.local/api/v1`

**Autenticación**: JWT Bearer Token en header `Authorization: Bearer <token>`

---

## Especificación OpenAPI 3.0

```yaml
openapi: 3.0.3
info:
  title: Consumo Estratégico API
  description: API REST para análisis de patrones de compra
  version: 1.0.0
  contact:
    name: Equipo de Desarrollo
servers:
  - url: https://api.consumo-estrategico.local/api/v1
    description: Servidor local de desarrollo

components:
  securitySchemes:
    BearerAuth:
      type: http
      scheme: bearer
      bearerFormat: JWT
  schemas:
    Error:
      type: object
      properties:
        detail:
          type: string
          example: "No autorizado"
    UserSummary:
      type: object
      properties:
        id: { type: integer }
        name: { type: string }
        email: { type: string }
        role: { type: string, enum: [admin, analista] }
        total_purchases: { type: integer }
        total_spent: { type: number, format: float }
        created_at: { type: string, format: date-time }

security:
  - BearerAuth: []
```

---

## 1. Autenticación

### POST /auth/login

Autentica un usuario y devuelve un token JWT.

**No requiere autenticación**

**Request:**
```json
{
  "email": "ana@correo.com",
  "password": "MiContraseñaSegura123"
}
```

**Response 200 OK:**
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer",
  "expires_in": 86400,
  "user": {
    "id": 1,
    "name": "Ana García",
    "email": "ana@correo.com",
    "role": "analista"
  }
}
```

**Response 401 Unauthorized:**
```json
{
  "detail": "Credenciales incorrectas"
}
```

---

### POST /auth/register

Registra un nuevo usuario en el sistema. Solo accesible por admins.

**Requiere rol: admin**

**Request:**
```json
{
  "name": "Carlos López",
  "email": "carlos@correo.com",
  "password": "OtraContraseña456",
  "role": "analista"
}
```

**Response 201 Created:**
```json
{
  "id": 2,
  "name": "Carlos López",
  "email": "carlos@correo.com",
  "role": "analista",
  "created_at": "2024-01-15T10:30:00Z"
}
```

**Response 400 Bad Request:**
```json
{
  "detail": "Ya existe un usuario con ese correo electrónico"
}
```

---

## 2. Usuarios

### GET /users

Lista todos los usuarios con su resumen de compras.

**Requiere autenticación**

**Query params:** `?page=1&limit=20&search=Ana`

**Response 200 OK:**
```json
{
  "total": 3,
  "page": 1,
  "limit": 20,
  "data": [
    {
      "id": 1,
      "name": "Ana García",
      "email": "ana@correo.com",
      "role": "analista",
      "total_purchases": 24,
      "total_spent": 1450.00,
      "created_at": "2024-01-01T09:00:00Z"
    },
    {
      "id": 2,
      "name": "Carlos López",
      "email": "carlos@correo.com",
      "role": "analista",
      "total_purchases": 18,
      "total_spent": 980.50,
      "created_at": "2024-01-02T11:00:00Z"
    }
  ]
}
```

---

### POST /users

Crea un usuario nuevo (registro desde la pantalla principal).

**Requiere autenticación**

**Request:**
```json
{
  "name": "María Torres",
  "email": "maria@correo.com"
}
```

**Response 201 Created:**
```json
{
  "id": 3,
  "name": "María Torres",
  "email": "maria@correo.com",
  "role": "analista",
  "created_at": "2024-01-15T12:00:00Z"
}
```

**Response 422 Unprocessable Entity:**
```json
{
  "detail": [
    {
      "loc": ["body", "email"],
      "msg": "value is not a valid email address",
      "type": "value_error.email"
    }
  ]
}
```

---

### GET /users/{id}

Obtiene los datos completos de un usuario.

**Requiere autenticación**

**Response 200 OK:**
```json
{
  "id": 1,
  "name": "Ana García",
  "email": "ana@correo.com",
  "role": "analista",
  "total_purchases": 24,
  "total_spent": 1450.00,
  "favorite_product": "Leche entera",
  "most_used_payment": "Tarjeta",
  "created_at": "2024-01-01T09:00:00Z"
}
```

---

### GET /users/{id}/summary

Resumen analítico de las compras del usuario.

**Requiere autenticación**

**Query params:** `?from=2024-01-01&to=2024-12-31`

**Response 200 OK:**
```json
{
  "user_id": 1,
  "user_name": "Ana García",
  "period": {
    "from": "2024-01-01",
    "to": "2024-12-31"
  },
  "summary": {
    "total_purchases": 24,
    "total_spent": 1450.00,
    "average_per_purchase": 60.42,
    "favorite_product": "Leche entera",
    "most_used_payment_method": "Tarjeta"
  },
  "top_products": [
    { "product": "Leche entera", "count": 8, "total_spent": 360.00 },
    { "product": "Pan integral", "count": 6, "total_spent": 180.00 },
    { "product": "Café molido", "count": 5, "total_spent": 445.00 }
  ],
  "payment_methods": {
    "Efectivo": 10,
    "Tarjeta": 12,
    "Transferencia": 2
  }
}
```

---

### DELETE /users/{id}

Elimina un usuario y todas sus compras asociadas.

**Requiere rol: admin**

**Response 200 OK:**
```json
{
  "message": "Usuario y 24 compras eliminados correctamente"
}
```

---

## 3. Compras

### POST /purchases

Registra una nueva compra.

**Requiere autenticación**

**Request:**
```json
{
  "user_id": 1,
  "product": "Leche entera",
  "quantity": 2,
  "price": 45.00,
  "purchase_date": "2024-01-15",
  "purchase_time": "14:30",
  "payment_method": "Efectivo"
}
```

**Response 201 Created:**
```json
{
  "id": 125,
  "user_id": 1,
  "user_name": "Ana García",
  "product": "Leche entera",
  "quantity": 2,
  "price": 45.00,
  "total": 90.00,
  "purchase_date": "2024-01-15",
  "purchase_time": "14:30:00",
  "payment_method": "Efectivo",
  "created_at": "2024-01-15T14:30:00Z"
}
```

**Response 422 Unprocessable Entity:**
```json
{
  "detail": [
    {
      "loc": ["body", "quantity"],
      "msg": "La cantidad debe ser mayor a 0",
      "type": "value_error"
    }
  ]
}
```

---

### GET /purchases

Lista compras con filtros.

**Requiere autenticación**

**Query params:** `?user_id=1&from=2024-01-01&to=2024-12-31&page=1&limit=50`

**Response 200 OK:**
```json
{
  "total": 24,
  "page": 1,
  "limit": 50,
  "data": [
    {
      "id": 125,
      "user_id": 1,
      "user_name": "Ana García",
      "product": "Leche entera",
      "quantity": 2,
      "price": 45.00,
      "total": 90.00,
      "purchase_date": "2024-01-15",
      "purchase_time": "14:30:00",
      "payment_method": "Efectivo"
    }
  ]
}
```

---

### DELETE /purchases/{id}

Elimina una compra individual.

**Requiere rol: admin**

**Response 200 OK:**
```json
{
  "message": "Compra eliminada correctamente"
}
```

---

## 4. Importaciones

### POST /imports

Inicia una importación de archivo. Devuelve un job_id para consultar el estado.

**Requiere rol: admin**

**Request:** `multipart/form-data`
- `file`: archivo .xlsx, .csv o .pdf (máx 10 MB)
- `anonymize`: boolean (opcional, default: false)
- `column_mapping`: JSON string con el mapeo de columnas

```
Content-Type: multipart/form-data; boundary=----boundary

------boundary
Content-Disposition: form-data; name="file"; filename="ventas.xlsx"
Content-Type: application/vnd.openxmlformats-officedocument.spreadsheetml.sheet

[binary data]
------boundary
Content-Disposition: form-data; name="anonymize"

false
------boundary
Content-Disposition: form-data; name="column_mapping"

{"nombre":"A","producto":"B","cantidad":"C","fecha":"D","precio":"E"}
------boundary--
```

**Response 202 Accepted:**
```json
{
  "import_id": 7,
  "status": "processing",
  "filename": "ventas.xlsx",
  "rows_detected": 245,
  "preview": [
    {
      "nombre": "Ana García",
      "producto": "Leche",
      "cantidad": 2,
      "fecha": "2024-01-05",
      "precio": 45.00
    }
  ],
  "validation": {
    "valid_rows": 238,
    "error_rows": 7,
    "errors": [
      { "row": 12, "field": "cantidad", "error": "Valor no numérico: 'dos'" },
      { "row": 45, "field": "fecha", "error": "Formato de fecha inválido: '15/01/24'" }
    ]
  }
}
```

---

### POST /imports/{id}/confirm

Confirma y ejecuta la importación luego de revisar la vista previa.

**Requiere rol: admin**

**Response 200 OK:**
```json
{
  "import_id": 7,
  "status": "completed",
  "rows_imported": 238,
  "rows_skipped": 7,
  "filename": "ventas.xlsx",
  "uploader": "admin@correo.com",
  "created_at": "2024-01-15T15:00:00Z"
}
```

---

### GET /imports/{id}

Obtiene el estado y log de una importación.

**Requiere autenticación**

**Response 200 OK:**
```json
{
  "id": 7,
  "filename": "ventas.xlsx",
  "status": "completed",
  "rows_imported": 238,
  "rows_skipped": 7,
  "uploader_name": "Admin Principal",
  "uploader_email": "admin@correo.com",
  "error_report_url": "/api/v1/imports/7/errors.csv",
  "created_at": "2024-01-15T15:00:00Z"
}
```

---

### GET /imports/{id}/errors.csv

Descarga el reporte de errores de una importación en CSV.

**Requiere autenticación**

**Response 200 OK:** `Content-Type: text/csv`

---

## 5. Exportación

### GET /exports/purchases

Exporta las compras de un usuario en CSV.

**Requiere autenticación**

**Query params:** `?user_id=1&from=2024-01-01&to=2024-12-31`

**Response 200 OK:** `Content-Type: text/csv`

---

## 6. Códigos de Estado

| Código | Significado |
|--------|-------------|
| 200 | Operación exitosa |
| 201 | Recurso creado |
| 202 | Solicitud aceptada (procesamiento asíncrono) |
| 400 | Solicitud inválida |
| 401 | No autenticado |
| 403 | No autorizado (rol insuficiente) |
| 404 | Recurso no encontrado |
| 413 | Archivo demasiado grande |
| 422 | Error de validación |
| 500 | Error interno del servidor |

---

## 7. Checklist de Pruebas — API

- [ ] POST /auth/login devuelve 401 con credenciales incorrectas
- [ ] Endpoints protegidos devuelven 401 sin token
- [ ] Endpoints de admin devuelven 403 con rol analista
- [ ] POST /purchases valida quantity > 0 y price >= 0
- [ ] POST /imports rechaza archivos > 10 MB (413)
- [ ] GET /users/{id}/summary devuelve datos correctos con rango de fechas
- [ ] DELETE /users/{id} elimina también las compras asociadas
- [ ] POST /imports/{id}/confirm hace rollback si hay error en BD
