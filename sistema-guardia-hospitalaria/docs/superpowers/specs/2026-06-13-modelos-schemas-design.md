# Diseño: Modelos SQLAlchemy y Schemas Pydantic

**Fecha:** 2026-06-13  
**Alcance:** Modelos de base de datos y schemas de validación para las tres entidades principales. Sin endpoints.

---

## Contexto

El backend usa FastAPI + SQLAlchemy + SQLite. Se necesitan los modelos ORM y schemas Pydantic para `Paciente`, `Médico` e `IngresoGuardia` antes de implementar endpoints.

---

## Estructura de archivos

```
backend/
├── database.py
├── models/
│   ├── __init__.py
│   ├── paciente.py
│   ├── medico.py
│   └── ingreso_guardia.py
└── schemas/
    ├── __init__.py
    ├── paciente.py
    ├── medico.py
    └── ingreso_guardia.py
```

---

## `database.py`

Centraliza la configuración de SQLAlchemy:
- `Base = declarative_base()`
- Engine SQLite apuntando a `guardia.db`
- `SessionLocal` con `autocommit=False`, `autoflush=False`

---

## Modelos SQLAlchemy

### `Paciente`

| Campo | Tipo SQLAlchemy | Restricciones |
|---|---|---|
| `id` | Integer | PK, autoincrement |
| `dni` | String | unique, not null, indexed |
| `nombre` | String | not null |
| `apellido` | String | not null |
| `fecha_nacimiento` | Date | not null |
| `telefono` | String | nullable |

Relación: `ingresos` → lista de `IngresoGuardia` (back_populates).

### `Medico`

| Campo | Tipo SQLAlchemy | Restricciones |
|---|---|---|
| `id` | Integer | PK, autoincrement |
| `nombre` | String | not null |
| `apellido` | String | not null |
| `matricula` | String | unique, not null |
| `especialidad` | String | nullable |

Relación: `ingresos` → lista de `IngresoGuardia` (back_populates).

### `IngresoGuardia`

| Campo | Tipo SQLAlchemy | Restricciones |
|---|---|---|
| `id` | Integer | PK, autoincrement |
| `paciente_id` | Integer | FK → paciente.id, not null |
| `medico_id` | Integer | FK → medico.id, nullable |
| `estado` | String (Enum) | default `EN_ESPERA` |
| `prioridad` | String (Enum) | not null |
| `fecha_ingreso` | DateTime | default `utcnow` |
| `observaciones` | Text | nullable |

Relaciones: `paciente` y `medico` (back_populates).

### Enums (Python `enum.Enum`, almacenados como String)

```python
class EstadoIngreso(str, Enum):
    EN_ESPERA = "EN_ESPERA"
    EN_ATENCION = "EN_ATENCION"
    ALTA = "ALTA"

class Prioridad(str, Enum):
    BAJA = "BAJA"
    MEDIA = "MEDIA"
    ALTA = "ALTA"
```

---

## Schemas Pydantic

Cada entidad tiene dos schemas:

### `Paciente`

- **`PacienteCreate`**: `dni`, `nombre`, `apellido`, `fecha_nacimiento`, `telefono`
- **`PacienteResponse`**: todo lo anterior + `id` + `edad` (campo computado con `@computed_field`)

### `Medico`

- **`MedicoCreate`**: `nombre`, `apellido`, `matricula`, `especialidad`
- **`MedicoResponse`**: todo lo anterior + `id`

### `IngresoGuardia`

- **`IngresoGuardiaCreate`**: `paciente_id`, `prioridad` — `estado` y `fecha_ingreso` se setean en el backend
- **`IngresoGuardiaResponse`**: todos los campos + objetos anidados `paciente: PacienteResponse` y `medico: MedicoResponse | None`

Todos los schemas de respuesta usan `model_config = ConfigDict(from_attributes=True)`.

---

## Reglas de negocio (a respetar en servicios/endpoints, no en modelos)

- Estado inicial de ingreso: `EN_ESPERA`
- Transiciones válidas: `EN_ESPERA` → `EN_ATENCION` → `ALTA`
- Estado `ALTA` es final, no se modifica
- Prioridad se asigna manualmente, nunca automáticamente
