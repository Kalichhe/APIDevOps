from fastapi import APIRouter
from app.api.v1.endpoints import empleados

api_router = APIRouter()
api_router.include_router(empleados.router, prefix="/empleados", tags=["Empleados"])
