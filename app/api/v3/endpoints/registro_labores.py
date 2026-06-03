from fastapi import APIRouter, Depends, HTTPException, Response
from sqlalchemy.orm import Session
from app.core.dependencies import get_db
from app.schemas.registro_labor import (
    RegistroLaborCreate,
    RegistroLaborRead,
    RegistroLaborUpdate,
    RegistroLaborPut,
)
from app.crud import (
    crud_registro_labor,
    crud_empleado,
    crud_labor,
)

router = APIRouter()


# Funcion para crear un registro labor
@router.post("/", response_model=RegistroLaborRead, status_code=201)
def crear_registro_labor(
    registro_labor: RegistroLaborCreate, db: Session = Depends(get_db)
):
    # A. Validar que el Empleado exista
    if not crud_empleado.get_empleado(db, registro_labor.empleado_cedula):
        raise HTTPException(
            status_code=404, detail="El empleado especificado no existe."
        )

    # B. Validar que la Labor exista
    if not crud_labor.get_labor(db, registro_labor.codigo_labor):
        raise HTTPException(status_code=404, detail="La labor especificada no existe.")

    return crud_registro_labor.create_registro_labor(db, registro_labor)


@router.get("/", response_model=list[RegistroLaborRead])
def listar_registro_labor(db: Session = Depends(get_db)):
    return crud_registro_labor.get_all_registros_labor(db)


# Funcion para buscar un registro labor
@router.get("/empleado/{empleado_cedula}", response_model=list[RegistroLaborRead])
def obtener_registros_por_empleado(empleado_cedula: int, db: Session = Depends(get_db)):
    # Buscamos todos los registros asociados a esa cédula
    registros = crud_registro_labor.get_registros_by_empleado(db, empleado_cedula)

    # Si la lista está vacía, puede ser que el empleado no tenga registros o no exista
    if not registros:
        raise HTTPException(
            status_code=404,
            detail=f"No se encontraron registros para el empleado con cédula {empleado_cedula}.",
        )
    return registros


# Función para modificar un registro labor usando PATCH
@router.patch("/{registro_id}", response_model=RegistroLaborRead)
def actualizar_registro_labor(
    registro_id: int,
    registro_labor: RegistroLaborUpdate,
    db: Session = Depends(get_db),
):
    # Verificar que el registro existe
    db_registro = crud_registro_labor.get_registro_labor(db, registro_id)
    if not db_registro:
        raise HTTPException(
            status_code=404, detail="Registro no encontrado para actualizar."
        )

    # Si se está cambiando el empleado, verificar que existe
    if registro_labor.empleado_cedula is not None:
        db_empleado = crud_empleado.get_empleado(db, registro_labor.empleado_cedula)
        if not db_empleado:
            raise HTTPException(
                status_code=404,
                detail="No se puede actualizar: Empleado no encontrado.",
            )

    # Si se está cambiando la labor, verificar que existe
    if registro_labor.codigo_labor is not None:
        db_labor = crud_labor.get_labor(db, registro_labor.codigo_labor)
        if not db_labor:
            raise HTTPException(
                status_code=404, detail="No se puede actualizar: Labor no encontrada."
            )

    return crud_registro_labor.update_registro_labor(db, registro_id, registro_labor)


# Función para reemplazar un registro labor usando PUT
@router.put("/{registro_id}", response_model=RegistroLaborRead)
def reemplazar_registro_labor(
    registro_id: int,
    registro_labor: RegistroLaborPut,
    db: Session = Depends(get_db),
):
    # Verificar que el registro existe
    db_registro = crud_registro_labor.get_registro_labor(db, registro_id)
    if not db_registro:
        raise HTTPException(
            status_code=404, detail="Registro no encontrado para reemplazar."
        )

    # Verificar que el empleado existe
    db_empleado = crud_empleado.get_empleado(db, registro_labor.empleado_cedula)
    if not db_empleado:
        raise HTTPException(
            status_code=404,
            detail="No se puede reemplazar: Empleado no encontrado.",
        )

    # Verificar que la labor existe
    db_labor = crud_labor.get_labor(db, registro_labor.codigo_labor)
    if not db_labor:
        raise HTTPException(
            status_code=404, detail="No se puede reemplazar: Labor no encontrada."
        )

    return crud_registro_labor.put_registro_labor(db, registro_id, registro_labor)


# Función para eliminar un registro labor
@router.delete("/{registro_id}", status_code=204)
def eliminar_registro_labor(registro_id: int, db: Session = Depends(get_db)):
    # Verificar que el registro existe antes de eliminar
    db_registro = crud_registro_labor.get_registro_labor(db, registro_id)
    if not db_registro:
        raise HTTPException(
            status_code=404, detail="No se puede eliminar: Registro no encontrado."
        )

    crud_registro_labor.delete_registro_labor(db, registro_id)
    return Response(status_code=204)
