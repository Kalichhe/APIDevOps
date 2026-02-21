from pydantic import BaseModel
from typing import Optional


# Base del empleado
class EmpleadoBase(BaseModel):
    cedula: int
    nombre: str
    rol: str


# Crear un empleado, que hereda de la clase EmpleadoBase
class EmpleadoCreate(EmpleadoBase):
    pass


# Busca a un empleado
class EmpleadoRead(EmpleadoBase):
    id: int

    # Permite que FastAPI transforme el dato de entrada id que viene en str a int
    class Config:
        from_attributes = True


# Actualiza a un empleado, pero los datos que se requieran, no todos son obligatorios
class EmpleadoUpdate(EmpleadoBase):
    cedula: Optional[str] = None
    nombre: Optional[str] = None
    rol: Optional[str] = None
