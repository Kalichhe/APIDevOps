from fastapi import FastAPI
from app.api.v1.api import api_router

from app.db.session import engine, Base
import app.db.base  # importa los modelos para que Base los conozca

app = FastAPI()

# Crea las tablas al iniciar la app
Base.metadata.create_all(bind=engine)

app.include_router(api_router, prefix="/api/v1")