import os
import secrets

from fastapi import FastAPI, Header, HTTPException, Query, Request
from fastapi.responses import JSONResponse, RedirectResponse, Response
from sqlalchemy.exc import SQLAlchemyError
from app.api.v1.api import api_router_v1
from app.api.v2.api import api_router_v2
from app.core.monitoring import (
    MetricsMiddleware,
    setup_logging,
)


from app.db.session import engine, Base
import app.db.base  # importa los modelos para que Base los conozca

# ── Configurar logging ──
setup_logging()

app = FastAPI(
    version="1.0.0",
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
    return {
        "status": "healthy",
        "version": "1.0.0",
        "database": "connected",
    }


app.include_router(api_router_v1, prefix="/api/v1")
app.include_router(api_router_v2, prefix="/api/v2")
