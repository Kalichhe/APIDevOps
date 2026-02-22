from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.core.dependencies import get_db
from app.schemas.empleado import EmpleadoCreate, EmpleadoRead, EmpleadoUpdate
from app.crud import crud_empleado

router = APIRouter()


# Funcion para crear a un Empleado
@router.post("/", response_model=EmpleadoRead, status_code=201)
def crear_empleado(empleado: EmpleadoCreate, db: Session = Depends(get_db)):
    return crud_empleado.create_empleado(db, empleado)


# Funcion para buscar empleados
@router.get("/", response_model=list[EmpleadoRead])
def listar_empleados(db: Session = Depends(get_db)):
    return crud_empleado.get_empleados(db)


# Funcion para buscar a un empleado
@router.get("/{empleado_cedula}", response_model=EmpleadoRead)
def obtener_empleado(empleado_cedula: int, db: Session = Depends(get_db)):
    empleado = crud_empleado.get_empleado(db, empleado_cedula)
    if empleado is None:
        raise HTTPException(status_code=404, detail="Empleado no encontrado")
    return empleado


# Funcion para poder modificar a un empleado usando Patch
@router.patch("/{empleado_cedula}", response_model=EmpleadoRead)
def actualizar_empleado(
    empleado_cedula: int, empleado: EmpleadoUpdate, db: Session = Depends(get_db)
):
    db_empleado = crud_empleado.update_empleado(db, empleado_cedula, empleado)
    if db_empleado is None:
        raise HTTPException(status_code=404, detail="Empleado no encontrado")
    return db_empleado


# Funcion para poder eliminar a un empleado
@router.delete("/{empleado_cedula}", status_code=204)
def eliminar_empleado(empleado_cedula: int, db: Session = Depends(get_db)):
    empleado = crud_empleado.delete_empleado(db, empleado_cedula)
    if empleado is None:
        raise HTTPException(status_code=404, detail="Empleado no encontrado")
