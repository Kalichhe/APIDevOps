from fastapi import APIRouter
from app.api.v1.endpoints import registro_labores
from app.api.v1.endpoints import empleados, labores, registro_labores

api_router = APIRouter()

api_router.include_router(empleados.router, prefix="/empleados", tags=["Empleados"])
api_router.include_router(labores.router, prefix="/labores", tags=["Labores"])
api_router.include_router(
    registro_labores.router, prefix="/registrolabores", tags=["RegistroLabores"]
)
