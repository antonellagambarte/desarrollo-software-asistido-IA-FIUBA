from datetime import datetime, timezone
from enum import Enum
from sqlalchemy import Column, Integer, String, DateTime, Text, ForeignKey, Enum as SAEnum
from sqlalchemy.orm import relationship
from database import Base


class EstadoIngreso(str, Enum):
    EN_ESPERA = "EN_ESPERA"
    EN_ATENCION = "EN_ATENCION"
    ALTA = "ALTA"


class Prioridad(str, Enum):
    BAJA = "BAJA"
    MEDIA = "MEDIA"
    ALTA = "ALTA"


class IngresoGuardia(Base):
    __tablename__ = "ingresos_guardia"

    id = Column(Integer, primary_key=True, index=True)
    paciente_id = Column(Integer, ForeignKey("pacientes.id"), nullable=False)
    medico_id = Column(Integer, ForeignKey("medicos.id"), nullable=True)
    estado = Column(SAEnum(EstadoIngreso), default=EstadoIngreso.EN_ESPERA, nullable=False)
    prioridad = Column(SAEnum(Prioridad), nullable=False)
    fecha_ingreso = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False)
    especialidad_requerida = Column(String, nullable=True)
    observaciones = Column(Text, nullable=True)
    observaciones_medico = Column(Text, nullable=True)

    paciente = relationship("Paciente", back_populates="ingresos")
    medico = relationship("Medico", back_populates="ingresos")
