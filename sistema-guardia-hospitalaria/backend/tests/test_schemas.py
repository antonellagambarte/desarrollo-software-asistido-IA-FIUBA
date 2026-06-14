from datetime import date, datetime, timezone
from schemas.paciente import PacienteCreate, PacienteResponse
from schemas.medico import MedicoCreate, MedicoResponse

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


def test_medico_create_campos_requeridos():
    m = MedicoCreate(nombre="Ana", apellido="García", matricula="MP99999", username="drgarcia", password="clave")
    assert m.especialidad is None


def test_medico_create_con_especialidad():
    m = MedicoCreate(nombre="Ana", apellido="García", matricula="MP99999", especialidad="Cardiología", username="drgarcia", password="clave")
    assert m.especialidad == "Cardiología"


def test_medico_response_tiene_id():
    m = MedicoResponse(id=5, nombre="Ana", apellido="García", matricula="MP99999", username="drgarcia")
    assert m.id == 5


def test_medico_response_desde_orm(db):
    from models.medico import Medico
    medico = Medico(nombre="Roberto", apellido="Silva", matricula="MP77777", especialidad="Traumatología", username="drsilva", password_hash="hashed")
    db.add(medico)
    db.commit()
    db.refresh(medico)

    response = MedicoResponse.model_validate(medico)
    assert response.matricula == "MP77777"
    assert response.especialidad == "Traumatología"


from schemas.ingreso_guardia import IngresoGuardiaCreate, IngresoGuardiaResponse
from models.ingreso_guardia import EstadoIngreso, Prioridad


def test_ingreso_create_campos_requeridos():
    i = IngresoGuardiaCreate(paciente_id=1, prioridad=Prioridad.ALTA)
    assert i.prioridad == Prioridad.ALTA
    assert i.paciente_id == 1


def test_ingreso_response_medico_opcional():
    from schemas.paciente import PacienteResponse
    paciente = PacienteResponse(
        id=1, dni="12345678", nombre="Juan", apellido="Pérez",
        fecha_nacimiento=date(1990, 1, 1),
    )
    i = IngresoGuardiaResponse(
        id=1,
        paciente_id=1,
        medico_id=None,
        estado=EstadoIngreso.EN_ESPERA,
        prioridad=Prioridad.ALTA,
        fecha_ingreso=datetime.now(timezone.utc),
        paciente=paciente,
        medico=None,
    )
    assert i.medico is None
    assert i.estado == EstadoIngreso.EN_ESPERA


def test_ingreso_response_desde_orm(db):
    from models.paciente import Paciente
    from models.ingreso_guardia import IngresoGuardia

    paciente = Paciente(dni="33333333", nombre="Clara", apellido="Núñez", fecha_nacimiento=date(1992, 4, 12))
    db.add(paciente)
    db.commit()

    ingreso = IngresoGuardia(paciente_id=paciente.id, prioridad=Prioridad.MEDIA)
    db.add(ingreso)
    db.commit()
    db.refresh(ingreso)

    _ = ingreso.paciente  # forzar carga lazy de la relación
    response = IngresoGuardiaResponse.model_validate(ingreso)
    assert response.estado == EstadoIngreso.EN_ESPERA
    assert response.paciente.dni == "33333333"
    assert response.medico is None
