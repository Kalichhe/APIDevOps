from pydantic import BaseModel
from typing import Optional
from datetime import date


class RegistroLaborBase(BaseModel):
    empleado_id: int
    codigo_labor: str
    fecha: date
    cantidad: float
    observacion: Optional[str] = None


class RegistroLaborCreate(RegistroLaborBase):
    pass


class RegistroLaborRead(RegistroLaborBase):
    id: int

    class Config:
        from_attributes = True


class RegistroLaborUpdate(RegistroLaborBase):
    empleado_id: Optional[int] = None
    codigo_labor: Optional[str] = None
    fecha: Optional[date] = None
    cantidad: Optional[float] = None
    observacion: Optional[str] = None
