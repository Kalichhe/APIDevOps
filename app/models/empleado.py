from sqlalchemy import Column, Integer, String, JSON
from app.db.session import Base


class Empleado(Base):
    __tablename__ = "empleados"

    cedula = Column(Integer, primary_key=True, nullable=False)
    nombre = Column(String, nullable=False)
    rol = Column(String, nullable=False)

    # Guardar todo el JSON completo
    data_json = Column(JSON, nullable=True)
