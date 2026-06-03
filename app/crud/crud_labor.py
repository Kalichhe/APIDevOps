from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from fastapi import HTTPException
from app.models.labor import Labor
from app.schemas.labor import LaborCreate, LaborUpdate, LaborPut


# Funcion para crear a una labor
def create_labor(db: Session, labor: LaborCreate):
    try:
        db_labor = Labor(**labor.model_dump())
        db.add(db_labor)
        db.commit()
        db.refresh(db_labor)
        return db_labor
    except SQLAlchemyError:
        db.rollback()
        raise HTTPException(
            status_code=500, detail="Error al crear la labor en la base de datos."
        )


# Funcion para buscar a labores
def get_labores(db: Session):
    return db.query(Labor).all()


# Funcion para buscar una labor
def get_labor(db: Session, codigo_labor: str):
    return db.query(Labor).filter(Labor.codigo_labor == codigo_labor).first()


# Funcion de busqueda con filtros, orden y paginacion (v3)
_LABOR_ORDER_COLUMNS = {
    "codigo_labor": Labor.codigo_labor,
    "nombre": Labor.nombre,
    "precio": Labor.precio,
}


def search_labores(
    db: Session,
    *,
    nombre: str | None = None,
    unidad_medida: str | None = None,
    precio_min: float | None = None,
    precio_max: float | None = None,
    order_by: str = "codigo_labor",
    order_dir: str = "asc",
    skip: int = 0,
    limit: int = 50,
):
    query = db.query(Labor)

    if nombre:
        query = query.filter(Labor.nombre.ilike(f"%{nombre}%"))
    if unidad_medida:
        query = query.filter(Labor.unidad_medida == unidad_medida)
    if precio_min is not None:
        query = query.filter(Labor.precio >= precio_min)
    if precio_max is not None:
        query = query.filter(Labor.precio <= precio_max)

    column = _LABOR_ORDER_COLUMNS.get(order_by, Labor.codigo_labor)
    column = column.desc() if order_dir == "desc" else column.asc()

    return query.order_by(column).offset(skip).limit(limit).all()


# Funcion para actualizar una labor usando Patch
def update_labor(db: Session, codigo_labor: str, labor: LaborUpdate):
    db_labor = db.query(Labor).filter(Labor.codigo_labor == codigo_labor).first()
    if db_labor is None:
        return None
    try:
        # Solo actualiza los campos que vienen con valor
        for campo, valor in labor.model_dump(exclude_unset=True).items():
            setattr(db_labor, campo, valor)
        db.commit()
        db.refresh(db_labor)
        return db_labor
    except SQLAlchemyError:
        db.rollback()
        raise HTTPException(
            status_code=500, detail="Error al actualizar la labor en la base de datos."
        )


# Funcion para reemplazar una labor usando Put
def put_labor(db: Session, codigo_labor: str, labor: LaborPut):
    db_labor = db.query(Labor).filter(Labor.codigo_labor == codigo_labor).first()
    if db_labor is None:
        return None
    try:
        for campo, valor in labor.model_dump().items():
            setattr(db_labor, campo, valor)
        db.commit()
        db.refresh(db_labor)
        return db_labor
    except SQLAlchemyError:
        db.rollback()
        raise HTTPException(
            status_code=500,
            detail="Error al reemplazar la labor en la base de datos.",
        )


# Funcion para eliminar una labor
def delete_labor(db: Session, codigo_labor: str):
    db_labor = db.query(Labor).filter(Labor.codigo_labor == codigo_labor).first()
    if db_labor is None:
        return None
    try:
        db.delete(db_labor)
        db.commit()
        return db_labor
    except SQLAlchemyError:
        db.rollback()
        raise HTTPException(
            status_code=500, detail="Error al eliminar la labor de la base de datos."
        )