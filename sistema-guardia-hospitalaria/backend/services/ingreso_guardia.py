from typing import List, Optional
from sqlalchemy.orm import Session
from models.ingreso_guardia import IngresoGuardia, EstadoIngreso
from models.paciente import Paciente
from models.medico import Medico
from schemas.ingreso_guardia import IngresoGuardiaCreate

TRANSICIONES_VALIDAS = {
    EstadoIngreso.EN_ESPERA: EstadoIngreso.EN_ATENCION,
    EstadoIngreso.EN_ATENCION: EstadoIngreso.ALTA,
}


def obtener_ingreso_activo_por_paciente(db: Session, paciente_id: int) -> Optional[IngresoGuardia]:
    return (
        db.query(IngresoGuardia)
        .filter(
            IngresoGuardia.paciente_id == paciente_id,
            IngresoGuardia.estado != EstadoIngreso.ALTA,
        )
        .first()
    )


def crear_ingreso(db: Session, data: IngresoGuardiaCreate) -> IngresoGuardia:
    if not db.get(Paciente, data.paciente_id):
        raise LookupError(f"Paciente con id {data.paciente_id} no encontrado")
    if obtener_ingreso_activo_por_paciente(db, data.paciente_id):
        raise ValueError("El paciente ya tiene un ingreso activo en guardia")
    ingreso = IngresoGuardia(
        paciente_id=data.paciente_id,
        prioridad=data.prioridad,
        especialidad_requerida=data.especialidad_requerida,
        observaciones=data.observaciones,
        estado=EstadoIngreso.EN_ESPERA,
    )
    db.add(ingreso)
    db.commit()
    db.refresh(ingreso)
    return ingreso


def obtener_ingresos(db: Session, estado: Optional[EstadoIngreso] = None) -> List[IngresoGuardia]:
    query = db.query(IngresoGuardia)
    if estado is not None:
        query = query.filter(IngresoGuardia.estado == estado)
    return query.all()


def cambiar_estado(db: Session, ingreso_id: int, nuevo_estado: EstadoIngreso) -> IngresoGuardia:
    ingreso = db.get(IngresoGuardia, ingreso_id)
    if ingreso is None:
        raise LookupError(f"Ingreso con id {ingreso_id} no encontrado")
    if ingreso.estado == EstadoIngreso.ALTA:
        raise ValueError("El ingreso con estado ALTA no puede modificarse")
    if TRANSICIONES_VALIDAS.get(ingreso.estado) != nuevo_estado:
        raise ValueError(f"Transición inválida: {ingreso.estado} → {nuevo_estado}")
    ingreso.estado = nuevo_estado
    db.commit()
    db.refresh(ingreso)
    return ingreso


def asignar_medico(db: Session, ingreso_id: int, medico_id: int) -> IngresoGuardia:
    ingreso = db.get(IngresoGuardia, ingreso_id)
    if ingreso is None:
        raise LookupError(f"Ingreso con id {ingreso_id} no encontrado")
    if not db.get(Medico, medico_id):
        raise LookupError(f"Médico con id {medico_id} no encontrado")
    ingreso.medico_id = medico_id
    db.commit()
    db.refresh(ingreso)
    return ingreso


def actualizar_prioridad(db: Session, ingreso_id: int, prioridad) -> IngresoGuardia:
    ingreso = db.get(IngresoGuardia, ingreso_id)
    if ingreso is None:
        raise LookupError(f"Ingreso con id {ingreso_id} no encontrado")
    if ingreso.estado == EstadoIngreso.ALTA:
        raise ValueError("El ingreso con estado ALTA no puede modificarse")
    ingreso.prioridad = prioridad
    db.commit()
    db.refresh(ingreso)
    return ingreso


def actualizar_especialidad(db: Session, ingreso_id: int, especialidad_requerida: str) -> IngresoGuardia:
    ingreso = db.get(IngresoGuardia, ingreso_id)
    if ingreso is None:
        raise LookupError(f"Ingreso con id {ingreso_id} no encontrado")
    if ingreso.estado == EstadoIngreso.ALTA:
        raise ValueError("El ingreso con estado ALTA no puede modificarse")
    ingreso.especialidad_requerida = especialidad_requerida
    db.commit()
    db.refresh(ingreso)
    return ingreso


def actualizar_observaciones(db: Session, ingreso_id: int, observaciones: Optional[str]) -> IngresoGuardia:
    ingreso = db.get(IngresoGuardia, ingreso_id)
    if ingreso is None:
        raise LookupError(f"Ingreso con id {ingreso_id} no encontrado")
    if ingreso.estado == EstadoIngreso.ALTA:
        raise ValueError("El ingreso con estado ALTA no puede modificarse")
    ingreso.observaciones = observaciones
    db.commit()
    db.refresh(ingreso)
    return ingreso


def actualizar_observaciones_medico(db: Session, ingreso_id: int, observaciones_medico: Optional[str]) -> IngresoGuardia:
    ingreso = db.get(IngresoGuardia, ingreso_id)
    if ingreso is None:
        raise LookupError(f"Ingreso con id {ingreso_id} no encontrado")
    if ingreso.estado == EstadoIngreso.ALTA:
        raise ValueError("El ingreso con estado ALTA no puede modificarse")
    ingreso.observaciones_medico = observaciones_medico
    db.commit()
    db.refresh(ingreso)
    return ingreso
