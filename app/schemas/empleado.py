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
    cedula: int

    class Config:
        from_attributes = True


class EmpleadoUpdate(BaseModel):
    nombre: Optional[str] = None
    rol: Optional[str] = None

class EmpleadoPut(BaseModel):
    nombre: str
    rol: str