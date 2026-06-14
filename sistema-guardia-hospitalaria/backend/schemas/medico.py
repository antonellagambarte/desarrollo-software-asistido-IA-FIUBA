from typing import Optional
from pydantic import BaseModel, ConfigDict


class MedicoCreate(BaseModel):
    nombre: str
    apellido: str
    matricula: str
    especialidad: Optional[str] = None


class MedicoResponse(MedicoCreate):
    model_config = ConfigDict(from_attributes=True)

    id: int
