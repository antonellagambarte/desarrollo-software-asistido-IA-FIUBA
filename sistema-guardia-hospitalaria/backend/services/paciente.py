from typing import List, Optional
from sqlalchemy import or_
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


def obtener_ultimos_pacientes(db: Session, limit: int) -> List[Paciente]:
    return db.query(Paciente).order_by(Paciente.id.desc()).limit(limit).all()


def obtener_paciente_por_dni(db: Session, dni: str) -> Optional[Paciente]:
    return db.query(Paciente).filter(Paciente.dni == dni).first()


def buscar_pacientes(db: Session, q: str) -> List[Paciente]:
    if not q or not q.strip():
        return []
    term = f"%{q.strip()}%"
    return (
        db.query(Paciente)
        .filter(
            or_(
                Paciente.dni.ilike(term),
                Paciente.nombre.ilike(term),
                Paciente.apellido.ilike(term),
            )
        )
        .order_by(Paciente.apellido, Paciente.nombre)
        .all()
    )
