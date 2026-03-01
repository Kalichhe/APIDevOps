from fastapi import APIRouter, Depends, HTTPException, Response
from sqlalchemy.orm import Session
from app.core.dependencies import get_db
from app.schemas.empleado import (
    EmpleadoCreate,
    EmpleadoPut,
    EmpleadoRead,
    EmpleadoUpdate,
)
from app.crud import crud_empleado
from app.models.registro_labor import RegistroLabor

router = APIRouter()


# Funcion para crear a un Empleado
@router.post("/", response_model=EmpleadoRead, status_code=201)
def crear_empleado(empleado: EmpleadoCreate, db: Session = Depends(get_db)):
    # 1. Buscamos si ya existe un empleado con esa cédula
    db_empleado = crud_empleado.get_empleado(db, empleado.cedula)

    # 2. Si existe, lanzamos una excepción 400 (Bad Request) o 409 (Conflict)
    if db_empleado:
        raise HTTPException(
            status_code=409,
            detail=f"Ya existe un empleado con la cédula {empleado.cedula}",
        )

    # 3. Si no existe, procedemos normalmente
    return crud_empleado.create_empleado(db, empleado)


# Funcion para buscar empleados
@router.get("/", response_model=list[EmpleadoRead])
def listar_empleados(db: Session = Depends(get_db)):
    return crud_empleado.get_empleados(db)


# Funcion para buscar a un empleado
@router.get("/{empleado_cedula}", response_model=EmpleadoRead)
def obtener_empleado(empleado_cedula: int, db: Session = Depends(get_db)):
    empleado = crud_empleado.get_empleado(db, empleado_cedula)
    if not empleado:
        raise HTTPException(
            status_code=404,
            detail=f"Empleado con cédula {empleado_cedula} no encontrado.",
        )
    return empleado


# Funcion para poder modificar a un empleado usando Patch
@router.patch("/{empleado_cedula}", response_model=EmpleadoRead)
def actualizar_empleado(
    empleado_cedula: int, empleado: EmpleadoUpdate, db: Session = Depends(get_db)
):
    # Verificamos primero si existe antes de intentar actualizar
    db_empleado = crud_empleado.get_empleado(db, empleado_cedula)
    if not db_empleado:
        raise HTTPException(
            status_code=404, detail="No se puede actualizar: Empleado no encontrado."
        )

    # Si existe, procedemos al CRUD
    return crud_empleado.update_empleado(db, empleado_cedula, empleado)


# Funcion para poder reemplazar a un empleado usando Put
@router.put("/{empleado_cedula}", response_model=EmpleadoRead)
def reemplazar_empleado(
    empleado_cedula: int, empleado: EmpleadoPut, db: Session = Depends(get_db)
):
    # Verificamos primero si existe antes de intentar reemplazar
    db_empleado = crud_empleado.get_empleado(db, empleado_cedula)
    if not db_empleado:
        raise HTTPException(
            status_code=404, detail="No se puede reemplazar: Empleado no encontrado."
        )

    # Si existe, procedemos al CRUD
    return crud_empleado.put_empleado(db, empleado_cedula, empleado)


# Funcion para poder eliminar a un empleado
@router.delete("/{empleado_cedula}", status_code=204)
def eliminar_empleado(empleado_cedula: int, db: Session = Depends(get_db)):
    # Verificamos existencia
    db_empleado = crud_empleado.get_empleado(db, empleado_cedula)
    if not db_empleado:
        raise HTTPException(
            status_code=404, detail="No se puede eliminar: Empleado no encontrado."
        )

    # Verificamos si tiene registros de labor asociados
    tiene_registros = (
        db.query(RegistroLabor)
        .filter(RegistroLabor.empleado_cedula == empleado_cedula)
        .first()
    )
    if tiene_registros:
        raise HTTPException(
            status_code=409,
            detail="No se puede eliminar: el empleado tiene registros de labor asociados.",
        )

    crud_empleado.delete_empleado(db, empleado_cedula)
    return Response(status_code=204)
