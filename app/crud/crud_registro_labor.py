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

    for campo, valor in datos.model_dump(exclude_unset=True).items():
        setattr(db_registro, campo, valor)

    db.commit()
    db.refresh(db_registro)
    return db_registro


# Funcion para eliminar una registro_labor
def delete_registro_labor(db: Session, registro_id: int):
    db_registro = (
        db.query(RegistroLabor).filter(RegistroLabor.id == registro_id).first()
    )
    db.delete(db_registro)
    db.commit()
