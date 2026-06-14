from datetime import date, datetime
from schemas.paciente import PacienteCreate, PacienteResponse

# Importar todos los modelos al nivel de módulo para que SQLAlchemy registre
# todas las clases antes de que conftest.py ejecute Base.metadata.create_all()
from models.paciente import Paciente  # noqa: F401
import models.ingreso_guardia  # noqa: F401
import models.medico  # noqa: F401


def test_paciente_create_campos_requeridos():
    p = PacienteCreate(
        dni="12345678",
        nombre="Juan",
        apellido="Pérez",
        fecha_nacimiento=date(1990, 5, 15),
    )
    assert p.dni == "12345678"
    assert p.telefono is None


def test_paciente_create_con_telefono():
    p = PacienteCreate(
        dni="12345678",
        nombre="Juan",
        apellido="Pérez",
        fecha_nacimiento=date(1990, 5, 15),
        telefono="1134567890",
    )
    assert p.telefono == "1134567890"


def test_paciente_response_calcula_edad():
    today = date.today()
    fecha_nacimiento = date(today.year - 30, today.month, today.day)
    p = PacienteResponse(
        id=1,
        dni="12345678",
        nombre="Juan",
        apellido="Pérez",
        fecha_nacimiento=fecha_nacimiento,
    )
    assert p.edad == 30


def test_paciente_response_desde_orm(db):
    paciente = Paciente(
        dni="44444444",
        nombre="Elena",
        apellido="Mora",
        fecha_nacimiento=date(1985, 6, 1),
    )
    db.add(paciente)
    db.commit()
    db.refresh(paciente)

    response = PacienteResponse.model_validate(paciente)
    assert response.id == paciente.id
    assert response.edad >= 0
