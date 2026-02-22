from sqlalchemy.orm import Session
from app.models.registro_labor import RegistroLabor
from app.schemas.registro_labor import RegistroLaborCreate, RegistroLaborUpdate


# Funcion para crear a una registro_labor
def create_registro_labor(db: Session, registro_labor: RegistroLaborCreate):
    db_registro_labor = RegistroLabor(**registro_labor.model_dump())
    db.add(db_registro_labor)
    db.commit()
    db.refresh(db_registro_labor)
    return db_registro_labor


# Funcion para buscar los registro de labores
def get_registro_labores(db: Session):
    return db.query(RegistroLabor).all()


# Funcion para buscar una registro_labor
def get_registro_labor(db: Session, codigo_registro_labor: str):
    return db.query(RegistroLabor).filter(RegistroLabor.codigocodigo_registro_labor ==codigo_registro_labor).first()


# Funcion para actualizar una registro_labor usando Patch
def update_registro_labor(db: Session,codigo_registro_labor: str, registro_labor: RegistroLaborUpdate):
    db_registro_labor = db.query(RegistroLabor).filter(RegistroLabor.codigo_registro_labor ==codigo_registro_labor).first()
    if db_registro_labor is None:
        return None
    # Solo actualiza los campos que vienen con valor
    for campo, valor in registro_labor.model_dump(exclude_unset=True).items():
        setattr(db_registro_labor, campo, valor)
    db.commit()
    db.refresh(db_registro_labor)
    return db_registro_labor


# Funcion para eliminar una registro_labor
def delete_registro_labor(db: Session,codigo_registro_labor: str):
    db_registro_labor = db.query(RegistroLabor).filter(RegistroLabor.codigo_registro_labor ==codigo_registro_labor).first()
    if db_registro_labor is None:
        return None
    db.delete(db_registro_labor)
    db.commit()
    return db_registro_labor