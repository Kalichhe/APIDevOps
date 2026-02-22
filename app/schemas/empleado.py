from pydantic import BaseModel
from typing import Optional


# Base del empleado
class EmpleadoBase(BaseModel):
    cedula: int
    nombre: str
    rol: str


class EmpleadoCreate(EmpleadoBase):
    pass


class EmpleadoRead(EmpleadoBase):
    id: int

    class Config:
        from_attributes = True


class EmpleadoUpdate(BaseModel):
    cedula: Optional[str] = None
    nombre: Optional[str] = None
    rol: Optional[str] = None
