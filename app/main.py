from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from sqlalchemy.exc import SQLAlchemyError
from app.api.v1.api import api_router

from app.db.session import engine, Base
import app.db.base  # importa los modelos para que Base los conozca

app = FastAPI()


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


app.include_router(api_router, prefix="/api/v1")
