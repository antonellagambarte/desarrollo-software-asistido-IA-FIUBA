# Modelos SQLAlchemy y Schemas Pydantic — Plan de Implementación

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Crear los modelos SQLAlchemy y schemas Pydantic para `Paciente`, `Médico` e `IngresoGuardia`, con tests que verifican su correcto funcionamiento.

**Architecture:** Un archivo por entidad en `models/` y `schemas/`. `database.py` centraliza la configuración de SQLAlchemy. Los enums `EstadoIngreso` y `Prioridad` viven en `models/ingreso_guardia.py`.

**Tech Stack:** FastAPI, SQLAlchemy 2.x, Pydantic v2, SQLite, pytest

---

## Estructura de archivos

```
backend/
├── database.py                     ← Base, engine, SessionLocal
├── models/
│   ├── __init__.py
│   ├── paciente.py
│   ├── medico.py
│   └── ingreso_guardia.py          ← también contiene EstadoIngreso y Prioridad
├── schemas/
│   ├── __init__.py
│   ├── paciente.py
│   ├── medico.py
│   └── ingreso_guardia.py
└── tests/
    ├── __init__.py
    ├── conftest.py                 ← fixture de DB en memoria
    ├── test_models.py
    └── test_schemas.py
```

---

## Task 1: Instalar pytest y crear `database.py`

**Files:**
- Modify: `backend/requirements.txt`
- Create: `backend/database.py`
- Create: `backend/tests/__init__.py`
- Create: `backend/tests/conftest.py`

- [ ] **Step 1: Instalar pytest en el venv**

```bash
cd backend
source venv/bin/activate
pip install pytest
pip freeze > requirements.txt
```

- [ ] **Step 2: Crear `backend/pytest.ini`**

Esto le dice a pytest que agregue `backend/` al Python path y dónde buscar los tests:

```ini
[pytest]
pythonpath = .
testpaths = tests
```

- [ ] **Step 3: Crear `backend/database.py`**

```python
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

SQLALCHEMY_DATABASE_URL = "sqlite:///./guardia.db"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()
```

- [ ] **Step 4: Crear `backend/tests/__init__.py`** (vacío)

- [ ] **Step 5: Crear `backend/tests/conftest.py`**

```python
import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from database import Base

@pytest.fixture
def db():
    engine = create_engine(
        "sqlite:///:memory:",
        connect_args={"check_same_thread": False},
    )
    Base.metadata.create_all(bind=engine)
    Session = sessionmaker(bind=engine)
    session = Session()
    yield session
    session.close()
    Base.metadata.drop_all(bind=engine)
```

- [ ] **Step 6: Verificar que pytest corre sin errores desde `backend/`**

```bash
cd backend && source venv/bin/activate && pytest -v
```

Resultado esperado: `no tests ran` sin errores de importación.

- [ ] **Step 7: Commit**

```bash
git add backend/database.py backend/pytest.ini backend/tests/ backend/requirements.txt
git commit -m "feat: configuracion de base de datos y setup de tests"
```

---

## Task 2: Modelo `Paciente`

**Files:**
- Create: `backend/models/__init__.py`
- Create: `backend/models/paciente.py`
- Modify: `backend/tests/test_models.py`

- [ ] **Step 1: Crear `backend/models/__init__.py`** (vacío)

- [ ] **Step 2: Escribir los tests fallidos en `backend/tests/test_models.py`**

```python
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
```

- [ ] **Step 3: Correr los tests para verificar que fallan**

```bash
cd backend && source venv/bin/activate && pytest tests/test_models.py -v
```

Resultado esperado: `ImportError` o `ModuleNotFoundError` para `models.paciente`.

- [ ] **Step 4: Crear `backend/models/paciente.py`**

```python
from sqlalchemy import Column, Integer, String, Date
from sqlalchemy.orm import relationship
from database import Base


class Paciente(Base):
    __tablename__ = "pacientes"

    id = Column(Integer, primary_key=True, index=True)
    dni = Column(String, unique=True, nullable=False, index=True)
    nombre = Column(String, nullable=False)
    apellido = Column(String, nullable=False)
    fecha_nacimiento = Column(Date, nullable=False)
    telefono = Column(String, nullable=True)

    ingresos = relationship("IngresoGuardia", back_populates="paciente")
```

- [ ] **Step 5: Correr los tests y verificar que pasan**

```bash
cd backend && source venv/bin/activate && pytest tests/test_models.py -v
```

Resultado esperado: 3 tests PASSED.

- [ ] **Step 6: Commit**

```bash
git add backend/models/ backend/tests/test_models.py
git commit -m "feat: modelo Paciente con tests"
```

---

## Task 3: Modelo `Medico`

**Files:**
- Create: `backend/models/medico.py`
- Modify: `backend/tests/test_models.py`

- [ ] **Step 1: Agregar tests para `Medico` al final de `backend/tests/test_models.py`**

```python
from models.medico import Medico


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
```

- [ ] **Step 2: Correr para verificar que fallan**

```bash
cd backend && source venv/bin/activate && pytest tests/test_models.py::test_crear_medico -v
```

Resultado esperado: `ImportError` para `models.medico`.

- [ ] **Step 3: Crear `backend/models/medico.py`**

```python
from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship
from database import Base


class Medico(Base):
    __tablename__ = "medicos"

    id = Column(Integer, primary_key=True, index=True)
    nombre = Column(String, nullable=False)
    apellido = Column(String, nullable=False)
    matricula = Column(String, unique=True, nullable=False)
    especialidad = Column(String, nullable=True)

    ingresos = relationship("IngresoGuardia", back_populates="medico")
```

- [ ] **Step 4: Correr todos los tests**

```bash
cd backend && source venv/bin/activate && pytest tests/test_models.py -v
```

Resultado esperado: 6 tests PASSED.

- [ ] **Step 5: Commit**

```bash
git add backend/models/medico.py backend/tests/test_models.py
git commit -m "feat: modelo Medico con tests"
```

---

## Task 4: Modelo `IngresoGuardia` y Enums

**Files:**
- Create: `backend/models/ingreso_guardia.py`
- Modify: `backend/tests/test_models.py`

- [ ] **Step 1: Agregar tests para `IngresoGuardia` al final de `backend/tests/test_models.py`**

```python
from models.ingreso_guardia import IngresoGuardia, EstadoIngreso, Prioridad


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
    medico = Medico(nombre="Rosa", apellido="Flores", matricula="MP55555")
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
```

- [ ] **Step 2: Correr para verificar que fallan**

```bash
cd backend && source venv/bin/activate && pytest tests/test_models.py::test_crear_ingreso_estado_inicial -v
```

Resultado esperado: `ImportError` para `models.ingreso_guardia`.

- [ ] **Step 3: Crear `backend/models/ingreso_guardia.py`**

```python
from datetime import datetime
from enum import Enum
from sqlalchemy import Column, Integer, String, DateTime, Text, ForeignKey, Enum as SAEnum
from sqlalchemy.orm import relationship
from database import Base


class EstadoIngreso(str, Enum):
    EN_ESPERA = "EN_ESPERA"
    EN_ATENCION = "EN_ATENCION"
    ALTA = "ALTA"


class Prioridad(str, Enum):
    BAJA = "BAJA"
    MEDIA = "MEDIA"
    ALTA = "ALTA"


class IngresoGuardia(Base):
    __tablename__ = "ingresos_guardia"

    id = Column(Integer, primary_key=True, index=True)
    paciente_id = Column(Integer, ForeignKey("pacientes.id"), nullable=False)
    medico_id = Column(Integer, ForeignKey("medicos.id"), nullable=True)
    estado = Column(SAEnum(EstadoIngreso), default=EstadoIngreso.EN_ESPERA, nullable=False)
    prioridad = Column(SAEnum(Prioridad), nullable=False)
    fecha_ingreso = Column(DateTime, default=datetime.utcnow, nullable=False)
    observaciones = Column(Text, nullable=True)

    paciente = relationship("Paciente", back_populates="ingresos")
    medico = relationship("Medico", back_populates="ingresos")
```

- [ ] **Step 4: Correr todos los tests**

```bash
cd backend && source venv/bin/activate && pytest tests/test_models.py -v
```

Resultado esperado: 9 tests PASSED.

- [ ] **Step 5: Commit**

```bash
git add backend/models/ingreso_guardia.py backend/tests/test_models.py
git commit -m "feat: modelo IngresoGuardia con enums y tests"
```

---

## Task 5: Schema `Paciente`

**Files:**
- Create: `backend/schemas/__init__.py`
- Create: `backend/schemas/paciente.py`
- Create: `backend/tests/test_schemas.py`

- [ ] **Step 1: Crear `backend/schemas/__init__.py`** (vacío)

- [ ] **Step 2: Escribir tests fallidos en `backend/tests/test_schemas.py`**

```python
from datetime import date, datetime
from schemas.paciente import PacienteCreate, PacienteResponse


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
    from models.paciente import Paciente
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
```

- [ ] **Step 3: Correr para verificar que fallan**

```bash
cd backend && source venv/bin/activate && pytest tests/test_schemas.py -v
```

Resultado esperado: `ImportError` para `schemas.paciente`.

- [ ] **Step 4: Crear `backend/schemas/paciente.py`**

```python
from datetime import date
from pydantic import BaseModel, ConfigDict, computed_field


class PacienteCreate(BaseModel):
    dni: str
    nombre: str
    apellido: str
    fecha_nacimiento: date
    telefono: str | None = None


class PacienteResponse(PacienteCreate):
    model_config = ConfigDict(from_attributes=True)

    id: int

    @computed_field
    @property
    def edad(self) -> int:
        today = date.today()
        born = self.fecha_nacimiento
        return today.year - born.year - ((today.month, today.day) < (born.month, born.day))
```

- [ ] **Step 5: Correr los tests**

```bash
cd backend && source venv/bin/activate && pytest tests/test_schemas.py -v
```

Resultado esperado: 4 tests PASSED.

- [ ] **Step 6: Commit**

```bash
git add backend/schemas/ backend/tests/test_schemas.py
git commit -m "feat: schema Paciente con campo calculado edad"
```

---

## Task 6: Schema `Medico`

**Files:**
- Create: `backend/schemas/medico.py`
- Modify: `backend/tests/test_schemas.py`

- [ ] **Step 1: Agregar tests para `MedicoCreate` y `MedicoResponse` al final de `backend/tests/test_schemas.py`**

```python
from schemas.medico import MedicoCreate, MedicoResponse


def test_medico_create_campos_requeridos():
    m = MedicoCreate(nombre="Ana", apellido="García", matricula="MP99999")
    assert m.especialidad is None


def test_medico_create_con_especialidad():
    m = MedicoCreate(nombre="Ana", apellido="García", matricula="MP99999", especialidad="Cardiología")
    assert m.especialidad == "Cardiología"


def test_medico_response_tiene_id():
    m = MedicoResponse(id=5, nombre="Ana", apellido="García", matricula="MP99999")
    assert m.id == 5


def test_medico_response_desde_orm(db):
    from models.medico import Medico
    medico = Medico(nombre="Roberto", apellido="Silva", matricula="MP77777", especialidad="Traumatología")
    db.add(medico)
    db.commit()
    db.refresh(medico)

    response = MedicoResponse.model_validate(medico)
    assert response.matricula == "MP77777"
    assert response.especialidad == "Traumatología"
```

- [ ] **Step 2: Correr para verificar que fallan**

```bash
cd backend && source venv/bin/activate && pytest tests/test_schemas.py::test_medico_create_campos_requeridos -v
```

Resultado esperado: `ImportError` para `schemas.medico`.

- [ ] **Step 3: Crear `backend/schemas/medico.py`**

```python
from pydantic import BaseModel, ConfigDict


class MedicoCreate(BaseModel):
    nombre: str
    apellido: str
    matricula: str
    especialidad: str | None = None


class MedicoResponse(MedicoCreate):
    model_config = ConfigDict(from_attributes=True)

    id: int
```

- [ ] **Step 4: Correr todos los tests**

```bash
cd backend && source venv/bin/activate && pytest tests/ -v
```

Resultado esperado: 13 tests PASSED.

- [ ] **Step 5: Commit**

```bash
git add backend/schemas/medico.py backend/tests/test_schemas.py
git commit -m "feat: schema Medico"
```

---

## Task 7: Schema `IngresoGuardia`

**Files:**
- Create: `backend/schemas/ingreso_guardia.py`
- Modify: `backend/tests/test_schemas.py`

- [ ] **Step 1: Agregar tests para `IngresoGuardiaCreate` e `IngresoGuardiaResponse` al final de `backend/tests/test_schemas.py`**

```python
from datetime import datetime
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
        fecha_ingreso=datetime.utcnow(),
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

    response = IngresoGuardiaResponse.model_validate(ingreso)
    assert response.estado == EstadoIngreso.EN_ESPERA
    assert response.paciente.dni == "33333333"
    assert response.medico is None
```

- [ ] **Step 2: Correr para verificar que fallan**

```bash
cd backend && source venv/bin/activate && pytest tests/test_schemas.py::test_ingreso_create_campos_requeridos -v
```

Resultado esperado: `ImportError` para `schemas.ingreso_guardia`.

- [ ] **Step 3: Crear `backend/schemas/ingreso_guardia.py`**

```python
from datetime import datetime
from pydantic import BaseModel, ConfigDict
from models.ingreso_guardia import EstadoIngreso, Prioridad
from schemas.paciente import PacienteResponse
from schemas.medico import MedicoResponse


class IngresoGuardiaCreate(BaseModel):
    paciente_id: int
    prioridad: Prioridad


class IngresoGuardiaResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    paciente_id: int
    medico_id: int | None = None
    estado: EstadoIngreso
    prioridad: Prioridad
    fecha_ingreso: datetime
    observaciones: str | None = None
    paciente: PacienteResponse
    medico: MedicoResponse | None = None
```

- [ ] **Step 4: Correr todos los tests**

```bash
cd backend && source venv/bin/activate && pytest tests/ -v
```

Resultado esperado: 16 tests PASSED.

- [ ] **Step 5: Commit**

```bash
git add backend/schemas/ingreso_guardia.py backend/tests/test_schemas.py
git commit -m "feat: schema IngresoGuardia con objetos anidados"
```
