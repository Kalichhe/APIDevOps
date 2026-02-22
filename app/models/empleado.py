from sqlalchemy import Column, Integer, String
from app.db.session import Base


class Empleado(Base):
    __tablename__ = "empleados"

    cedula = Column(String, primary_key=True, nullable=False)
    nombre = Column(String, nullable=False)
    rol = Column(String, nullable=False)
