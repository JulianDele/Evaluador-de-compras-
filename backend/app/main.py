"""
Punto de entrada principal de la aplicación FastAPI — Consumo Estratégico.
"""
import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import settings
from app.auth.router import router as auth_router
from app.users.router import router as users_router
from app.purchases.router import router as purchases_router
from app.imports.router import router as imports_router

# ─── Crear aplicación ─────────────────────────────────────────────────────────

app = FastAPI(
    title="Consumo Estratégico API",
    description="Sistema de análisis de patrones de compra y hábitos de consumo",
    version="1.0.0",
    docs_url="/docs" if settings.debug else None,
    redoc_url="/redoc" if settings.debug else None,
)

# ─── Middlewares ──────────────────────────────────────────────────────────────

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.allowed_origins_list,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*"],
)

# ─── Routers ──────────────────────────────────────────────────────────────────

API_PREFIX = "/api/v1"

app.include_router(auth_router,      prefix=API_PREFIX)
app.include_router(users_router,     prefix=API_PREFIX)
app.include_router(purchases_router, prefix=API_PREFIX)
app.include_router(imports_router,   prefix=API_PREFIX)

# ─── Endpoints de salud ───────────────────────────────────────────────────────

@app.get("/health", tags=["Sistema"], summary="Verificar estado del servidor")
def health_check():
    return {"status": "ok", "version": "1.0.0"}


@app.get("/", tags=["Sistema"])
def root():
    return {
        "app": "Consumo Estratégico API",
        "version": "1.0.0",
        "docs": "/docs",
    }
