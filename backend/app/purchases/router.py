"""
Router de compras: registro, listado y exportación.
"""
import csv
import io
from datetime import date, datetime, timedelta
from decimal import Decimal
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Query, Request, status
from fastapi.responses import StreamingResponse
from sqlalchemy import func, desc
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import User, Purchase, Product, AuditLog
from app.schemas import PurchaseCreate, PurchaseResponse, PurchaseList
from app.auth.security import get_current_user

router = APIRouter(prefix="/purchases", tags=["Compras"])


# ─── Ruta de prueba ───────────────────────────────────────────────────────────

@router.get("/test/{purchase_id}", summary="Ruta de prueba")
def test_purchase_route(
    purchase_id: int,
    db: Session = Depends(get_db),
    _: User = Depends(get_current_user),
):
    """Ruta simple de prueba en el router de purchases"""
    return {"status": "ok", "purchase_id": purchase_id}


def _get_or_create_product(db: Session, name: str) -> Product:
    """Devuelve el producto existente o crea uno nuevo."""
    product = db.query(Product).filter(
        func.lower(Product.name) == name.lower()
    ).first()
    if not product:
        product = Product(name=name.strip())
        db.add(product)
        db.flush()
    return product


# ─── Registrar compra ─────────────────────────────────────────────────────────

@router.post("", response_model=PurchaseResponse, status_code=status.HTTP_201_CREATED,
             summary="Registrar nueva compra")
def create_purchase(
    body: PurchaseCreate,
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    user = db.query(User).filter(User.id == body.user_id, User.is_active == True).first()
    if not user:
        raise HTTPException(404, "Usuario no encontrado")

    product = _get_or_create_product(db, body.product)

    purchase = Purchase(
        user_id=body.user_id,
        product_id=product.id,
        quantity=body.quantity,
        price=body.price,
        purchase_date=body.purchase_date,
        purchase_time=body.purchase_time,
        payment_method=body.payment_method.value,
    )
    db.add(purchase)

    db.add(AuditLog(
        user_id=current_user.id,
        action="CREATE_PURCHASE",
        entity_type="purchase",
        details={"product": body.product, "total": float(body.quantity * body.price)},
        ip_address=request.client.host if request.client else None,
    ))
    db.commit()
    db.refresh(purchase)

    return PurchaseResponse(
        id=purchase.id,
        user_id=purchase.user_id,
        user_name=user.name,
        product=product.name,
        quantity=purchase.quantity,
        price=purchase.price,
        total=purchase.total,
        purchase_date=purchase.purchase_date,
        purchase_time=purchase.purchase_time,
        payment_method=purchase.payment_method,
        created_at=purchase.created_at,
    )


# ─── Listar compras ───────────────────────────────────────────────────────────

@router.get("", response_model=PurchaseList, summary="Listar compras con filtros")
def list_purchases(
    user_id:   Optional[int]  = Query(None),
    from_date: Optional[date] = Query(None, alias="from"),
    to_date:   Optional[date] = Query(None, alias="to"),
    page:      int = Query(1, ge=1),
    limit:     int = Query(50, ge=1, le=200),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    q = db.query(Purchase)
    if user_id:
        q = q.filter(Purchase.user_id == user_id)
    if from_date:
        q = q.filter(Purchase.purchase_date >= from_date)
    if to_date:
        q = q.filter(Purchase.purchase_date <= to_date)

    total = q.count()
    purchases = (
        q.order_by(desc(Purchase.purchase_date), desc(Purchase.purchase_time))
        .offset((page - 1) * limit)
        .limit(limit)
        .all()
    )

    data = [
        PurchaseResponse(
            id=p.id,
            user_id=p.user_id,
            user_name=p.user.name,
            product=p.product.name,
            quantity=p.quantity,
            price=p.price,
            total=p.total,
            purchase_date=p.purchase_date,
            purchase_time=p.purchase_time,
            payment_method=p.payment_method,
            created_at=p.created_at,
        )
        for p in purchases
    ]
    return PurchaseList(total=total, page=page, limit=limit, data=data)


# ─── Exportar CSV ─────────────────────────────────────────────────────────────

@router.get("/export/csv", summary="Exportar compras en CSV")
def export_purchases_csv(
    user_id:   Optional[int]  = Query(None),
    from_date: Optional[date] = Query(None, alias="from"),
    to_date:   Optional[date] = Query(None, alias="to"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    q = db.query(Purchase)
    if user_id:
        q = q.filter(Purchase.user_id == user_id)
    if from_date:
        q = q.filter(Purchase.purchase_date >= from_date)
    if to_date:
        q = q.filter(Purchase.purchase_date <= to_date)

    purchases = q.order_by(desc(Purchase.purchase_date)).all()

    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(["ID", "Usuario", "Producto", "Cantidad", "Precio", "Total",
                     "Fecha", "Hora", "Método de Pago"])
    for p in purchases:
        writer.writerow([
            p.id, p.user.name, p.product.name, p.quantity,
            float(p.price), float(p.total),
            str(p.purchase_date), str(p.purchase_time), p.payment_method,
        ])

    output.seek(0)
    return StreamingResponse(
        iter([output.getvalue()]),
        media_type="text/csv",
        headers={"Content-Disposition": "attachment; filename=compras.csv"},
    )


# ─── Eliminar compra ──────────────────────────────────────────────────────────

@router.delete("/{purchase_id}", summary="Eliminar compra")
def delete_purchase(
    purchase_id: int,
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    purchase = db.query(Purchase).filter(Purchase.id == purchase_id).first()
    if not purchase:
        raise HTTPException(404, "Compra no encontrada")

    db.add(AuditLog(
        user_id=current_user.id,
        action="DELETE_PURCHASE",
        entity_type="purchase",
        entity_id=purchase_id,
        details={"product": purchase.product.name, "user_id": purchase.user_id},
        ip_address=request.client.host if request.client else None,
    ))
    db.delete(purchase)
    db.commit()
    return {"message": "Compra eliminada correctamente"}
