from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from dependencies import get_db
from models.ingreso_guardia import EstadoIngreso
from schemas.medico import MedicoCreate, MedicoResponse, MedicoConCargaResponse
from services import medico as medico_service

router = APIRouter(prefix="/medicos", tags=["medicos"])


@router.post("/", response_model=MedicoResponse, status_code=status.HTTP_201_CREATED)
def crear_medico(data: MedicoCreate, db: Session = Depends(get_db)):
    try:
        return medico_service.crear_medico(db, data)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(e))


@router.get("/", response_model=List[MedicoResponse])
def listar_medicos(db: Session = Depends(get_db)):
    return medico_service.obtener_medicos(db)


@router.get("/con-carga", response_model=List[MedicoConCargaResponse])
def listar_medicos_con_carga(
    estado: EstadoIngreso = EstadoIngreso.EN_ESPERA,
    db: Session = Depends(get_db),
):
    return medico_service.obtener_medicos_con_carga(db, estado)
