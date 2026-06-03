from fastapi import APIRouter, Depends, HTTPException, Query, Response
from sqlalchemy.orm import Session
from app.core.dependencies import get_db
from app.schemas.labor import LaborCreate, LaborRead, LaborUpdate, LaborPut
from app.crud import crud_labor
from app.models.registro_labor import RegistroLabor

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


# Funcion para buscar labores con filtros, orden y paginacion (novedad v3)
@router.get("/", response_model=list[LaborRead])
def listar_labores(
    db: Session = Depends(get_db),
    nombre: str | None = Query(
        default=None, description="Filtra por nombre (coincidencia parcial)."
    ),
    unidad_medida: str | None = Query(
        default=None, description="Filtra por unidad de medida (exacta)."
    ),
    precio_min: float | None = Query(
        default=None, ge=0, description="Precio mínimo (inclusive)."
    ),
    precio_max: float | None = Query(
        default=None, ge=0, description="Precio máximo (inclusive)."
    ),
    order_by: str = Query(
        default="codigo_labor", pattern="^(codigo_labor|nombre|precio)$"
    ),
    order_dir: str = Query(default="asc", pattern="^(asc|desc)$"),
    skip: int = Query(default=0, ge=0),
    limit: int = Query(default=50, ge=1, le=200),
):
    if (
        precio_min is not None
        and precio_max is not None
        and precio_min > precio_max
    ):
        raise HTTPException(
            status_code=400,
            detail="precio_min no puede ser mayor que precio_max.",
        )

    return crud_labor.search_labores(
        db,
        nombre=nombre,
        unidad_medida=unidad_medida,
        precio_min=precio_min,
        precio_max=precio_max,
        order_by=order_by,
        order_dir=order_dir,
        skip=skip,
        limit=limit,
    )


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


# Funcion para poder reemplazar una labor usando Put
@router.put("/{codigo_labor}", response_model=LaborRead)
def reemplazar_labor(codigo_labor: str, labor: LaborPut, db: Session = Depends(get_db)):
    # Primero validamos que la labor exista
    db_labor = crud_labor.get_labor(db, codigo_labor)
    if not db_labor:
        raise HTTPException(
            status_code=404, detail="No se puede reemplazar: Labor no encontrada."
        )

    return crud_labor.put_labor(db, codigo_labor, labor)


@router.delete("/{codigo_labor}", status_code=204)
def eliminar_labor(codigo_labor: str, db: Session = Depends(get_db)):
    # Validamos existencia antes de borrar
    db_labor = crud_labor.get_labor(db, codigo_labor)
    if not db_labor:
        raise HTTPException(
            status_code=404, detail="No se puede eliminar: Labor no encontrada."
        )

    # Verificamos si tiene registros de labor asociados
    tiene_registros = (
        db.query(RegistroLabor)
        .filter(RegistroLabor.codigo_labor == codigo_labor)
        .first()
    )
    if tiene_registros:
        raise HTTPException(
            status_code=409,
            detail="No se puede eliminar: la labor tiene registros asociados.",
        )

    crud_labor.delete_labor(db, codigo_labor)
    return Response(status_code=204)
