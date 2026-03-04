from fastapi import FastAPI
from app.api.v1.api import api_router
from app.db.session import engine, Base
import app.db.base

app = FastAPI()

@app.get("/health")
async def health():
    return {"status": "ok"}

try:
    Base.metadata.create_all(bind=engine)
except Exception as e:
    print(f"⚠️  No se pudo conectar a la base de datos: {e}")

app.include_router(api_router, prefix="/api/v1")
