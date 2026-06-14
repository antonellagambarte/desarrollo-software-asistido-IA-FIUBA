from datetime import date
from typing import Optional
from pydantic import BaseModel, ConfigDict, computed_field


class PacienteCreate(BaseModel):
    dni: str
    nombre: str
    apellido: str
    fecha_nacimiento: date
    telefono: Optional[str] = None


class PacienteResponse(PacienteCreate):
    model_config = ConfigDict(from_attributes=True)

    id: int

    @computed_field
    @property
    def edad(self) -> int:
        today = date.today()
        born = self.fecha_nacimiento
        return today.year - born.year - ((today.month, today.day) < (born.month, born.day))
