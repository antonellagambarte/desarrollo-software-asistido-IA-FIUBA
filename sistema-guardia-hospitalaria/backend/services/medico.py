from typing import List
from sqlalchemy.orm import Session
from models.medico import Medico
from schemas.medico import MedicoCreate
from security import hash_password


def crear_medico(db: Session, data: MedicoCreate) -> Medico:
    if db.query(Medico).filter(Medico.matricula == data.matricula).first():
        raise ValueError(f"Ya existe un médico con matrícula {data.matricula}")
    if db.query(Medico).filter(Medico.username == data.username).first():
        raise ValueError(f"Ya existe un médico con usuario {data.username}")
    medico_data = data.model_dump(exclude={"password"})
    medico_data["password_hash"] = hash_password(data.password)
    medico = Medico(**medico_data)
    db.add(medico)
    db.commit()
    db.refresh(medico)
    return medico


def obtener_medicos(db: Session) -> List[Medico]:
    return db.query(Medico).all()
