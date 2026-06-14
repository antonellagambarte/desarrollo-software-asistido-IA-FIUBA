from typing import List, Optional
from sqlalchemy.orm import Session
from models.paciente import Paciente
from schemas.paciente import PacienteCreate


def crear_paciente(db: Session, data: PacienteCreate) -> Paciente:
    if db.query(Paciente).filter(Paciente.dni == data.dni).first():
        raise ValueError(f"Ya existe un paciente con DNI {data.dni}")
    paciente = Paciente(**data.model_dump())
    db.add(paciente)
    db.commit()
    db.refresh(paciente)
    return paciente


def obtener_pacientes(db: Session) -> List[Paciente]:
    return db.query(Paciente).all()


def obtener_paciente_por_dni(db: Session, dni: str) -> Optional[Paciente]:
    return db.query(Paciente).filter(Paciente.dni == dni).first()
