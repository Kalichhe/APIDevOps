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