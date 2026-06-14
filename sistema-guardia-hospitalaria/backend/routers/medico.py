from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from dependencies import get_db
from schemas.medico import MedicoCreate, MedicoResponse
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
