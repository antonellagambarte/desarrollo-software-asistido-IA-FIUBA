from typing import List, Optional
from sqlalchemy.orm import Session
from models.medico import Medico
from schemas.medico import MedicoCreate


def crear_medico(db: Session, data: MedicoCreate) -> Medico:
    if db.query(Medico).filter(Medico.matricula == data.matricula).first():
        raise ValueError(f"Ya existe un médico con matrícula {data.matricula}")
    medico = Medico(**data.model_dump())
    db.add(medico)
    db.commit()
    db.refresh(medico)
    return medico


def obtener_medicos(db: Session) -> List[Medico]:
    return db.query(Medico).all()
