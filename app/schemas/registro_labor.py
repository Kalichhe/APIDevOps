from pydantic import BaseModel, ConfigDict
from typing import Optional
from datetime import date


class RegistroLaborBase(BaseModel):
    id: int
    empleado_cedula: int
    codigo_labor: str
    fecha: date
    cantidad: float
    observacion: Optional[str] = None


class RegistroLaborCreate(RegistroLaborBase):
    pass


class RegistroLaborRead(RegistroLaborBase):
    id: int
    model_config = ConfigDict(from_attributes=True)


class RegistroLaborUpdate(BaseModel):
    empleado_cedula: Optional[int] = None
    codigo_labor: Optional[str] = None
    fecha: Optional[date] = None
    cantidad: Optional[float] = None
    observacion: Optional[str] = None


class RegistroLaborPut(BaseModel):
    empleado_cedula: int
    codigo_labor: str
    fecha: date
    cantidad: float
    observacion: Optional[str] = None