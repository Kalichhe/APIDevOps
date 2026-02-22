from fastapi import APIRouter
from app.api.v1.endpoints import registro_labores

api_router = APIRouter()
api_router.include_router(registro_labores.router, prefix="/registrolabores", tags=["RegistroLabores"])