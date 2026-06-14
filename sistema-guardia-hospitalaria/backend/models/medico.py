from sqlalchemy import Column, Integer, String
from database import Base


class Medico(Base):
    __tablename__ = "medicos"

    id = Column(Integer, primary_key=True, index=True)
    nombre = Column(String, nullable=False)
    apellido = Column(String, nullable=False)
    matricula = Column(String, unique=True, nullable=False)
    especialidad = Column(String, nullable=True)

    # ingresos: relación con IngresoGuardia se agrega en Task 4
    # para evitar dependencia circular en la resolución de mappers
