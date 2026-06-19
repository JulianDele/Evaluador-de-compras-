# 05 — Seguridad y Privacidad

## Resumen Ejecutivo

Este documento detalla las medidas de seguridad implementadas en **Consumo Estratégico**, cubriendo autenticación, autorización, protección de datos, validación de entradas, auditoría y cumplimiento de buenas prácticas (OWASP Top 10).

---

## 1. Autenticación y Autorización

### 1.1 Contraseñas
- **Nunca** se almacenan contraseñas en texto plano
- Se usa **bcrypt** con factor de costo ≥ 12 (`bcrypt.hashpw(password, bcrypt.gensalt(rounds=12))`)
- Política mínima: 8 caracteres, al menos 1 mayúscula, 1 número

### 1.2 JSON Web Tokens (JWT)
- Algoritmo: **HS256** (HMAC-SHA256)
- Expiración: **24 horas**
- Payload mínimo: `{ "sub": user_id, "role": "analista", "exp": timestamp }`
- La clave secreta se almacena en variable de entorno (`JWT_SECRET_KEY`), **nunca en código**
- Renovación de token: endpoint `POST /auth/refresh` con token válido

### 1.3 Control de Roles (RBAC)

| Acción | admin | analista |
|--------|-------|----------|
| Ver lista de usuarios | ✅ | ✅ |
| Crear usuario nuevo | ✅ | ✅ |
| Eliminar usuario | ✅ | ❌ |
| Registrar compra | ✅ | ✅ (solo propia) |
| Ver compras de cualquier usuario | ✅ | ❌ |
| Importar archivo masivo | ✅ | ❌ |
| Ver logs de auditoría | ✅ | ❌ |
| Exportar CSV | ✅ | ✅ (solo propios) |

---

## 2. Protección de Datos

### 2.1 Cifrado en Tránsito
- Toda comunicación usa **HTTPS/TLS 1.2+**
- Certificados: Let's Encrypt (producción) o certificado autofirmado (desarrollo local)
- Headers de seguridad HTTP:
  ```
  Strict-Transport-Security: max-age=31536000; includeSubDomains
  X-Content-Type-Options: nosniff
  X-Frame-Options: DENY
  Content-Security-Policy: default-src 'self'
  ```

### 2.2 Cifrado en Reposo
- Cifrar campos sensibles opcionales (correo electrónico) con `pgcrypto` en PostgreSQL
- Backups cifrados con AES-256
- Variables de entorno con credenciales de BD **nunca** en control de versiones

### 2.3 Anonimización
- Al importar, opción `anonymize=true` reemplaza correos por su hash SHA-256
- Ejemplo: `ana@correo.com` → `a1b2c3d4e5f6...` (hash irreversible)
- Opción de eliminación de datos por solicitud del usuario (GDPR/privacidad)

---

## 3. Validación y Saneamiento de Entradas (OWASP A03)

### 3.1 Prevención de Inyección SQL
- **Nunca** concatenar entradas del usuario en queries SQL
- Usar **SQLAlchemy ORM** con parámetros vinculados siempre
- Ejemplo correcto:
  ```python
  # ✅ Correcto — consulta parametrizada
  db.query(User).filter(User.email == email).first()
  
  # ❌ NUNCA hacer esto
  db.execute(f"SELECT * FROM users WHERE email = '{email}'")
  ```

### 3.2 Prevención de XSS
- Frontend: usar React (escapa HTML automáticamente, evitar `dangerouslySetInnerHTML`)
- Backend: sanitizar y escapar datos antes de incluirlos en respuestas

### 3.3 Validación con Pydantic
- Todos los esquemas de entrada usan **Pydantic v2** con validadores estrictos
- Ejemplos de validaciones:
  ```python
  class PurchaseCreate(BaseModel):
      quantity: int = Field(gt=0, description="Debe ser mayor a 0")
      price: Decimal = Field(ge=0, description="No puede ser negativo")
      purchase_date: date
      payment_method: Literal["Efectivo", "Tarjeta", "Transferencia"]
  ```

---

## 4. Control de Acceso a Archivos (OWASP A01)

| Control | Implementación |
|---------|---------------|
| Tipos permitidos | `.xlsx`, `.csv`, `.pdf` únicamente |
| Validación de tipo | Magic bytes + extensión (no solo extensión) |
| Tamaño máximo | 10 MB (configurable en `MAX_FILE_SIZE_MB`) |
| Nombre de archivo | Sanitizado antes de almacenar (sin `../`, caracteres especiales) |
| Almacenamiento | Directorio aislado fuera del webroot (`/var/app/uploads/`) |
| Procesamiento | En worker separado (Celery o background task de FastAPI) |

```python
ALLOWED_CONTENT_TYPES = {
    "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",  # .xlsx
    "text/csv",
    "application/pdf",
}
MAX_FILE_SIZE = 10 * 1024 * 1024  # 10 MB

def validate_upload(file: UploadFile) -> None:
    if file.content_type not in ALLOWED_CONTENT_TYPES:
        raise HTTPException(400, "Tipo de archivo no permitido")
    if file.size > MAX_FILE_SIZE:
        raise HTTPException(413, "Archivo demasiado grande (máx 10 MB)")
```

---

## 5. Registro y Auditoría

Cada acción sensible genera un registro en la tabla `audit_logs`:

| Acción | Se registra cuando... |
|--------|-----------------------|
| `LOGIN` | Usuario inicia sesión |
| `LOGIN_FAILED` | Intento fallido de login |
| `CREATE_USER` | Se crea un usuario |
| `DELETE_USER` | Se elimina un usuario |
| `CREATE_PURCHASE` | Se registra una compra |
| `DELETE_PURCHASE` | Se elimina una compra |
| `IMPORT_START` | Se inicia importación de archivo |
| `IMPORT_COMPLETE` | Importación finaliza exitosamente |
| `IMPORT_FAILED` | Importación falla |
| `EXPORT_CSV` | Usuario exporta datos en CSV |

Cada log incluye: `user_id`, `action`, `ip_address`, `timestamp`, `details (JSON)`.

---

## 6. Dependencias y Vulnerabilidades

### Revisión periódica
```bash
# Python — revisar vulnerabilidades conocidas
pip install safety
safety check -r requirements.txt

# Node.js — revisar dependencias frontend
npm audit
npm audit fix
```

### Dependencias de seguridad clave (backend)
```
passlib[bcrypt]>=1.7.4    # Hashing de contraseñas
python-jose[cryptography]>=3.3.0  # JWT
cryptography>=41.0.0      # Cifrado general
```

---

## 7. Pruebas de Penetración Básicas

| Prueba | Herramienta | Frecuencia |
|--------|-------------|------------|
| Inyección SQL | SQLMap (manual review) | Antes de cada release |
| XSS | OWASP ZAP | Antes de cada release |
| Autenticación JWT | jwt.io + Burp Suite | Antes de cada release |
| Archivos maliciosos | Subida manual de tipos inválidos | Antes de cada release |
| Rate limiting | wrk / ab | Mensual |

---

## 8. Privacidad y Retención de Datos

- Datos personales mínimos: solo nombre y correo (opcional)
- Retención de logs de auditoría: **12 meses**, luego purga automática
- Retención de backups: **30 días** en almacenamiento cifrado
- Derecho al olvido: endpoint `DELETE /users/{id}` elimina todos los datos del usuario (cascada)
- Documentar en `docs/06-Guia-Despliegue.md` la ubicación de backups

---

## 9. Checklist de Seguridad — MVP

- [ ] Contraseñas hasheadas con bcrypt (rounds ≥ 12)
- [ ] JWT expira en 24 horas
- [ ] Clave JWT en variable de entorno (no en código)
- [ ] Todos los endpoints verifican token
- [ ] Endpoints admin verifican rol
- [ ] Consultas SQL usan parámetros vinculados (ORM)
- [ ] Archivos validados por tipo real (magic bytes) y tamaño
- [ ] Headers de seguridad HTTP configurados
- [ ] HTTPS habilitado en producción
- [ ] Logs de auditoría funcionan para login y cambios de datos
- [ ] `safety check` pasa sin vulnerabilidades críticas
- [ ] `npm audit` pasa sin vulnerabilidades críticas
- [ ] Archivos `.env` en `.gitignore`
