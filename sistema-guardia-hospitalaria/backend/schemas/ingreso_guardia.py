from datetime import datetime
from typing import Optional
from pydantic import BaseModel, ConfigDict
from models.ingreso_guardia import EstadoIngreso, Prioridad
from schemas.paciente import PacienteResponse
from schemas.medico import MedicoResponse


class IngresoGuardiaCreate(BaseModel):
    paciente_id: int
    prioridad: Prioridad


class IngresoGuardiaResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    paciente_id: int
    medico_id: Optional[int] = None
    estado: EstadoIngreso
    prioridad: Prioridad
    fecha_ingreso: datetime
    observaciones: Optional[str] = None
    paciente: PacienteResponse
    medico: Optional[MedicoResponse] = None
