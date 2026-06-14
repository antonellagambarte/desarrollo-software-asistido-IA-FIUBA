from pydantic import BaseModel, ConfigDict


class MedicoCreate(BaseModel):
    nombre: str
    apellido: str
    matricula: str
    especialidad: str
    username: str
    password: str


class MedicoResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    nombre: str
    apellido: str
    matricula: str
    especialidad: str
    username: str


class MedicoConCargaResponse(MedicoResponse):
    pacientes_en_espera: int
