from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from dependencies import get_db
from schemas.paciente import PacienteCreate, PacienteResponse
from services import paciente as paciente_service

router = APIRouter(prefix="/pacientes", tags=["pacientes"])


@router.post("/", response_model=PacienteResponse, status_code=status.HTTP_201_CREATED)
def crear_paciente(data: PacienteCreate, db: Session = Depends(get_db)):
    try:
        return paciente_service.crear_paciente(db, data)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(e))


@router.get("/", response_model=List[PacienteResponse])
def listar_pacientes(q: Optional[str] = None, db: Session = Depends(get_db)):
    if q is not None:
        return paciente_service.buscar_pacientes(db, q)
    return paciente_service.obtener_pacientes(db)


@router.get("/{dni}", response_model=PacienteResponse)
def obtener_paciente(dni: str, db: Session = Depends(get_db)):
    paciente = paciente_service.obtener_paciente_por_dni(db, dni)
    if paciente is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Paciente con DNI {dni} no encontrado",
        )
    return paciente
