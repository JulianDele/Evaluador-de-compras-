"""
Punto de entrada principal de la aplicación FastAPI — Consumo Estratégico.
"""
import os
import re
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

# ─── Middlewares ──────────────────────────────────────────────────────────────

app.add_middleware(
    CORSMiddleware,
    allow_origin_regex=r"https://.*\.vercel\.app|http://localhost.*" if "*" in settings.allowed_origins else None,
    allow_origins=[o for o in cors_origins if "*" not in o] if "*" in settings.allowed_origins else cors_origins,
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
