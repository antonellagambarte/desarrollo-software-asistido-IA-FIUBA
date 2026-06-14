from typing import List
from sqlalchemy import func
from sqlalchemy.orm import Session
from models.medico import Medico
from models.ingreso_guardia import IngresoGuardia, EstadoIngreso
from schemas.medico import MedicoCreate, MedicoConCargaResponse
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


def obtener_medicos_con_carga(
    db: Session, estado: EstadoIngreso = EstadoIngreso.EN_ESPERA
) -> List[MedicoConCargaResponse]:
    medicos = db.query(Medico).all()
    result = []
    for m in medicos:
        count = (
            db.query(func.count(IngresoGuardia.id))
            .filter(
                IngresoGuardia.medico_id == m.id,
                IngresoGuardia.estado == estado,
            )
            .scalar()
            or 0
        )
        result.append(
            MedicoConCargaResponse(
                id=m.id,
                nombre=m.nombre,
                apellido=m.apellido,
                matricula=m.matricula,
                especialidad=m.especialidad,
                username=m.username,
                pacientes_en_espera=count,
            )
        )
    return result
