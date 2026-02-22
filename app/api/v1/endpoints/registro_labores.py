from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.core.dependencies import get_db
from app.schemas.registro_labor import (
    RegistroLaborCreate,
    RegistroLaborRead,
    RegistroLaborUpdate,
)
from app.crud import crud_registro_labor

router = APIRouter()


# Funcion para crear un registro labor
@router.post("/", response_model=RegistroLaborRead, status_code=201)
def crear_registro_labor(
    registro_labor: RegistroLaborCreate, db: Session = Depends(get_db)
):
    return crud_registro_labor.create_registro_labor(db, registro_labor)


# Funcion para buscar registro labores
@router.get("/", response_model=list[RegistroLaborRead])
def listar_registro_labor(db: Session = Depends(get_db)):
    return crud_registro_labor.get_registro_labores(db)


# Funcion para buscar un registro labor
@router.get("/{codigo_registro_labor}", response_model=RegistroLaborRead)
def obtener_registro_labor(codigo_registro_labor: str, db: Session = Depends(get_db)):
    registro_labor = crud_registro_labor.get_registro_labor(db, codigo_registro_labor)
    if registro_labor is None:
        raise HTTPException(status_code=404, detail="Registro labor no encontrada")
    return registro_labor


# Funcion para poder modificar una registro labor usando Patch
@router.patch("/{codigo_registro_labor}", response_model=RegistroLaborRead)
def actualizar_registro_labor(
    codigo_registro_labor: str,
    registro_labor: RegistroLaborUpdate,
    db: Session = Depends(get_db),
):
    db_registro_labor = crud_registro_labor.update_registro_labor(
        db, codigo_registro_labor, registro_labor
    )
    if db_registro_labor is None:
        raise HTTPException(status_code=404, detail="Registro labor no encontrada")
    return db_registro_labor


# Funcion para poder eliminar un registro labor
@router.delete("/{codigo_registro_labor}", status_code=204)
def eliminar_registro_labor(codigo_registro_labor: str, db: Session = Depends(get_db)):
    registro_labor = crud_registro_labor.delete_registro_labor(
        db, codigo_registro_labor
    )
    if registro_labor is None:
        raise HTTPException(status_code=404, detail="Registro labor no encontrada")
