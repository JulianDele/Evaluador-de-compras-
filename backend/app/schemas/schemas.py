"""
Esquemas Pydantic para validación y serialización.
"""
from datetime import date, time, datetime
from decimal import Decimal
from typing import Optional, List, Any
from pydantic import BaseModel, EmailStr, Field, field_validator
from enum import Enum


# ─── Enums ───────────────────────────────────────────────────────────────────

class PaymentMethodEnum(str, Enum):
    efectivo      = "Efectivo"
    tarjeta       = "Tarjeta"
    transferencia = "Transferencia"


class ImportStatusEnum(str, Enum):
    pending    = "pending"
    processing = "processing"
    completed  = "completed"
    failed     = "failed"


# ─── Auth ─────────────────────────────────────────────────────────────────────

class LoginRequest(BaseModel):
    email:    EmailStr
    password: str = Field(min_length=8)


class TokenResponse(BaseModel):
    access_token: str
    token_type:   str = "bearer"
    expires_in:   int
    user:         "UserBasic"


class RegisterRequest(BaseModel):
    name:     str      = Field(min_length=2, max_length=200)
    email:    EmailStr
    password: str      = Field(min_length=8, max_length=100)

    @field_validator("password")
    @classmethod
    def password_strength(cls, v: str) -> str:
        if not any(c.isupper() for c in v):
            raise ValueError("La contraseña debe tener al menos una mayúscula")
        if not any(c.isdigit() for c in v):
            raise ValueError("La contraseña debe tener al menos un número")
        return v


# ─── Users ────────────────────────────────────────────────────────────────────

class UserBasic(BaseModel):
    id:         int
    name:       str
    email:      str
    created_at: datetime

    model_config = {"from_attributes": True}


class UserCreate(BaseModel):
    name:  str      = Field(min_length=2, max_length=200)
    email: EmailStr


class UserSummary(BaseModel):
    id:               int
    name:             str
    email:            str
    total_purchases:  int
    total_spent:      Decimal
    created_at:       datetime

    model_config = {"from_attributes": True}


class UserDetail(UserSummary):
    avg_per_purchase:      Decimal
    favorite_product:      Optional[str]
    most_used_payment:     Optional[str]
    last_purchase_date:    Optional[date]


class AnalysisSummary(BaseModel):
    user_id:   int
    user_name: str
    period:    dict
    summary:   dict
    top_products:     List[dict]
    payment_methods:  dict


# ─── Purchases ───────────────────────────────────────────────────────────────

class PurchaseCreate(BaseModel):
    user_id:        int
    product:        str  = Field(min_length=1, max_length=300)
    quantity:       int  = Field(gt=0, description="Debe ser mayor a 0")
    price:          Decimal = Field(ge=0, description="No puede ser negativo")
    purchase_date:  date
    purchase_time:  time
    payment_method: PaymentMethodEnum


class PurchaseResponse(BaseModel):
    id:             int
    user_id:        int
    user_name:      str
    product:        str
    quantity:       int
    price:          Decimal
    total:          Decimal
    purchase_date:  date
    purchase_time:  time
    payment_method: str
    created_at:     datetime

    model_config = {"from_attributes": True}


class PurchaseList(BaseModel):
    total: int
    page:  int
    limit: int
    data:  List[PurchaseResponse]


# ─── Imports ─────────────────────────────────────────────────────────────────

class ImportResponse(BaseModel):
    import_id:    int
    status:       ImportStatusEnum
    filename:     str
    rows_detected: int
    preview:      List[dict]
    validation:   dict

    model_config = {"from_attributes": True}


class ImportConfirmResponse(BaseModel):
    import_id:     int
    status:        ImportStatusEnum
    rows_imported: int
    rows_skipped:  int
    filename:      str
    created_at:    datetime

    model_config = {"from_attributes": True}


class ImportDetail(BaseModel):
    id:                int
    filename:          str
    status:            ImportStatusEnum
    rows_imported:     int
    rows_skipped:      int
    uploader_name:     Optional[str]
    uploader_email:    Optional[str]
    error_report_url:  Optional[str]
    created_at:        datetime

    model_config = {"from_attributes": True}


# ─── Paginación genérica ─────────────────────────────────────────────────────

class PaginatedUsers(BaseModel):
    total: int
    page:  int
    limit: int
    data:  List[UserSummary]
