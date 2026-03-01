from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from fastapi import HTTPException
from app.models.empleado import Empleado
from app.schemas.empleado import EmpleadoCreate, EmpleadoUpdate, EmpleadoPut


# Funcion para crear a un empleado
def create_empleado(db: Session, empleado: EmpleadoCreate):
    try:
        db_empleado = Empleado(**empleado.model_dump())
        db.add(db_empleado)
        db.commit()
        db.refresh(db_empleado)
        return db_empleado
    except SQLAlchemyError:
        db.rollback()
        raise HTTPException(
            status_code=500, detail="Error al crear el empleado en la base de datos."
        )


# Funcion para buscar a empleados
def get_empleados(db: Session):
    return db.query(Empleado).all()


# Funcion para buscar a un empleado
def get_empleado(db: Session, empleado_cedula: int):
    return db.query(Empleado).filter(Empleado.cedula == empleado_cedula).first()


# Funcion para actualizar a un empleado usando Patch
def update_empleado(db: Session, empleado_cedula: int, empleado: EmpleadoUpdate):
    db_empleado = db.query(Empleado).filter(Empleado.cedula == empleado_cedula).first()
    if db_empleado is None:
        return None
    try:
        # Solo actualiza los campos que vienen con valor
        for campo, valor in empleado.model_dump(exclude_unset=True).items():
            setattr(db_empleado, campo, valor)
        db.commit()
        db.refresh(db_empleado)
        return db_empleado
    except SQLAlchemyError:
        db.rollback()
        raise HTTPException(
            status_code=500,
            detail="Error al actualizar el empleado en la base de datos.",
        )


# Funcion para reemplazar a un empleado usando Put
def put_empleado(db: Session, empleado_cedula: int, empleado: EmpleadoPut):
    db_empleado = db.query(Empleado).filter(Empleado.cedula == empleado_cedula).first()
    if db_empleado is None:
        return None
    try:
        for campo, valor in empleado.model_dump().items():
            setattr(db_empleado, campo, valor)
        db.commit()
        db.refresh(db_empleado)
        return db_empleado
    except SQLAlchemyError:
        db.rollback()
        raise HTTPException(
            status_code=500,
            detail="Error al reemplazar el empleado en la base de datos.",
        )


# Funcion para eliminar a un empleado
def delete_empleado(db: Session, empleado_cedula: int):
    db_empleado = db.query(Empleado).filter(Empleado.cedula == empleado_cedula).first()
    if db_empleado is None:
        return None
    try:
        db.delete(db_empleado)
        db.commit()
        return db_empleado
    except SQLAlchemyError:
        db.rollback()
        raise HTTPException(
            status_code=500, detail="Error al eliminar el empleado de la base de datos."
        )
