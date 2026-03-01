from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from fastapi import HTTPException
from app.models.registro_labor import RegistroLabor
from app.schemas.registro_labor import RegistroLaborCreate, RegistroLaborPut, RegistroLaborUpdate


# Funcion para crear a una registro_labor
def create_registro_labor(db: Session, registro_labor: RegistroLaborCreate):
    try:
        db_registro_labor = RegistroLabor(**registro_labor.model_dump())
        db.add(db_registro_labor)
        db.commit()
        db.refresh(db_registro_labor)
        return db_registro_labor
    except SQLAlchemyError:
        db.rollback()
        raise HTTPException(
            status_code=500,
            detail="Error al crear el registro de labor en la base de datos.",
        )


def get_registro_labor(db: Session, registro_id: int):
    return db.query(RegistroLabor).filter(RegistroLabor.id == registro_id).first()


def get_all_registros_labor(db: Session):
    return db.query(RegistroLabor).all()


# Funcion para buscar una registro_labor
def get_registros_by_empleado(db: Session, cedula: int):
    # Usamos .all() porque esperamos una lista de registros, no solo uno
    return db.query(RegistroLabor).filter(RegistroLabor.empleado_cedula == cedula).all()


# Funcion para actualizar una registro_labor usando Patch
def update_registro_labor(db: Session, registro_id: int, datos: RegistroLaborUpdate):
    db_registro = (
        db.query(RegistroLabor).filter(RegistroLabor.id == registro_id).first()
    )
    if db_registro is None:
        return None
    try:
        for campo, valor in datos.model_dump(exclude_unset=True).items():
            setattr(db_registro, campo, valor)

        db.commit()
        db.refresh(db_registro)
        return db_registro
    except SQLAlchemyError:
        db.rollback()
        raise HTTPException(
            status_code=500,
            detail="Error al actualizar el registro de labor en la base de datos.",
        )


# Funcion para reemplazar un registro_labor usando Put
def put_registro_labor(db: Session, registro_id: int, datos: RegistroLaborPut):
    db_registro = (
        db.query(RegistroLabor).filter(RegistroLabor.id == registro_id).first()
    )
    if db_registro is None:
        return None
    try:
        for campo, valor in datos.model_dump().items():
            setattr(db_registro, campo, valor)
        db.commit()
        db.refresh(db_registro)
        return db_registro
    except SQLAlchemyError:
        db.rollback()
        raise HTTPException(
            status_code=500,
            detail="Error al reemplazar el registro de labor en la base de datos.",
        )


# Funcion para eliminar una registro_labor
def delete_registro_labor(db: Session, registro_id: int):
    db_registro = (
        db.query(RegistroLabor).filter(RegistroLabor.id == registro_id).first()
    )
    if db_registro is None:
        return None
    try:
        db.delete(db_registro)
        db.commit()
    except SQLAlchemyError:
        db.rollback()
        raise HTTPException(
            status_code=500,
            detail="Error al eliminar el registro de labor de la base de datos.",
        )
