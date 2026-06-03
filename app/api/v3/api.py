from fastapi import APIRouter
from app.api.v3.endpoints import empleados, labores, registro_labores

api_router_v3 = APIRouter()

api_router_v3.include_router(empleados.router, prefix="/empleados", tags=["Empleados"])
api_router_v3.include_router(labores.router, prefix="/labores", tags=["Labores"])
api_router_v3.include_router(
    registro_labores.router, prefix="/registrolabores", tags=["RegistroLabores"]
)
