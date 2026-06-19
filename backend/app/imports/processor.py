"""
Servicio de procesamiento de archivos de importación.
Soporta: .xlsx, .csv, .pdf
"""
import hashlib
import io
import os
import re
import unicodedata
from datetime import datetime
from pathlib import Path
from typing import Optional

import pandas as pd
import numpy as np

from app.config import settings

# ─── Tipos permitidos (magic bytes + MIME) ───────────────────────────────────

ALLOWED_EXTENSIONS = {".xlsx", ".csv", ".pdf"}
ALLOWED_CONTENT_TYPES = {
    "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
    "text/csv",
    "application/csv",
    "application/pdf",
}

REQUIRED_COLUMNS = {"nombre", "producto", "cantidad", "fecha", "precio"}
OPTIONAL_COLUMNS = {"hora", "metodo_pago"}


# ─── Funciones de lectura ─────────────────────────────────────────────────────

def read_excel(content: bytes) -> pd.DataFrame:
    return pd.read_excel(io.BytesIO(content), dtype=str)


def read_csv(content: bytes) -> pd.DataFrame:
    # Detectar encoding y separador
    for encoding in ("utf-8", "latin-1", "cp1252"):
        try:
            text = content.decode(encoding)
            sep = ";" if text.count(";") > text.count(",") else ","
            return pd.read_csv(io.StringIO(text), sep=sep, dtype=str)
        except Exception:
            continue
    raise ValueError("No se pudo leer el CSV. Verifica el formato y codificación.")


def read_pdf(content: bytes) -> pd.DataFrame:
    try:
        import pdfplumber
        with pdfplumber.open(io.BytesIO(content)) as pdf:
            tables = []
            for page in pdf.pages:
                for table in page.extract_tables():
                    if table:
                        tables.append(table)
            if not tables:
                raise ValueError("No se encontraron tablas en el PDF")
            headers = [str(h).strip() if h else f"col_{i}" for i, h in enumerate(tables[0][0])]
            rows = [row for t in tables for row in t[1:] if any(row)]
            return pd.DataFrame(rows, columns=headers, dtype=str)
    except ImportError:
        raise ValueError("pdfplumber no está instalado. Ejecuta: pip install pdfplumber")
    except Exception as e:
        raise ValueError(f"Error al leer PDF: {e}")


def load_file(content: bytes, filename: str) -> pd.DataFrame:
    ext = Path(filename).suffix.lower()
    if ext == ".xlsx":
        return read_excel(content)
    elif ext == ".csv":
        return read_csv(content)
    elif ext == ".pdf":
        return read_pdf(content)
    raise ValueError(f"Formato no soportado: {ext}")


# ─── Normalización de nombres de columna ─────────────────────────────────────

def _normalize(s: str) -> str:
    """Convierte a minúsculas sin tildes ni espacios."""
    s = unicodedata.normalize("NFD", s.lower())
    s = "".join(c for c in s if unicodedata.category(c) != "Mn")
    return re.sub(r"[^a-z0-9_]", "_", s).strip("_")


def auto_map_columns(df: pd.DataFrame) -> dict[str, str]:
    """
    Intenta mapear automáticamente las columnas del DataFrame
    a los campos del sistema usando sinónimos comunes.
    Devuelve dict {campo_sistema: nombre_columna_original}.
    """
    synonyms: dict[str, list[str]] = {
        "nombre":      ["nombre", "name", "cliente", "client", "usuario", "user"],
        "producto":    ["producto", "product", "item", "articulo", "descripcion", "description"],
        "cantidad":    ["cantidad", "quantity", "qty", "cant", "units", "unidades"],
        "fecha":       ["fecha", "date", "purchase_date", "fecha_compra"],
        "hora":        ["hora", "time", "purchase_time", "hora_compra"],
        "precio":      ["precio", "price", "monto", "importe", "valor", "amount"],
        "metodo_pago": ["metodo_pago", "payment_method", "metodo", "pago", "forma_pago"],
    }

    norm_cols = {_normalize(c): c for c in df.columns}
    mapping: dict[str, str] = {}

    for field, aliases in synonyms.items():
        for alias in aliases:
            if alias in norm_cols:
                mapping[field] = norm_cols[alias]
                break

    return mapping


# ─── Validación de filas ─────────────────────────────────────────────────────

def _parse_date(value: str) -> Optional[str]:
    for fmt in ("%Y-%m-%d", "%d/%m/%Y", "%m/%d/%Y", "%d-%m-%Y", "%Y%m%d"):
        try:
            return datetime.strptime(str(value).strip(), fmt).strftime("%Y-%m-%d")
        except ValueError:
            continue
    return None


def _parse_time(value: str) -> Optional[str]:
    for fmt in ("%H:%M:%S", "%H:%M", "%I:%M %p"):
        try:
            return datetime.strptime(str(value).strip(), fmt).strftime("%H:%M:%S")
        except ValueError:
            continue
    return None


def validate_and_transform(
    df: pd.DataFrame,
    column_mapping: dict[str, str],
    anonymize: bool = False,
) -> tuple[list[dict], list[dict]]:
    """
    Valida y transforma filas usando el mapeo de columnas.
    Retorna (valid_rows, error_rows).
    """
    valid_rows: list[dict] = []
    error_rows: list[dict] = []

    for idx, row in df.iterrows():
        errors: list[str] = []
        record: dict = {}

        # Nombre
        col = column_mapping.get("nombre")
        nombre = str(row[col]).strip() if col and col in row else ""
        if not nombre or nombre.lower() in ("nan", "none", ""):
            errors.append("Nombre vacío")
        else:
            record["nombre"] = (
                hashlib.sha256(nombre.lower().encode()).hexdigest()[:16] if anonymize else nombre
            )

        # Producto
        col = column_mapping.get("producto")
        producto = str(row[col]).strip() if col and col in row else ""
        if not producto or producto.lower() in ("nan", "none", ""):
            errors.append("Producto vacío")
        else:
            record["producto"] = producto

        # Cantidad
        col = column_mapping.get("cantidad")
        try:
            cantidad = int(float(str(row[col]).strip())) if col and col in row else 0
            if cantidad <= 0:
                errors.append("Cantidad debe ser mayor a 0")
            else:
                record["cantidad"] = cantidad
        except (ValueError, TypeError):
            errors.append(f"Cantidad no numérica: '{row.get(col, '')}'")

        # Fecha
        col = column_mapping.get("fecha")
        parsed_date = _parse_date(str(row[col]).strip()) if col and col in row else None
        if not parsed_date:
            errors.append(f"Formato de fecha inválido: '{row.get(col, '')}'")
        else:
            record["fecha"] = parsed_date

        # Hora (opcional)
        col = column_mapping.get("hora")
        if col and col in row:
            parsed_time = _parse_time(str(row[col]).strip())
            record["hora"] = parsed_time or "00:00:00"
        else:
            record["hora"] = "00:00:00"

        # Precio
        col = column_mapping.get("precio")
        try:
            precio_str = str(row[col]).strip().replace("$", "").replace(",", "").strip() \
                         if col and col in row else "0"
            precio = float(precio_str)
            if precio < 0:
                errors.append("Precio no puede ser negativo")
            else:
                record["precio"] = round(precio, 2)
        except (ValueError, TypeError):
            errors.append(f"Precio no numérico: '{row.get(col, '')}'")

        # Método de pago (opcional)
        col = column_mapping.get("metodo_pago")
        metodo_raw = str(row[col]).strip() if col and col in row else ""
        metodo_map = {
            "efectivo": "Efectivo", "cash": "Efectivo",
            "tarjeta": "Tarjeta",   "card": "Tarjeta",
            "transferencia": "Transferencia", "transfer": "Transferencia",
        }
        record["metodo_pago"] = metodo_map.get(metodo_raw.lower(), "Efectivo")

        if errors:
            error_rows.append({"row": int(idx) + 2, "errors": errors})
        else:
            valid_rows.append(record)

    return valid_rows, error_rows


# ─── Función principal ────────────────────────────────────────────────────────

def process_import_file(
    content: bytes,
    filename: str,
    column_mapping: Optional[dict] = None,
    anonymize: bool = False,
) -> dict:
    """
    Procesa un archivo de importación y retorna resumen de validación.
    """
    df = load_file(content, filename)
    df = df.dropna(how="all")  # Eliminar filas completamente vacías

    rows_detected = len(df)
    auto_mapping = auto_map_columns(df)

    # Usar mapeo manual si se provee, sino usar auto-detectado
    mapping = column_mapping if column_mapping else auto_mapping

    # Vista previa (primeras 10 filas sin transformar)
    preview_cols = list(mapping.values())
    preview_df = df[preview_cols].head(10) if preview_cols else df.head(10)
    preview = preview_df.replace({np.nan: None}).to_dict(orient="records")

    # Validar y transformar
    valid_rows, error_rows = validate_and_transform(df, mapping, anonymize)

    return {
        "rows_detected":  rows_detected,
        "valid_rows":     valid_rows,
        "error_rows":     error_rows,
        "column_mapping": mapping,
        "auto_mapping":   auto_mapping,
        "preview":        preview,
        "validation": {
            "valid_rows": len(valid_rows),
            "error_rows": len(error_rows),
            "errors":     error_rows[:20],  # Mostrar máx 20 errores en vista previa
        }
    }
