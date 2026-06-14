from sqlalchemy.orm import Session
from models.medico import Medico
from security import verify_password


def verificar_credenciales(db: Session, username: str, password: str) -> Medico:
    medico = db.query(Medico).filter(Medico.username == username).first()
    if medico is None or not verify_password(password, medico.password_hash):
        raise ValueError("Credenciales incorrectas")
    return medico
