from datetime import date
from sqlalchemy.exc import IntegrityError
import pytest
from models.paciente import Paciente
from models.medico import Medico
from models.ingreso_guardia import IngresoGuardia, EstadoIngreso, Prioridad


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
        username="drlopez",
        password_hash="hashed",
    )
    db.add(medico)
    db.commit()
    db.refresh(medico)
    assert medico.id is not None
    assert medico.matricula == "MP12345"


def test_matricula_unica(db):
    m1 = Medico(nombre="Ana", apellido="García", matricula="MP99999", username="drgarcia1", password_hash="h1")
    m2 = Medico(nombre="Luis", apellido="Ruiz", matricula="MP99999", username="drruiz1", password_hash="h2")
    db.add(m1)
    db.commit()
    db.add(m2)
    with pytest.raises(IntegrityError):
        db.commit()


def test_medico_especialidad_opcional(db):
    medico = Medico(nombre="Pedro", apellido="Sosa", matricula="MP00001", username="drsosa", password_hash="hashed")
    db.add(medico)
    db.commit()
    db.refresh(medico)
    assert medico.especialidad is None


def test_crear_ingreso_estado_inicial(db):
    paciente = Paciente(dni="77777777", nombre="Sofía", apellido="Vega", fecha_nacimiento=date(1995, 3, 20))
    db.add(paciente)
    db.commit()

    ingreso = IngresoGuardia(paciente_id=paciente.id, prioridad=Prioridad.ALTA)
    db.add(ingreso)
    db.commit()
    db.refresh(ingreso)

    assert ingreso.id is not None
    assert ingreso.estado == EstadoIngreso.EN_ESPERA
    assert ingreso.medico_id is None
    assert ingreso.fecha_ingreso is not None
    assert ingreso.observaciones is None


def test_ingreso_relacion_paciente(db):
    paciente = Paciente(dni="66666666", nombre="Lucía", apellido="Torres", fecha_nacimiento=date(1988, 7, 10))
    db.add(paciente)
    db.commit()

    ingreso = IngresoGuardia(paciente_id=paciente.id, prioridad=Prioridad.MEDIA)
    db.add(ingreso)
    db.commit()
    db.refresh(ingreso)

    assert ingreso.paciente.nombre == "Lucía"


def test_ingreso_con_medico(db):
    paciente = Paciente(dni="55555555", nombre="Martín", apellido="Ríos", fecha_nacimiento=date(1970, 11, 5))
    medico = Medico(nombre="Rosa", apellido="Flores", matricula="MP55555", username="drflores", password_hash="hashed")
    db.add_all([paciente, medico])
    db.commit()

    ingreso = IngresoGuardia(
        paciente_id=paciente.id,
        medico_id=medico.id,
        prioridad=Prioridad.BAJA,
        observaciones="Dolor de cabeza leve",
    )
    db.add(ingreso)
    db.commit()
    db.refresh(ingreso)

    assert ingreso.medico.matricula == "MP55555"
    assert ingreso.observaciones == "Dolor de cabeza leve"
