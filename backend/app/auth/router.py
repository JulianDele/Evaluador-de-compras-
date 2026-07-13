"""
Router de autenticación: login y registro de usuarios.
"""
from fastapi import APIRouter, Depends, HTTPException, status, Request
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import User, AuditLog
from app.schemas import LoginRequest, TokenResponse, UserBasic
from app.auth.security import hash_password, verify_password, create_access_token, get_current_user
from app.config import settings

router = APIRouter(prefix="/auth", tags=["Autenticación"])


def _log(db: Session, user_id: int | None, action: str, details: dict, request: Request) -> None:
    log = AuditLog(
        user_id=user_id,
        action=action,
        entity_type="auth",
        details=details,
        ip_address=request.client.host if request.client else None,
    )
    db.add(log)
    db.commit()


@router.post("/login", response_model=TokenResponse, summary="Iniciar sesión")
def login(body: LoginRequest, request: Request, db: Session = Depends(get_db)):
    user = db.query(User).filter(
        User.email == body.email.lower(),
        User.is_active == True
    ).first()

    if not user or not verify_password(body.password, user.password_hash):
        _log(db, None, "LOGIN_FAILED", {"email": body.email}, request)
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Credenciales incorrectas",
        )

    token = create_access_token(user.id)
    _log(db, user.id, "LOGIN", {"email": user.email}, request)

    return TokenResponse(
        access_token=token,
        expires_in=settings.jwt_expire_hours * 3600,
        user=UserBasic.model_validate(user),
    )
