from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship
from database import Base


class Medico(Base):
    __tablename__ = "medicos"

    id = Column(Integer, primary_key=True, index=True)
    nombre = Column(String, nullable=False)
    apellido = Column(String, nullable=False)
    matricula = Column(String, unique=True, nullable=False)
    especialidad = Column(String, nullable=False)
    username = Column(String, unique=True, nullable=False)
    password_hash = Column(String, nullable=False)

    ingresos = relationship("IngresoGuardia", back_populates="medico")
