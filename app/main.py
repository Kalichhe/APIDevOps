import os
import secrets

from fastapi import FastAPI, Header, HTTPException, Query, Request
from fastapi.responses import JSONResponse, RedirectResponse, Response
from sqlalchemy.exc import SQLAlchemyError
from app.api.v1.api import api_router_v1
from app.api.v2.api import api_router_v2
from app.api.v3.api import api_router_v3
from app.core.monitoring import (
    MetricsMiddleware,
    setup_logging,
)
from datetime import datetime


from sqlalchemy import text

from app.core.config import settings
from app.db.session import engine, Base
import app.db.base  # importa los modelos para que Base los conozca

# ── Configurar logging ──
setup_logging()

app = FastAPI(
    version="2.0.0",
    title="APIDevOps",
    description="API REST con monitoreo y observabilidad",
)

# ── Agregar middleware de monitoreo ──
app.add_middleware(MetricsMiddleware)


def _is_metrics_access_allowed(
    x_metrics_token: str | None,
    authorization: str | None,
    query_token: str | None,
) -> bool:
    expected_token = os.getenv("METRICS_TOKEN", "").strip()

    # If METRICS_TOKEN is not configured, keep local/dev behavior unchanged.
    if not expected_token:
        return True

    bearer_token = None
    if authorization and authorization.lower().startswith("bearer "):
        bearer_token = authorization[7:].strip()

    candidates = [x_metrics_token, query_token, bearer_token]
    return any(
        candidate and secrets.compare_digest(candidate, expected_token)
        for candidate in candidates
    )


@app.get("/")
async def root():
    return RedirectResponse(url="/docs")


# ── Manejador global de excepciones no controladas ──
@app.exception_handler(SQLAlchemyError)
async def sqlalchemy_exception_handler(request: Request, exc: SQLAlchemyError):
    return JSONResponse(
        status_code=500,
        content={"detail": "Error interno de base de datos. Intente más tarde."},
    )


@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    return JSONResponse(
        status_code=500,
        content={"detail": "Error interno del servidor. Intente más tarde."},
    )


# ── Crear tablas al iniciar (con manejo de conexión caída) ──
try:
    Base.metadata.create_all(bind=engine)
except Exception as e:
    print(f"⚠️  No se pudo conectar a la base de datos: {e}")


# ── Endpoints de Monitoreo y Observabilidad ──
@app.get("/metrics", tags=["Monitoring"], description="Métricas Prometheus")
async def metrics(
    x_metrics_token: str | None = Header(default=None, alias="X-Metrics-Token"),
    authorization: str | None = Header(default=None, alias="Authorization"),
    token: str | None = Query(default=None),
):
    """Expone métricas en formato Prometheus."""
    if not _is_metrics_access_allowed(x_metrics_token, authorization, token):
        raise HTTPException(status_code=403, detail="Forbidden")

    from prometheus_client import generate_latest, CONTENT_TYPE_LATEST

    return Response(content=generate_latest(), media_type=CONTENT_TYPE_LATEST)


@app.get("/health", tags=["Monitoring"], description="Health check de la aplicación")
async def health_check():
    """Verifica el estado de la aplicación y la conexión a BD."""
    try:
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        database = "connected"
    except SQLAlchemyError:
        database = "disconnected"

    payload = {
        "status": "canary",  # ← siempre "canary", sin importar la BD
        "version": settings.APP_VERSION,
        "release_channel": settings.RELEASE_CHANNEL,
        "environment": settings.ENV,
        "database": database,
        "timestamp": datetime.utcnow().isoformat(),
    }
    return JSONResponse(status_code=200, content=payload)


# ── Ingeniería del Caos: OOM Kill ──────────────────────────────
import gc
import psutil
import sys

_chaos_memory_store = []
_CHAOS_MEMORY_LIMIT_MB = 200


@app.get("/chaos/acumular-memoria", tags=["Chaos Engineering"])
async def chaos_acumular_memoria(mb: int = 50):
    """Acumula MB en RAM, pero libera memoria si se supera el límite."""
    proceso = psutil.Process()
    usado_mb = proceso.memory_info().rss / (1024 * 1024)

    if usado_mb + mb > _CHAOS_MEMORY_LIMIT_MB:
        _chaos_memory_store.clear()
        gc.collect()
        usado_tras_limpieza = psutil.Process().memory_info().rss / (1024 * 1024)
        raise HTTPException(
            status_code=429,
            detail={
                "error": "Límite alcanzado — memoria liberada automáticamente",
                "memoria_antes_MB": round(usado_mb, 2),
                "limite_MB": _CHAOS_MEMORY_LIMIT_MB,
                "memoria_tras_limpieza_MB": round(usado_tras_limpieza, 2),
            },
        )

    _chaos_memory_store.append(" " * (mb * 1024 * 1024))
    return {
        "memoria_usada_MB": round(
            psutil.Process().memory_info().rss / (1024 * 1024), 2
        ),
        "chunks_almacenados": len(_chaos_memory_store),
        "limite_MB": _CHAOS_MEMORY_LIMIT_MB,
    }


@app.get("/chaos/estado-memoria", tags=["Chaos Engineering"])
async def chaos_estado_memoria():
    usado_mb = psutil.Process().memory_info().rss / (1024 * 1024)

    # Calcula el tamaño real de lo acumulado en el store
    store_size_bytes = sum(sys.getsizeof(item) for item in _chaos_memory_store)
    store_size_mb = store_size_bytes / (1024 * 1024)

    return {
        "memoria_total_proceso_MB": round(usado_mb, 2),
        "memoria_almacenada_en_store_MB": round(store_size_mb, 2),
        "chunks_almacenados": len(_chaos_memory_store),
        "limite_interno_MB": _CHAOS_MEMORY_LIMIT_MB,
    }


@app.delete("/chaos/liberar-memoria", tags=["Chaos Engineering"])
async def chaos_liberar_memoria():
    antes = psutil.Process().memory_info().rss / (1024 * 1024)
    _chaos_memory_store.clear()
    gc.collect()
    despues = psutil.Process().memory_info().rss / (1024 * 1024)
    return {
        "memoria_antes_MB": round(antes, 2),
        "memoria_despues_MB": round(despues, 2),
        "liberado_MB": round(antes - despues, 2),
    }


app.include_router(api_router_v1, prefix="/api/v1")
app.include_router(api_router_v2, prefix="/api/v2")
app.include_router(api_router_v3, prefix="/api/v3")
