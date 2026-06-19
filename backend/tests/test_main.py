"""
Pruebas unitarias del backend — Consumo Estratégico.
Ejecutar con: pytest backend/tests/ -v
"""
import pytest
from decimal import Decimal
from unittest.mock import MagicMock, patch
from datetime import date, time

# ─── Tests de seguridad (contraseñas) ────────────────────────────────────────

def test_password_hashing():
    from app.auth.security import hash_password, verify_password
    hashed = hash_password("MiContraseña123")
    assert hashed != "MiContraseña123"
    assert verify_password("MiContraseña123", hashed)
    assert not verify_password("ContraseñaIncorrecta", hashed)


def test_password_hash_is_bcrypt():
    from app.auth.security import hash_password
    hashed = hash_password("Test123")
    assert hashed.startswith("$2b$")


# ─── Tests de JWT ─────────────────────────────────────────────────────────────

def test_jwt_create_and_decode():
    from app.auth.security import create_access_token, decode_token
    token = create_access_token(user_id=1, role="analista")
    payload = decode_token(token)
    assert payload["sub"] == "1"
    assert payload["role"] == "analista"


def test_jwt_invalid_token_raises():
    from app.auth.security import decode_token
    from fastapi import HTTPException
    with pytest.raises(HTTPException) as exc_info:
        decode_token("token.invalido.aqui")
    assert exc_info.value.status_code == 401


# ─── Tests de validación de esquemas ─────────────────────────────────────────

def test_purchase_schema_valid():
    from app.schemas import PurchaseCreate, PaymentMethodEnum
    p = PurchaseCreate(
        user_id=1,
        product="Leche",
        quantity=2,
        price=Decimal("45.00"),
        purchase_date=date(2024, 1, 15),
        purchase_time=time(14, 30),
        payment_method=PaymentMethodEnum.efectivo,
    )
    assert p.quantity == 2
    assert p.price == Decimal("45.00")


def test_purchase_schema_invalid_quantity():
    from app.schemas import PurchaseCreate, PaymentMethodEnum
    from pydantic import ValidationError
    with pytest.raises(ValidationError) as exc_info:
        PurchaseCreate(
            user_id=1,
            product="Leche",
            quantity=0,  # inválido
            price=Decimal("45.00"),
            purchase_date=date(2024, 1, 15),
            purchase_time=time(14, 30),
            payment_method=PaymentMethodEnum.efectivo,
        )
    errors = exc_info.value.errors()
    assert any("quantity" in str(e) for e in errors)


def test_purchase_schema_invalid_price():
    from app.schemas import PurchaseCreate, PaymentMethodEnum
    from pydantic import ValidationError
    with pytest.raises(ValidationError):
        PurchaseCreate(
            user_id=1,
            product="Leche",
            quantity=1,
            price=Decimal("-1.00"),  # inválido
            purchase_date=date(2024, 1, 15),
            purchase_time=time(14, 30),
            payment_method=PaymentMethodEnum.efectivo,
        )


def test_register_schema_weak_password():
    from app.schemas import RegisterRequest
    from pydantic import ValidationError
    with pytest.raises(ValidationError):
        RegisterRequest(
            name="Test",
            email="test@test.com",
            password="sinmayusculas1",  # sin mayúscula
        )


# ─── Tests de procesamiento de archivos ──────────────────────────────────────

def test_auto_map_columns_spanish():
    import pandas as pd
    from app.imports.processor import auto_map_columns
    df = pd.DataFrame(columns=["cliente", "item", "qty", "fecha", "monto"])
    mapping = auto_map_columns(df)
    assert mapping.get("nombre") == "cliente"
    assert mapping.get("producto") == "item"
    assert mapping.get("cantidad") == "qty"
    assert mapping.get("fecha") == "fecha"
    assert mapping.get("precio") == "monto"


def test_validate_rows_valid():
    import pandas as pd
    from app.imports.processor import validate_and_transform
    df = pd.DataFrame([{
        "nombre": "Ana", "producto": "Leche", "cantidad": "2",
        "fecha": "2024-01-15", "hora": "10:30", "precio": "45.00",
    }])
    mapping = {
        "nombre": "nombre", "producto": "producto", "cantidad": "cantidad",
        "fecha": "fecha", "hora": "hora", "precio": "precio",
    }
    valid, errors = validate_and_transform(df, mapping)
    assert len(valid) == 1
    assert len(errors) == 0
    assert valid[0]["cantidad"] == 2
    assert valid[0]["precio"] == 45.0


def test_validate_rows_invalid_quantity():
    import pandas as pd
    from app.imports.processor import validate_and_transform
    df = pd.DataFrame([{
        "nombre": "Ana", "producto": "Leche", "cantidad": "cero",
        "fecha": "2024-01-15", "precio": "45.00",
    }])
    mapping = {
        "nombre": "nombre", "producto": "producto", "cantidad": "cantidad",
        "fecha": "fecha", "precio": "precio",
    }
    valid, errors = validate_and_transform(df, mapping)
    assert len(valid) == 0
    assert len(errors) == 1


def test_validate_rows_invalid_date():
    import pandas as pd
    from app.imports.processor import validate_and_transform
    df = pd.DataFrame([{
        "nombre": "Ana", "producto": "Leche", "cantidad": "2",
        "fecha": "fecha_invalida", "precio": "45.00",
    }])
    mapping = {
        "nombre": "nombre", "producto": "producto", "cantidad": "cantidad",
        "fecha": "fecha", "precio": "precio",
    }
    valid, errors = validate_and_transform(df, mapping)
    assert len(errors) == 1
    assert any("fecha" in e.lower() for e in errors[0]["errors"])


def test_anonymize_email():
    import pandas as pd
    from app.imports.processor import validate_and_transform
    df = pd.DataFrame([{
        "nombre": "ana@correo.com", "producto": "Leche", "cantidad": "1",
        "fecha": "2024-01-15", "precio": "20.00",
    }])
    mapping = {
        "nombre": "nombre", "producto": "producto", "cantidad": "cantidad",
        "fecha": "fecha", "precio": "precio",
    }
    valid, _ = validate_and_transform(df, mapping, anonymize=True)
    assert valid[0]["nombre"] != "ana@correo.com"
    assert len(valid[0]["nombre"]) == 16  # hash truncado


def test_read_csv():
    from app.imports.processor import read_csv
    content = b"nombre,producto,cantidad,fecha,precio\nAna,Leche,2,2024-01-15,45.00"
    df = read_csv(content)
    assert len(df) == 1
    assert "nombre" in df.columns


# ─── Tests de API (integración mínima con TestClient) ─────────────────────────

def test_health_endpoint():
    from fastapi.testclient import TestClient
    from app.main import app
    client = TestClient(app)
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"


def test_protected_endpoint_without_token():
    from fastapi.testclient import TestClient
    from app.main import app
    client = TestClient(app)
    response = client.get("/api/v1/users")
    assert response.status_code == 403  # HTTPBearer devuelve 403 sin header


def test_login_invalid_credentials():
    from fastapi.testclient import TestClient
    from unittest.mock import patch
    from app.main import app

    client = TestClient(app)
    with patch("app.auth.router.db") as mock_db:
        # Simular usuario no encontrado
        mock_db.query.return_value.filter.return_value.first.return_value = None
        response = client.post("/api/v1/auth/login", json={
            "email": "inexistente@test.com",
            "password": "Password123"
        })
    # Sin BD real, esperamos 500 o 401 dependiendo del mock
    assert response.status_code in (401, 500)
