from fastapi import APIRouter
from app.api.v1.endpoints import labores

api_router = APIRouter()
api_router.include_router(labores.router, prefix="/labores", tags=["Labores"])