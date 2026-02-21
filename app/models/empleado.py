from sqlalchemy import Column, Integer, String
from app.db.session import Base

class Empleado(Base):
  __tablename__ = "empleados"

  id = Column(Integer, primary_key=True, index=True)
  cedula = Column(String, unique=True, nullable=False)
  nombre = Column(String, nullable=False)
  rol = Column(String, nullable=False)
