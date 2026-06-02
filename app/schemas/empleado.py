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


class EmpleadoMessageDoctorBase(BaseModel):
    documento: Optional[str] = None
    nombres: Optional[str] = None
    apellidos: Optional[str] = None
    especialidad: Optional[str] = None
    durationCitaMinutos: Optional[int] = None


class EmpleadoMessageDoctorCreate(BaseModel):
    documento: Optional[str] = None
    nombres: Optional[str] = None
    apellidos: Optional[str] = None
    especialidad: Optional[str] = None
    durationCitaMinutos: Optional[int] = None


class EmpleadoMessageDoctorUpdate(BaseModel):
    documento: Optional[str] = None
    nombres: Optional[str] = None
    apellidos: Optional[str] = None
    especialidad: Optional[str] = None
    durationCitaMinutos: Optional[int] = None


class EmpleadoMessageDoctorPut(BaseModel):
    documento: Optional[str] = None
    nombres: Optional[str] = None
    apellidos: Optional[str] = None
    especialidad: Optional[str] = None
    durationCitaMinutos: Optional[int] = None


class EmpleadoMessageDirectorBase(BaseModel):
    nombre: Optional[str] = None
    jsonDoctor: Optional[EmpleadoMessageDoctorBase] = None


class EmpleadoMessageDirectorCreate(BaseModel):
    nombre: Optional[str] = None
    jsonDoctor: Optional[EmpleadoMessageDoctorCreate] = None


class EmpleadoMessageDirectorUpdate(BaseModel):
    nombre: Optional[str] = None
    jsonDoctor: Optional[EmpleadoMessageDoctorUpdate] = None


class EmpleadoMessageDirectorPut(BaseModel):
    nombre: Optional[str] = None
    jsonDoctor: Optional[EmpleadoMessageDoctorPut] = None


class EmpleadoMessageCreate(BaseModel):
    model_config = ConfigDict(extra="ignore")
    cedula: int
    nombre: str
    rol: str
    jsonDirector: Optional[EmpleadoMessageDirectorCreate] = None


class EmpleadoMessageUpdate(BaseModel):
    model_config = ConfigDict(extra="ignore")
    nombre: Optional[str] = None
    rol: Optional[str] = None
    jsonDirector: Optional[EmpleadoMessageDirectorUpdate] = None


class EmpleadoMessagePut(BaseModel):
    model_config = ConfigDict(extra="ignore")
    nombre: str
    rol: str
    jsonDirector: Optional[EmpleadoMessageDirectorPut] = None


class EmpleadoMessageRead(BaseModel):
    model_config = ConfigDict(extra="ignore")
    cedula: int
    nombre: str
    rol: str
    jsonDirector: Optional[EmpleadoMessageDirectorBase] = None
