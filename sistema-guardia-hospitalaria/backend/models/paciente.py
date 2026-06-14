from sqlalchemy import Column, Integer, String, Date
from sqlalchemy.orm import relationship
from database import Base


class Paciente(Base):
    __tablename__ = "pacientes"

    id = Column(Integer, primary_key=True, index=True)
    dni = Column(String, unique=True, nullable=False, index=True)
    nombre = Column(String, nullable=False)
    apellido = Column(String, nullable=False)
    fecha_nacimiento = Column(Date, nullable=False)
    telefono = Column(String, nullable=True)

    ingresos = relationship("IngresoGuardia", back_populates="paciente")
