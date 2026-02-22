from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.core.dependencies import get_db
from app.schemas.labor import LaborCreate, LaborRead, LaborUpdate
from app.crud import crud_labor

router = APIRouter()


# Funcion para crear una labor
@router.post("/", response_model=LaborRead, status_code=201)
def crear_labor(labor: LaborCreate, db: Session = Depends(get_db)):
    return crud_labor.create_labor(db, labor)


# Funcion para buscar labores
@router.get("/", response_model=list[LaborRead])
def listar_labores(db: Session = Depends(get_db)):
    return crud_labor.get_labores(db)


# Funcion para buscar una labor
@router.get("/{codigo_labor}", response_model=LaborRead)
def obtener_labor(codigo_labor: str, db: Session = Depends(get_db)):
    labor = crud_labor.get_labor(db, codigo_labor)
    if labor is None:
        raise HTTPException(status_code=404, detail="Labor no encontrada")
    return labor


# Funcion para poder modificar una labor usando Patch
@router.patch("/{codigo_labor}", response_model=LaborRead)
def actualizar_labor(
    codigo_labor: str, labor: LaborUpdate, db: Session = Depends(get_db)
):
    db_labor = crud_labor.update_labor(db, codigo_labor, labor)
    if db_labor is None:
        raise HTTPException(status_code=404, detail="Labor no encontrada")
    return db_labor


# Funcion para poder eliminar una labor
@router.delete("/{codigo_labor}", status_code=204)
def eliminar_labor(codigo_labor: str, db: Session = Depends(get_db)):
    labor = crud_labor.delete_labor(db, codigo_labor)
    if labor is None:
        raise HTTPException(status_code=404, detail="Labor na encontrada")
