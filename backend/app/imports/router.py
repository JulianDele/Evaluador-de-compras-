"""
Router de importaciones: subida de archivos Excel/CSV/PDF.
"""
import csv
import io
import json
import os
import re
import unicodedata
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional

from fastapi import APIRouter, Depends, File, Form, HTTPException, Request, UploadFile, status
from fastapi.responses import StreamingResponse
from sqlalchemy import func
from sqlalchemy.orm import Session

from app.config import settings
from app.database import get_db
from app.models import Import, Purchase, Product, User, AuditLog
from app.schemas import ImportResponse, ImportConfirmResponse, ImportDetail
from app.auth.security import get_current_user
from app.imports.processor import (
    ALLOWED_EXTENSIONS, ALLOWED_CONTENT_TYPES, process_import_file,
)

router = APIRouter(prefix="/imports", tags=["Importaciones"])

# Almacenamiento temporal en memoria de vista previa (en producción usar Redis/BD)
_import_previews: dict[int, dict] = {}


def _safe_filename(name: str) -> str:
    """Sanitiza nombre de archivo para evitar path traversal."""
    name = unicodedata.normalize("NFKD", name)
    name = re.sub(r"[^\w\s\-\.]", "", name).strip()
    return name[:200]


def _validate_file(file: UploadFile, content: bytes) -> None:
    ext = Path(file.filename or "").suffix.lower()
    if ext not in ALLOWED_EXTENSIONS:
        raise HTTPException(400, f"Tipo de archivo no permitido. Usa: {', '.join(ALLOWED_EXTENSIONS)}")
    if len(content) > settings.max_file_size_bytes:
        raise HTTPException(413, f"El archivo supera el límite de {settings.max_file_size_mb} MB")
    if file.content_type and file.content_type not in ALLOWED_CONTENT_TYPES:
        # Advertencia — no bloquear en caso de MIME impreciso del cliente
        pass


# ─── Subir archivo y generar vista previa ─────────────────────────────────────

@router.post(
    "",
    response_model=ImportResponse,
    status_code=status.HTTP_202_ACCEPTED,
    summary="Subir archivo para importación",
)
async def upload_import(
    request: Request,
    file: UploadFile = File(..., description="Archivo .xlsx, .csv o .pdf"),
    anonymize: bool = Form(False),
    column_mapping: Optional[str] = Form(None, description="JSON con mapeo de columnas"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    content = await file.read()
    _validate_file(file, content)

    # Parsear mapeo de columnas si se provee
    col_map = None
    if column_mapping:
        try:
            col_map = json.loads(column_mapping)
        except json.JSONDecodeError:
            raise HTTPException(400, "column_mapping debe ser un JSON válido")

    # Procesar archivo
    try:
        result = process_import_file(content, file.filename or "archivo", col_map, anonymize)
    except ValueError as e:
        raise HTTPException(400, str(e))

    # Guardar registro de importación en BD (estado: processing)
    safe_name = _safe_filename(file.filename or "archivo")
    ts = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
    stored_filename = f"{ts}_{safe_name}"

    imp = Import(
        filename=stored_filename,
        original_filename=file.filename or "archivo",
        file_size_bytes=len(content),
        uploader_user_id=current_user.id,
        rows_detected=result["rows_detected"],
        status="processing",
        anonymized=anonymize,
        error_log=result["validation"]["errors"],
    )
    db.add(imp)
    db.commit()
    db.refresh(imp)

    # Guardar vista previa en memoria para confirmación posterior
    _import_previews[imp.id] = {
        "valid_rows":   result["valid_rows"],
        "error_rows":   result["error_rows"],
        "content":      content,
        "filename":     file.filename,
        "anonymize":    anonymize,
        "column_mapping": result["column_mapping"],
    }

    db.add(AuditLog(
        user_id=current_user.id,
        action="IMPORT_START",
        entity_type="import",
        entity_id=imp.id,
        details={"filename": file.filename, "rows_detected": result["rows_detected"]},
        ip_address=request.client.host if request.client else None,
    ))
    db.commit()

    return ImportResponse(
        import_id=imp.id,
        status="processing",
        filename=file.filename or "",
        rows_detected=result["rows_detected"],
        preview=result["preview"],
        validation=result["validation"],
    )


# ─── Confirmar importación ────────────────────────────────────────────────────

@router.post(
    "/{import_id}/confirm",
    response_model=ImportConfirmResponse,
    summary="Confirmar e insertar datos de importación",
)
def confirm_import(
    import_id: int,
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    imp = db.query(Import).filter(Import.id == import_id).first()
    if not imp:
        raise HTTPException(404, "Importación no encontrada")
    if imp.status not in ("processing",):
        raise HTTPException(400, f"La importación ya fue procesada (estado: {imp.status})")

    preview = _import_previews.get(import_id)
    if not preview:
        raise HTTPException(400, "No hay datos pendientes de confirmación para esta importación")

    valid_rows = preview["valid_rows"]
    rows_imported = 0

    try:
        for record in valid_rows:
            # Obtener o crear usuario por nombre
            user = db.query(User).filter(
                func.lower(User.name) == record["nombre"].lower()
            ).first()
            if not user:
                from app.auth.security import hash_password
                import secrets
                user = User(
                    name=record["nombre"],
                    email=f"importado_{secrets.token_hex(4)}@sin-correo.local",
                    password_hash=hash_password(secrets.token_urlsafe(16)),
                )
                db.add(user)
                db.flush()

            # Obtener o crear producto
            product = db.query(Product).filter(
                func.lower(Product.name) == record["producto"].lower()
            ).first()
            if not product:
                product = Product(name=record["producto"])
                db.add(product)
                db.flush()

            purchase = Purchase(
                user_id=product.id,  # se sobreescribirá
                product_id=product.id,
                quantity=record["cantidad"],
                price=record["precio"],
                purchase_date=record["fecha"],
                purchase_time=record["hora"],
                payment_method=record["metodo_pago"],
            )
            purchase.user_id = user.id
            db.add(purchase)
            rows_imported += 1

        imp.rows_imported = rows_imported
        imp.rows_skipped  = len(preview["error_rows"])
        imp.status        = "completed"
        imp.completed_at  = datetime.now(timezone.utc)

        db.add(AuditLog(
            user_id=current_user.id,
            action="IMPORT_COMPLETE",
            entity_type="import",
            entity_id=imp.id,
            details={"rows_imported": rows_imported, "rows_skipped": imp.rows_skipped},
            ip_address=request.client.host if request.client else None,
        ))
        db.commit()

    except Exception as e:
        db.rollback()
        imp.status = "failed"
        db.commit()
        db.add(AuditLog(
            user_id=current_user.id,
            action="IMPORT_FAILED",
            entity_type="import",
            entity_id=imp.id,
            details={"error": str(e)},
            ip_address=request.client.host if request.client else None,
        ))
        db.commit()
        raise HTTPException(500, f"Error durante la importación: {e}")
    finally:
        _import_previews.pop(import_id, None)

    db.refresh(imp)
    return ImportConfirmResponse(
        import_id=imp.id,
        status=imp.status,
        rows_imported=imp.rows_imported,
        rows_skipped=imp.rows_skipped,
        filename=imp.original_filename,
        created_at=imp.created_at,
    )


# ─── Consultar estado de importación ─────────────────────────────────────────

@router.get("/{import_id}", response_model=ImportDetail, summary="Estado de importación")
def get_import(
    import_id: int,
    db: Session = Depends(get_db),
    _: User = Depends(get_current_user),
):
    imp = db.query(Import).filter(Import.id == import_id).first()
    if not imp:
        raise HTTPException(404, "Importación no encontrada")

    uploader = db.query(User).filter(User.id == imp.uploader_user_id).first()

    return ImportDetail(
        id=imp.id,
        filename=imp.original_filename,
        status=imp.status,
        rows_imported=imp.rows_imported,
        rows_skipped=imp.rows_skipped,
        uploader_name=uploader.name if uploader else None,
        uploader_email=uploader.email if uploader else None,
        error_report_url=f"/api/v1/imports/{import_id}/errors.csv" if imp.error_log else None,
        created_at=imp.created_at,
    )


# ─── Descargar reporte de errores ─────────────────────────────────────────────

@router.get("/{import_id}/errors.csv", summary="Descargar reporte de errores en CSV")
def download_errors(
    import_id: int,
    db: Session = Depends(get_db),
    _: User = Depends(get_current_user),
):
    imp = db.query(Import).filter(Import.id == import_id).first()
    if not imp:
        raise HTTPException(404, "Importación no encontrada")

    errors = imp.error_log or []
    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(["Fila", "Errores"])
    for err in errors:
        writer.writerow([err.get("row", ""), "; ".join(err.get("errors", []))])

    output.seek(0)
    return StreamingResponse(
        iter([output.getvalue()]),
        media_type="text/csv",
        headers={"Content-Disposition": f"attachment; filename=errores_importacion_{import_id}.csv"},
    )
