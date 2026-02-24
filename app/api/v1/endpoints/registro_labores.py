from fastapi import APIRouter, Depends, HTTPException, Response
from sqlalchemy.orm import Session
from app.core.dependencies import get_db
from app.schemas.registro_labor import (
    RegistroLaborCreate,
    RegistroLaborRead,
    RegistroLaborUpdate,
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


# Funcion para buscar registro labores
@router.get("/", response_model=list[RegistroLaborRead])
def listar_registro_labor(db: Session = Depends(get_db)):
    return crud_registro_labor.get_registro_labores(db)


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


# Funcion para poder modificar una registro labor usando Patch
# @router.patch("/{codigo_registro_labor}", response_model=RegistroLaborRead)
# def actualizar_registro_labor(
#     codigo_registro_labor: str,
#     registro_labor: RegistroLaborUpdate,
#     db: Session = Depends(get_db),
# ):
#     # Verificar existencia del registro principal
#     db_registro = crud_registro_labor.get_registro_labor(db, codigo_registro_labor)
#     if not db_registro:
#         raise HTTPException(
#             status_code=404, detail="Registro no encontrado para actualizar."
#         )

#     # Opcional: Si el PATCH permite cambiar la cédula o labor, deberías validar que existan también.

#     return crud_registro_labor.update_registro_labor(
#         db, codigo_registro_labor, registro_labor
#     )
# Pensar despues en como implementar eso

# Funcion para poder eliminar un registro labor
# @router.delete("/{codigo_registro_labor}", status_code=204)
# def eliminar_registro_labor(codigo_registro_labor: str, db: Session = Depends(get_db)):
#     db_registro = crud_registro_labor.get_registro_labor(db, codigo_registro_labor)
#     if not db_registro:
#         raise HTTPException(
#             status_code=404, detail="No se puede eliminar: Registro no encontrado."
#         )

#     crud_registro_labor.delete_registro_labor(db, codigo_registro_labor)
#     return Response(status_code=204)
# Pensar despues en como implementar eso
