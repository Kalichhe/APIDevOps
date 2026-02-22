from pydantic import BaseModel
from typing import Optional


# Base de la labor
class LaborBase(BaseModel):
    nombre: str
    unidad_medida: str
    precio: float
    observacion: Optional[str] = None


# Crear una labor, que hereda de la clase LaborBase
class LaborCreate(LaborBase):
    pass


# Busca una labor
class LaborRead(LaborBase):
    codigo_labor: int

    # Permite que FastAPI transforme el dato de entrada id que viene en str a int
    class Config:
        from_attributes = True


# Actualiza una labor, pero los datos que se requieran, no todos son obligatorios
class LaborUpdate(LaborBase):
    nombre: Optional[str] = None
    unidad_medida: Optional[str] = None
    precio: Optional[float] = None
    observacion: Optional[str] = None
