from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from dependencies import get_db
from models.ingreso_guardia import EstadoIngreso
from schemas.ingreso_guardia import (
    IngresoGuardiaCreate,
    IngresoGuardiaResponse,
    CambioEstadoRequest,
    AsignacionMedicoRequest,
    ActualizarObservacionesRequest,
    ActualizarObservacionesMedicoRequest,
)
from services import ingreso_guardia as ingreso_service

router = APIRouter(prefix="/ingresos", tags=["ingresos"])


@router.post("/", response_model=IngresoGuardiaResponse, status_code=status.HTTP_201_CREATED)
def crear_ingreso(data: IngresoGuardiaCreate, db: Session = Depends(get_db)):
    try:
        return ingreso_service.crear_ingreso(db, data)
    except LookupError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))


@router.get("/", response_model=List[IngresoGuardiaResponse])
def listar_ingresos(estado: Optional[EstadoIngreso] = None, db: Session = Depends(get_db)):
    return ingreso_service.obtener_ingresos(db, estado)


@router.patch("/{ingreso_id}/estado", response_model=IngresoGuardiaResponse)
def cambiar_estado(ingreso_id: int, data: CambioEstadoRequest, db: Session = Depends(get_db)):
    try:
        return ingreso_service.cambiar_estado(db, ingreso_id, data.estado)
    except LookupError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.patch("/{ingreso_id}/medico", response_model=IngresoGuardiaResponse)
def asignar_medico(ingreso_id: int, data: AsignacionMedicoRequest, db: Session = Depends(get_db)):
    try:
        return ingreso_service.asignar_medico(db, ingreso_id, data.medico_id)
    except LookupError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))


@router.patch("/{ingreso_id}/observaciones", response_model=IngresoGuardiaResponse)
def actualizar_observaciones(ingreso_id: int, data: ActualizarObservacionesRequest, db: Session = Depends(get_db)):
    try:
        return ingreso_service.actualizar_observaciones(db, ingreso_id, data.observaciones)
    except LookupError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.patch("/{ingreso_id}/observaciones-medico", response_model=IngresoGuardiaResponse)
def actualizar_observaciones_medico(ingreso_id: int, data: ActualizarObservacionesMedicoRequest, db: Session = Depends(get_db)):
    try:
        return ingreso_service.actualizar_observaciones_medico(db, ingreso_id, data.observaciones_medico)
    except LookupError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
