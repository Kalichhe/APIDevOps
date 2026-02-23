from sqlalchemy import Column, Integer, Float, String, Date, ForeignKey
from sqlalchemy.orm import relationship
from app.db.session import Base


class RegistroLabor(Base):
    __tablename__ = "registro_labores"

    id = Column(Integer, primary_key=True, index=True)
    empleado_cedula = Column(Integer, ForeignKey("empleados.cedula"), nullable=False)
    codigo_labor = Column(String, ForeignKey("labores.codigo_labor"), nullable=False)
    fecha = Column(Date, nullable=False)
    cantidad = Column(Float, nullable=False)
    observacion = Column(String, nullable=True)

    empleado = relationship("Empleado")
    labor = relationship("Labor")
