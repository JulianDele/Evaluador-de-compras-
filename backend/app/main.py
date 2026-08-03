"""
Punto de entrada principal de la aplicación FastAPI — Consumo Estratégico.
"""
import os
import re
from datetime import date, timedelta
from typing import Optional, Callable
from fastapi import FastAPI, Depends, Query, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import Response
from starlette.requests import Request
from starlette.types import ASGIApp
from sqlalchemy.orm import Session

from app.config import settings
from app.auth.router import router as auth_router
from app.users.router import router as users_router
from app.purchases.router import router as purchases_router
from app.imports.router import router as imports_router
from app.database import get_db
from app.models import User, Purchase
from app.auth.security import get_current_user


class CORSOptionsMiddleware:
    """Middleware ASGI puro para manejar preflight CORS OPTIONS requests."""
    
    def __init__(self, app: ASGIApp):
        self.app = app
        self.send = None
    
    async def __call__(self, scope, receive, send):
        if scope["type"] != "http" or scope["method"] != "OPTIONS":
            await self.app(scope, receive, send)
            return
        
        # Para OPTIONS requests, interceptar y responder directamente
        async def send_wrapper(message):
            if message["type"] == "http.response.start":
                # Enviar respuesta 200 con headers CORS
                await send({
                    "type": "http.response.start",
                    "status": 200,
                    "headers": [
                        [b"access-control-allow-origin", b"*"],
                        [b"access-control-allow-methods", b"GET, POST, PUT, DELETE, PATCH, OPTIONS"],
                        [b"access-control-allow-headers", b"*"],
                        [b"access-control-allow-credentials", b"true"],
                        [b"access-control-max-age", b"86400"],
                        [b"content-type", b"text/plain"],
                        [b"content-length", b"0"],
                    ],
                })
            elif message["type"] == "http.response.body":
                # Enviar body vacío
                await send({
                    "type": "http.response.body",
                    "body": b"",
                })
        
        await self.app(scope, receive, send_wrapper)


# ─── Middleware ASGI BaseHTTPMiddleware para preflight CORS ────────────────────

class ASGICORSPreflight(BaseHTTPMiddleware):
    """Middleware que responde a OPTIONS requests con CORS headers."""
    
    async def dispatch(self, request: Request, call_next):
        print(f"🔵 ASGICORSPreflight: {request.method} {request.url.path}", flush=True)
        
        if request.method == "OPTIONS":
            print(f"📋 OPTIONS preflight intercepted: {request.url.path}", flush=True)
            return Response(
                content="",
                status_code=200,
                headers={
                    "Access-Control-Allow-Origin": "*",
                    "Access-Control-Allow-Methods": "GET, POST, PUT, DELETE, PATCH, OPTIONS",
                    "Access-Control-Allow-Headers": "content-type, authorization",
                    "Access-Control-Allow-Credentials": "true",
                    "Access-Control-Max-Age": "86400",
                }
            )
        
        response = await call_next(request)
        return response

# ─── Crear aplicación ─────────────────────────────────────────────────────────

app = FastAPI(
    title="Consumo Estratégico API",
    description="Sistema de análisis de patrones de compra y hábitos de consumo",
    version="1.0.0",
    docs_url="/docs" if settings.debug else None,
    redoc_url="/redoc" if settings.debug else None,
)

# ─── Procesar CORS con soporte para wildcards ─────────────────────────────────

def process_cors_origins(origins_str: str) -> list:
    """Convierte lista de origins con wildcards a lista para CORSMiddleware."""
    origins_list = []
    for origin in origins_str.split(","):
        origin = origin.strip()
        if not origin:
            continue
        # Si contiene *, permitir como patrón regex
        if "*" in origin:
            # Convertir wildcard a patrón que CORSMiddleware entienda
            # FastAPI permite regex patterns
            pattern = origin.replace(".", r"\.").replace("*", ".*")
            origins_list.append(pattern)
        else:
            origins_list.append(origin)
    return origins_list

cors_origins = process_cors_origins(settings.allowed_origins)

# ─── Agregar middlewares (el último agregado se ejecuta PRIMERO) ──────────────

# Agregar middleware de CORS preflight ÚLTIMO (se ejecuta PRIMERO)
app.add_middleware(ASGICORSPreflight)

# Agregar CORSMiddleware (se ejecuta SEGUNDO)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["*"],
)

# Agregar middleware ASGI puro para OPTIONS (se ejecuta TERCERO)
app.add_middleware(CORSOptionsMiddleware)

# ─── Routers ──────────────────────────────────────────────────────────────────

API_PREFIX = "/api/v1"

app.include_router(auth_router,      prefix=API_PREFIX)

# ─── NOTA IMPORTANTE: Las rutas directas en app DEBEN ir antes de include_router
# para que FastAPI las priorice sobre los patrones parametrizados del router.
# Esto es necesario porque el router de usuarios tiene un patrón `/{user_id}` 
# que coincide con CUALQUIER segmento de URL, causando conflictos de ruteo.

@app.get("/test-forecast-route")
def test_route():
    return {"message": "test route works"}

@app.get("/forecast-purchases", summary="Predecir compras futuras")
def predict_future_purchases_direct(
    user_id: int = Query(..., description="ID del usuario"),
    db: Session = Depends(get_db),
    _: User = Depends(get_current_user),
):
    """Predice productos y cantidades que el usuario probablemente comprará en el futuro."""
    
    user = db.query(User).filter(User.id == user_id, User.is_active == True).first()
    if not user:
        raise HTTPException(404, "Usuario no encontrado")
    
    # Obtener todas las compras del usuario (últimos 12 meses)
    cutoff_date = date.today() - timedelta(days=365)
    purchases = db.query(Purchase).filter(
        Purchase.user_id == user_id,
        Purchase.purchase_date >= cutoff_date,
    ).all()
    
    if not purchases:
        return {"predictions": []}
    
    # Agrupar por producto y calcular estadísticas
    product_stats = {}
    for purchase in purchases:
        key = purchase.product.name
        if key not in product_stats:
            product_stats[key] = {
                "product": key,
                "dates": [],
                "quantities": [],
                "prices": [],
                "total_spent": 0,
            }
        
        product_stats[key]["dates"].append(purchase.purchase_date)
        product_stats[key]["quantities"].append(purchase.quantity)
        product_stats[key]["prices"].append(float(purchase.price))
        product_stats[key]["total_spent"] += float(purchase.quantity * purchase.price)
    
    predictions = []
    today = date.today()
    
    for product_name, stats in product_stats.items():
        if len(stats["dates"]) < 2:
            continue
        
        # Calcular días entre compras (frecuencia)
        sorted_dates = sorted(stats["dates"])
        intervals = []
        for i in range(1, len(sorted_dates)):
            delta = (sorted_dates[i] - sorted_dates[i-1]).days
            if delta > 0:
                intervals.append(delta)
        
        if not intervals:
            continue
        
        # Promedios
        avg_days = sum(intervals) / len(intervals)
        avg_quantity = sum(stats["quantities"]) / len(stats["quantities"])
        avg_price = sum(stats["prices"]) / len(stats["prices"])
        
        # Predecir fecha de próxima compra
        last_date = sorted_dates[-1]
        predicted_date = last_date + timedelta(days=avg_days)
        
        # Solo incluir predicciones dentro de los próximos 30 días
        days_until_prediction = (predicted_date - today).days
        if 0 <= days_until_prediction <= 30:
            predictions.append({
                "product": product_name,
                "predicted_quantity": round(avg_quantity),
                "predicted_price": round(avg_price, 2),
                "predicted_total": round(avg_quantity * avg_price, 2),
                "predicted_date": predicted_date.isoformat(),
                "frequency_days": round(avg_days),
                "confidence": min(100, int((len(stats["dates"]) / 12) * 100)),
                "purchase_count": len(stats["dates"]),
                "total_spent": round(stats["total_spent"], 2),
            })
    
    # Ordenar por probabilidad (confianza) de mayor a menor
    predictions.sort(key=lambda x: x["confidence"], reverse=True)
    
    return {"predictions": predictions[:10]}  # Top 10 predicciones

@app.get("/test-query")
def test_query(test_param: Optional[str] = Query(None)):
    """Endpoint de prueba para ver si FastAPI recibe los query parameters."""
    return {"received_test_param": test_param}

app.include_router(users_router,     prefix=API_PREFIX)
app.include_router(purchases_router, prefix=API_PREFIX)
app.include_router(imports_router,   prefix=API_PREFIX)

# ─── Endpoints de salud ───────────────────────────────────────────────────────

@app.get("/simple", tags=["Test"], summary="Ruta de prueba simple")
def simple_test():
    return {"status": "ok"}


@app.get("/health", tags=["Sistema"], summary="Verificar estado del servidor")
def health_check(user_id: Optional[int] = Query(None)):
    """Verifica el estado del servidor. Si se proporciona user_id, retorna predicciones."""
    print(f"DEBUG: user_id = {user_id}, type = {type(user_id)}", flush=True)
    
    if user_id is None:
        return {"status": "ok", "version": "1.0.0"}
    
    # Esto es un workaround para el problema de ruteo de FastAPI
    # Las predicciones se manejan aquí en lugar de en una ruta separada
    from sqlalchemy.orm import Session as SessionLocal
    db = SessionLocal()
    
    try:
        user = db.query(User).filter(User.id == user_id, User.is_active == True).first()
        if not user:
            raise HTTPException(404, "Usuario no encontrado")
        
        # Obtener todas las compras del usuario (últimos 12 meses)
        cutoff_date = date.today() - timedelta(days=365)
        purchases = db.query(Purchase).filter(
            Purchase.user_id == user_id,
            Purchase.purchase_date >= cutoff_date,
        ).all()
        
        if not purchases:
            return {"predictions": []}
        
        # Agrupar por producto y calcular estadísticas
        product_stats = {}
        for purchase in purchases:
            key = purchase.product.name
            if key not in product_stats:
                product_stats[key] = {
                    "product": key,
                    "dates": [],
                    "quantities": [],
                    "prices": [],
                    "total_spent": 0,
                }
            
            product_stats[key]["dates"].append(purchase.purchase_date)
            product_stats[key]["quantities"].append(purchase.quantity)
            product_stats[key]["prices"].append(float(purchase.price))
            product_stats[key]["total_spent"] += float(purchase.quantity * purchase.price)
        
        predictions = []
        today = date.today()
        
        for product_name, stats in product_stats.items():
            if len(stats["dates"]) < 2:
                continue
            
            # Calcular días entre compras (frecuencia)
            sorted_dates = sorted(stats["dates"])
            intervals = []
            for i in range(1, len(sorted_dates)):
                delta = (sorted_dates[i] - sorted_dates[i-1]).days
                if delta > 0:
                    intervals.append(delta)
            
            if not intervals:
                continue
            
            # Promedios
            avg_days = sum(intervals) / len(intervals)
            avg_quantity = sum(stats["quantities"]) / len(stats["quantities"])
            avg_price = sum(stats["prices"]) / len(stats["prices"])
            
            # Predecir fecha de próxima compra
            last_date = sorted_dates[-1]
            predicted_date = last_date + timedelta(days=avg_days)
            
            # Solo incluir predicciones dentro de los próximos 30 días
            days_until_prediction = (predicted_date - today).days
            if 0 <= days_until_prediction <= 30:
                predictions.append({
                    "product": product_name,
                    "predicted_quantity": round(avg_quantity),
                    "predicted_price": round(avg_price, 2),
                    "predicted_total": round(avg_quantity * avg_price, 2),
                    "predicted_date": predicted_date.isoformat(),
                    "frequency_days": round(avg_days),
                    "confidence": min(100, int((len(stats["dates"]) / 12) * 100)),
                    "purchase_count": len(stats["dates"]),
                    "total_spent": round(stats["total_spent"], 2),
                })
        
        # Ordenar por probabilidad (confianza) de mayor a menor
        predictions.sort(key=lambda x: x["confidence"], reverse=True)
        
        return {"predictions": predictions[:10]}  # Top 10 predicciones
        
    finally:
        db.close()


@app.get("/", tags=["Sistema"])
def root():
    return {
        "app": "Consumo Estratégico API",
        "version": "1.0.0",
        "docs": "/docs",
    }

# ─── Debug: Listar todas las rutas ────────────────────────────────────────────

print("\n=== RUTAS REGISTRADAS ===", flush=True)
for route in app.routes:
    if hasattr(route, 'path'):
        print(f"  {route.methods if hasattr(route, 'methods') else 'N/A'} {route.path}", flush=True)
    elif hasattr(route, 'original_router'):
        print(f"  Router: {route.include_context.prefix}", flush=True)
        for subroute in route.original_router.routes:
            if hasattr(subroute, 'path'):
                methods = subroute.methods if hasattr(subroute, 'methods') else ['N/A']
                print(f"    {methods} {subroute.path}", flush=True)
print("=== FIN RUTAS ===\n", flush=True)

# ─── Handler de excepción para 405 (Method Not Allowed) ───────────────────────
# NOTA: esto NO funcionará para 405 porque FastAPI genera la respuesta internamente

# ─── Middleware ASGI que intercepta OPTIONS preflight ANTES de FastAPI ─────────


