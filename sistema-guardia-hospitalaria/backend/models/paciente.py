from sqlalchemy import Column, Integer, String, Date
from database import Base


class Paciente(Base):
    __tablename__ = "pacientes"

    id = Column(Integer, primary_key=True, index=True)
    dni = Column(String, unique=True, nullable=False, index=True)
    nombre = Column(String, nullable=False)
    apellido = Column(String, nullable=False)
    fecha_nacimiento = Column(Date, nullable=False)
    telefono = Column(String, nullable=True)

    # ingresos: relación con IngresoGuardia se configura en models/ingreso_guardia.py
    # para evitar dependencia circular en la resolución de mappers
