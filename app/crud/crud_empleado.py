from sqlalchemy.orm import Session
from app.models.empleado import Empleado
from app.schemas.empleado import EmpleadoCreate, EmpleadoUpdate


# Funcion para crear a un empleado
def create_empleado(db: Session, empleado: EmpleadoCreate):
    db_empleado = Empleado(**empleado.model_dump())
    db.add(db_empleado)
    db.commit()
    db.refresh(db_empleado)
    return db_empleado


# Funcion para buscar a empleados
def get_empleados(db: Session):
    return db.query(Empleado).all()


# Funcion para buscar a un empleado
def get_empleado(db: Session, empleado_id: int):
    return db.query(Empleado).filter(Empleado.id == empleado_id).first()


# Funcion para actualizar a un empleado usando Patch
def update_empleado(db: Session, empleado_id: int, empleado: EmpleadoUpdate):
    db_empleado = db.query(Empleado).filter(Empleado.id == empleado_id).first()
    if db_empleado is None:
        return None
    # Solo actualiza los campos que vienen con valor
    for campo, valor in empleado.model_dump(exclude_unset=True).items():
        setattr(db_empleado, campo, valor)
    db.commit()
    db.refresh(db_empleado)
    return db_empleado


# Funcion para eliminar a un empleado
def delete_empleado(db: Session, empleado_id: int):
    db_empleado = db.query(Empleado).filter(Empleado.id == empleado_id).first()
    if db_empleado is None:
        return None
    db.delete(db_empleado)
    db.commit()
    return db_empleado
