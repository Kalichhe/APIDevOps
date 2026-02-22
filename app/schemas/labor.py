from pydantic import BaseModel
from typing import Optional


class LaborBase(BaseModel):
    codigo_labor: str
    nombre: str
    unidad_medida: str
    precio: float
    observacion: Optional[str] = None


class LaborCreate(LaborBase):
    pass


class LaborRead(LaborBase):
    codigo_labor: str

    class Config:
        from_attributes = True


class LaborUpdate(BaseModel):
    nombre: Optional[str] = None
    unidad_medida: Optional[str] = None
    precio: Optional[float] = None
    observacion: Optional[str] = None
