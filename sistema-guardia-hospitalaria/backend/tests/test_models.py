from datetime import date
from sqlalchemy.exc import IntegrityError
import pytest
from models.paciente import Paciente


def test_crear_paciente(db):
    paciente = Paciente(
        dni="12345678",
        nombre="Juan",
        apellido="Pérez",
        fecha_nacimiento=date(1990, 5, 15),
        telefono="1134567890",
    )
    db.add(paciente)
    db.commit()
    db.refresh(paciente)
    assert paciente.id is not None
    assert paciente.dni == "12345678"
    assert paciente.telefono == "1134567890"


def test_dni_unico(db):
    p1 = Paciente(dni="11111111", nombre="Ana", apellido="Garcia", fecha_nacimiento=date(1985, 1, 1))
    p2 = Paciente(dni="11111111", nombre="Luis", apellido="Lopez", fecha_nacimiento=date(1990, 2, 2))
    db.add(p1)
    db.commit()
    db.add(p2)
    with pytest.raises(IntegrityError):
        db.commit()


def test_paciente_telefono_opcional(db):
    paciente = Paciente(
        dni="99990000",
        nombre="Carlos",
        apellido="Díaz",
        fecha_nacimiento=date(2000, 1, 1),
    )
    db.add(paciente)
    db.commit()
    db.refresh(paciente)
    assert paciente.telefono is None
