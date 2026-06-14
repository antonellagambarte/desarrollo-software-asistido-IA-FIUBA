from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from dependencies import get_db
from schemas.auth import LoginRequest
from schemas.medico import MedicoResponse
from services import auth as auth_service

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/login", response_model=MedicoResponse)
def login(data: LoginRequest, db: Session = Depends(get_db)):
    try:
        return auth_service.verificar_credenciales(db, data.username, data.password)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Credenciales incorrectas",
        )
