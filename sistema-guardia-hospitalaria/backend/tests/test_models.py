from datetime import date
from sqlalchemy.exc import IntegrityError
import pytest
from models.paciente import Paciente
from models.medico import Medico


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


def test_crear_medico(db):
    medico = Medico(
        nombre="María",
        apellido="López",
        matricula="MP12345",
        especialidad="Clínica Médica",
    )
    db.add(medico)
    db.commit()
    db.refresh(medico)
    assert medico.id is not None
    assert medico.matricula == "MP12345"


def test_matricula_unica(db):
    m1 = Medico(nombre="Ana", apellido="García", matricula="MP99999")
    m2 = Medico(nombre="Luis", apellido="Ruiz", matricula="MP99999")
    db.add(m1)
    db.commit()
    db.add(m2)
    with pytest.raises(IntegrityError):
        db.commit()


def test_medico_especialidad_opcional(db):
    medico = Medico(nombre="Pedro", apellido="Sosa", matricula="MP00001")
    db.add(medico)
    db.commit()
    db.refresh(medico)
    assert medico.especialidad is None
