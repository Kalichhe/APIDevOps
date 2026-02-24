from fastapi import APIRouter, Depends, HTTPException, Response
from sqlalchemy.orm import Session
from app.core.dependencies import get_db
from app.schemas.labor import LaborCreate, LaborRead, LaborUpdate
from app.crud import crud_labor

router = APIRouter()


# Funcion para crear una labor
@router.post("/", response_model=LaborRead, status_code=201)
def crear_labor(labor: LaborCreate, db: Session = Depends(get_db)):
    # Verificamos si el código de labor ya existe
    db_labor = crud_labor.get_labor(db, labor.codigo_labor)
    if db_labor:
        raise HTTPException(
            status_code=409,
            detail=f"La labor con código '{labor.codigo_labor}' ya está registrada.",
        )
    return crud_labor.create_labor(db, labor)


# Funcion para buscar labores
@router.get("/", response_model=list[LaborRead])
def listar_labores(db: Session = Depends(get_db)):
    return crud_labor.get_labores(db)


# Funcion para buscar una labor
@router.get("/{codigo_labor}", response_model=LaborRead)
def obtener_labor(codigo_labor: str, db: Session = Depends(get_db)):
    labor = crud_labor.get_labor(db, codigo_labor)
    if not labor:
        raise HTTPException(
            status_code=404, detail=f"Labor '{codigo_labor}' no encontrada."
        )
    return labor


# Funcion para poder modificar una labor usando Patch
@router.patch("/{codigo_labor}", response_model=LaborRead)
def actualizar_labor(
    codigo_labor: str, labor: LaborUpdate, db: Session = Depends(get_db)
):
    # Primero validamos que la labor exista
    db_labor = crud_labor.get_labor(db, codigo_labor)
    if not db_labor:
        raise HTTPException(
            status_code=404, detail="No se puede actualizar: Labor no encontrada."
        )

    return crud_labor.update_labor(db, codigo_labor, labor)


# Funcion para poder eliminar una labor
@router.delete("/{codigo_labor}", status_code=204)
def eliminar_labor(codigo_labor: str, db: Session = Depends(get_db)):
    # Validamos existencia antes de borrar
    db_labor = crud_labor.get_labor(db, codigo_labor)
    if not db_labor:
        raise HTTPException(
            status_code=404,
            detail="No se puede eliminar: Labor no encontrada."
        )

    crud_labor.delete_labor(db, codigo_labor)
    return Response(status_code=204)
