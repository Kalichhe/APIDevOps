from pydantic import BaseModel, ConfigDict
from typing import Optional


class EmpleadoBase(BaseModel):
    cedula: int
    nombre: str
    rol: str


class EmpleadoCreate(EmpleadoBase):
    pass


class EmpleadoRead(EmpleadoBase):
    data_json: Optional[dict] = None
    model_config = ConfigDict(from_attributes=True)


class EmpleadoUpdate(BaseModel):
    nombre: Optional[str] = None
    rol: Optional[str] = None


class EmpleadoPut(BaseModel):
    nombre: str
    rol: str


class EmpleadoMessageDirectorBase(BaseModel):
    nombre: Optional[str] = None
    jsonEmpleado: EmpleadoRead


class EmpleadoMessageDirectorCreate(BaseModel):
    nombre: Optional[str] = None
    jsonEmpleado: EmpleadoCreate


class EmpleadoMessageDirectorUpdate(BaseModel):
    nombre: Optional[str] = None
    jsonEmpleado: EmpleadoUpdate


class EmpleadoMessageDirectorPut(BaseModel):
    nombre: Optional[str] = None
    jsonEmpleado: EmpleadoPut


class EmpleadoMessageCreate(BaseModel):
    model_config = ConfigDict(extra="ignore")
    documento: Optional[str] = None
    nombres: Optional[str] = None
    apellidos: Optional[str] = None
    especialidad: Optional[str] = None
    durationCitaMinutos: Optional[int] = None
    jsonDirector: EmpleadoMessageDirectorCreate


class EmpleadoMessageUpdate(BaseModel):
    model_config = ConfigDict(extra="ignore")
    documento: Optional[str] = None
    nombres: Optional[str] = None
    apellidos: Optional[str] = None
    especialidad: Optional[str] = None
    durationCitaMinutos: Optional[int] = None
    jsonDirector: EmpleadoMessageDirectorUpdate


class EmpleadoMessagePut(BaseModel):
    model_config = ConfigDict(extra="ignore")
    documento: Optional[str] = None
    nombres: Optional[str] = None
    apellidos: Optional[str] = None
    especialidad: Optional[str] = None
    durationCitaMinutos: Optional[int] = None
    jsonDirector: EmpleadoMessageDirectorPut


class EmpleadoMessageRead(BaseModel):
    model_config = ConfigDict(extra="ignore")
    documento: Optional[str] = None
    nombres: Optional[str] = None
    apellidos: Optional[str] = None
    especialidad: Optional[str] = None
    durationCitaMinutos: Optional[int] = None
    jsonDirector: EmpleadoMessageDirectorBase
