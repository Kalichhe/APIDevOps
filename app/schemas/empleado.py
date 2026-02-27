from pydantic import BaseModel, ConfigDict
from typing import Optional

class EmpleadoBase(BaseModel):
    cedula: int
    nombre: str
    rol: str

class EmpleadoCreate(EmpleadoBase):
    pass

class EmpleadoRead(EmpleadoBase):
    cedula: int
    model_config = ConfigDict(from_attributes=True)

class EmpleadoUpdate(BaseModel):
    nombre: Optional[str] = None
    rol: Optional[str] = None