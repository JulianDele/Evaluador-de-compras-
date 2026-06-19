"""
Router de usuarios: CRUD y análisis de compras.
"""
from datetime import date
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Query, Request, status
from sqlalchemy import func, desc
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import User, Purchase, Product, AuditLog
from app.schemas import (
    UserCreate, UserSummary, UserDetail, AnalysisSummary,
    PaginatedUsers,
)
from app.auth.security import get_current_user

router = APIRouter(prefix="/users", tags=["Usuarios"])


# ─── Listar usuarios ──────────────────────────────────────────────────────────

@router.get("", response_model=PaginatedUsers, summary="Listar usuarios con resumen")
def list_users(
    page:   int = Query(1, ge=1),
    limit:  int = Query(20, ge=1, le=100),
    search: Optional[str] = Query(None),
    db: Session = Depends(get_db),
    _: User = Depends(get_current_user),
):
    q = db.query(User)
    if search:
        q = q.filter(User.name.ilike(f"%{search}%"))

    total = q.count()
    users = q.order_by(User.name).offset((page - 1) * limit).limit(limit).all()

    data = []
    for u in users:
        stats = db.query(
            func.count(Purchase.id).label("total_purchases"),
            func.coalesce(func.sum(Purchase.quantity * Purchase.price), 0).label("total_spent"),
        ).filter(Purchase.user_id == u.id).one()

        data.append(UserSummary(
            id=u.id,
            name=u.name,
            email=u.email,
            total_purchases=stats.total_purchases,
            total_spent=stats.total_spent,
            created_at=u.created_at,
        ))

    return PaginatedUsers(total=total, page=page, limit=limit, data=data)


# ─── Crear usuario ────────────────────────────────────────────────────────────

@router.post("", response_model=UserSummary, status_code=status.HTTP_201_CREATED,
             summary="Crear usuario nuevo")
def create_user(
    body: UserCreate,
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    existing = db.query(User).filter(User.email == body.email.lower()).first()
    if existing:
        raise HTTPException(400, "Ya existe un usuario con ese correo electrónico")

    # Contraseña temporal — el usuario deberá cambiarla al primer login
    from app.auth.security import hash_password
    import secrets
    temp_pass = secrets.token_urlsafe(16)

    new_user = User(
        name=body.name,
        email=body.email.lower(),
        password_hash=hash_password(temp_pass),
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    db.add(AuditLog(
        user_id=current_user.id,
        action="CREATE_USER",
        entity_type="user",
        entity_id=new_user.id,
        details={"name": new_user.name, "email": new_user.email},
        ip_address=request.client.host if request.client else None,
    ))
    db.commit()

    return UserSummary(
        id=new_user.id,
        name=new_user.name,
        email=new_user.email,
        total_purchases=0,
        total_spent=0,
        created_at=new_user.created_at,
    )


# ─── Obtener usuario ──────────────────────────────────────────────────────────

@router.get("/{user_id}", response_model=UserDetail, summary="Detalle de usuario")
def get_user(
    user_id: int,
    db: Session = Depends(get_db),
    _: User = Depends(get_current_user),
):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(404, "Usuario no encontrado")

    stats = db.query(
        func.count(Purchase.id).label("total_purchases"),
        func.coalesce(func.sum(Purchase.quantity * Purchase.price), 0).label("total_spent"),
        func.coalesce(func.avg(Purchase.quantity * Purchase.price), 0).label("avg_per_purchase"),
        func.max(Purchase.purchase_date).label("last_purchase_date"),
    ).filter(Purchase.user_id == user_id).one()

    # Producto favorito
    fav = (
        db.query(Product.name, func.count(Purchase.id).label("cnt"))
        .join(Purchase, Purchase.product_id == Product.id)
        .filter(Purchase.user_id == user_id)
        .group_by(Product.name)
        .order_by(desc("cnt"))
        .first()
    )

    # Método de pago más usado
    pay = (
        db.query(Purchase.payment_method, func.count(Purchase.id).label("cnt"))
        .filter(Purchase.user_id == user_id)
        .group_by(Purchase.payment_method)
        .order_by(desc("cnt"))
        .first()
    )

    return UserDetail(
        id=user.id,
        name=user.name,
        email=user.email,
        total_purchases=stats.total_purchases,
        total_spent=stats.total_spent,
        avg_per_purchase=stats.avg_per_purchase,
        favorite_product=fav[0] if fav else None,
        most_used_payment=pay[0] if pay else None,
        last_purchase_date=stats.last_purchase_date,
        created_at=user.created_at,
    )


# ─── Resumen analítico ────────────────────────────────────────────────────────

@router.get("/{user_id}/summary", response_model=AnalysisSummary,
            summary="Resumen analítico de compras del usuario")
def get_user_summary(
    user_id: int,
    from_date: Optional[date] = Query(None, alias="from"),
    to_date:   Optional[date] = Query(None, alias="to"),
    db: Session = Depends(get_db),
    _: User = Depends(get_current_user),
):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(404, "Usuario no encontrado")

    q = db.query(Purchase).filter(Purchase.user_id == user_id)
    if from_date:
        q = q.filter(Purchase.purchase_date >= from_date)
    if to_date:
        q = q.filter(Purchase.purchase_date <= to_date)

    purchases = q.all()
    totals = [(p.quantity * p.price) for p in purchases]
    total_spent = sum(totals)
    avg = total_spent / len(totals) if totals else 0

    # Top productos
    from collections import Counter
    product_counts: dict = {}
    product_spent:  dict = {}
    payment_counts: Counter = Counter()

    for p in purchases:
        pname = p.product.name
        product_counts[pname] = product_counts.get(pname, 0) + 1
        product_spent[pname]  = product_spent.get(pname, 0) + float(p.quantity * p.price)
        payment_counts[p.payment_method] += 1

    top_products = [
        {"product": name, "count": cnt, "total_spent": round(product_spent[name], 2)}
        for name, cnt in sorted(product_counts.items(), key=lambda x: -x[1])[:5]
    ]

    fav = max(product_counts, key=product_counts.get) if product_counts else None
    fav_pay = payment_counts.most_common(1)[0][0] if payment_counts else None

    return AnalysisSummary(
        user_id=user_id,
        user_name=user.name,
        period={"from": str(from_date or ""), "to": str(to_date or "")},
        summary={
            "total_purchases": len(purchases),
            "total_spent": round(float(total_spent), 2),
            "average_per_purchase": round(float(avg), 2),
            "favorite_product": fav,
            "most_used_payment_method": fav_pay,
        },
        top_products=top_products,
        payment_methods=dict(payment_counts),
    )


# ─── Eliminar usuario ─────────────────────────────────────────────────────────

@router.delete("/{user_id}", summary="Eliminar usuario")
def delete_user(
    user_id: int,
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(404, "Usuario no encontrado")
    if user.id == current_user.id:
        raise HTTPException(400, "No puedes eliminar tu propio usuario")

    purchase_count = db.query(Purchase).filter(Purchase.user_id == user_id).count()
    db.delete(user)

    db.add(AuditLog(
        user_id=current_user.id,
        action="DELETE_USER",
        entity_type="user",
        entity_id=user_id,
        details={"deleted_name": user.name, "purchases_deleted": purchase_count},
        ip_address=request.client.host if request.client else None,
    ))
    db.commit()

    return {"message": f"Usuario y {purchase_count} compras eliminados correctamente"}
