from sqlalchemy import Column, Integer, String, Float
from app.db.session import Base

class Labor(Base):
    __tablename__ = "labores"

    id = Column(Integer, primary_key=True, index=True)
    codigo_labor = Column(Integer, primary_key=True, index=True)
    nombre = Column(String, nullable=False)
    unidad_medida = Column(String, nullable=False)
    precio = Column(Float, nullable=False)
    observacion = Column(String, nullable=True)