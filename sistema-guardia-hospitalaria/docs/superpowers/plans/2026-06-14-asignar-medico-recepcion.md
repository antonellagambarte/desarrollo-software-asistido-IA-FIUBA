# Asignación de médico en recepción — Plan de implementación

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Agregar un selector de médico opcional en el formulario de ingreso a guardia, mostrando cuántos pacientes en espera tiene cada médico.

**Architecture:** Nuevo endpoint `GET /medicos/con-carga` en el backend que devuelve médicos con conteo de pacientes por estado. El formulario `FormularioIngreso.vue` carga esa lista al montarse y, si se elige un médico, llama al endpoint `PATCH /ingresos/{id}/medico` ya existente después de crear el ingreso.

**Tech Stack:** FastAPI, SQLAlchemy, Pydantic (backend); Nuxt 3 + Vue 3 + Vuetify (frontend).

---

## Archivos a modificar

| Archivo | Acción |
|---|---|
| `backend/schemas/medico.py` | Agregar `MedicoConCargaResponse` |
| `backend/services/medico.py` | Agregar `obtener_medicos_con_carga()` |
| `backend/routers/medico.py` | Agregar `GET /medicos/con-carga` |
| `backend/tests/test_medico_endpoints.py` | Agregar 4 tests del nuevo endpoint |
| `frontend/services/medicoService.js` | Agregar `listarMedicosConCarga()` |
| `frontend/components/FormularioIngreso.vue` | Agregar selector de médico |

---

## Task 1: Backend — endpoint `GET /medicos/con-carga`

**Files:**
- Modify: `backend/schemas/medico.py`
- Modify: `backend/services/medico.py`
- Modify: `backend/routers/medico.py`
- Test: `backend/tests/test_medico_endpoints.py`

### Contexto

El endpoint devuelve todos los médicos con el conteo de ingresos asignados a cada uno filtrado por estado. Por defecto filtra `EN_ESPERA`. Se reutilizan los modelos ORM `Medico` e `IngresoGuardia` ya existentes.

El archivo `backend/tests/test_medico_endpoints.py` ya tiene `MEDICO_DATA` y `MEDICO_DATA_2` como dicts en el módulo. Los tests nuevos necesitan crear pacientes e ingresos vía HTTP (igual que en `test_ingreso_guardia_endpoints.py`).

- [ ] **Step 1: Agregar `PACIENTE_DATA` y 4 tests al final de `test_medico_endpoints.py`**

Agregar al final del archivo `backend/tests/test_medico_endpoints.py`:

```python
PACIENTE_DATA = {
    "dni": "55555555",
    "nombre": "Marta",
    "apellido": "Ruiz",
    "fecha_nacimiento": "1980-03-10",
}


def test_medicos_con_carga_lista_vacia(client):
    response = client.get("/medicos/con-carga")
    assert response.status_code == 200
    assert response.json() == []


def test_medicos_con_carga_sin_ingresos(client):
    client.post("/medicos/", json=MEDICO_DATA)
    response = client.get("/medicos/con-carga")
    data = response.json()
    assert len(data) == 1
    assert data[0]["pacientes_en_espera"] == 0


def test_medicos_con_carga_cuenta_en_espera(client):
    medico = client.post("/medicos/", json=MEDICO_DATA).json()
    paciente = client.post("/pacientes/", json=PACIENTE_DATA).json()
    ingreso = client.post(
        "/ingresos/", json={"paciente_id": paciente["id"], "prioridad": "ALTA"}
    ).json()
    client.patch(f"/ingresos/{ingreso['id']}/medico", json={"medico_id": medico["id"]})

    response = client.get("/medicos/con-carga")
    data = response.json()
    assert data[0]["pacientes_en_espera"] == 1


def test_medicos_con_carga_estado_personalizado(client):
    medico = client.post("/medicos/", json=MEDICO_DATA).json()
    paciente = client.post("/pacientes/", json=PACIENTE_DATA).json()
    ingreso = client.post(
        "/ingresos/", json={"paciente_id": paciente["id"], "prioridad": "ALTA"}
    ).json()
    client.patch(f"/ingresos/{ingreso['id']}/medico", json={"medico_id": medico["id"]})
    client.patch(f"/ingresos/{ingreso['id']}/estado", json={"estado": "EN_ATENCION"})

    en_espera = client.get("/medicos/con-carga?estado=EN_ESPERA").json()
    en_atencion = client.get("/medicos/con-carga?estado=EN_ATENCION").json()
    assert en_espera[0]["pacientes_en_espera"] == 0
    assert en_atencion[0]["pacientes_en_espera"] == 1
```

- [ ] **Step 2: Verificar que los tests fallan**

```bash
cd backend && python -m pytest tests/test_medico_endpoints.py::test_medicos_con_carga_lista_vacia tests/test_medico_endpoints.py::test_medicos_con_carga_sin_ingresos tests/test_medico_endpoints.py::test_medicos_con_carga_cuenta_en_espera tests/test_medico_endpoints.py::test_medicos_con_carga_estado_personalizado -v
```

Expected: 4 FAILED (404 Not Found — el endpoint no existe todavía).

- [ ] **Step 3: Agregar `MedicoConCargaResponse` en `backend/schemas/medico.py`**

Reemplazar el contenido completo del archivo:

```python
from pydantic import BaseModel, ConfigDict


class MedicoCreate(BaseModel):
    nombre: str
    apellido: str
    matricula: str
    especialidad: str
    username: str
    password: str


class MedicoResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    nombre: str
    apellido: str
    matricula: str
    especialidad: str
    username: str


class MedicoConCargaResponse(MedicoResponse):
    pacientes_en_espera: int
```

- [ ] **Step 4: Agregar `obtener_medicos_con_carga()` en `backend/services/medico.py`**

Reemplazar el contenido completo del archivo:

```python
from typing import List
from sqlalchemy import func
from sqlalchemy.orm import Session
from models.medico import Medico
from models.ingreso_guardia import IngresoGuardia, EstadoIngreso
from schemas.medico import MedicoCreate, MedicoConCargaResponse
from security import hash_password


def crear_medico(db: Session, data: MedicoCreate) -> Medico:
    if db.query(Medico).filter(Medico.matricula == data.matricula).first():
        raise ValueError(f"Ya existe un médico con matrícula {data.matricula}")
    if db.query(Medico).filter(Medico.username == data.username).first():
        raise ValueError(f"Ya existe un médico con usuario {data.username}")
    medico_data = data.model_dump(exclude={"password"})
    medico_data["password_hash"] = hash_password(data.password)
    medico = Medico(**medico_data)
    db.add(medico)
    db.commit()
    db.refresh(medico)
    return medico


def obtener_medicos(db: Session) -> List[Medico]:
    return db.query(Medico).all()


def obtener_medicos_con_carga(
    db: Session, estado: EstadoIngreso = EstadoIngreso.EN_ESPERA
) -> List[MedicoConCargaResponse]:
    medicos = db.query(Medico).all()
    result = []
    for m in medicos:
        count = (
            db.query(func.count(IngresoGuardia.id))
            .filter(
                IngresoGuardia.medico_id == m.id,
                IngresoGuardia.estado == estado,
            )
            .scalar()
            or 0
        )
        result.append(
            MedicoConCargaResponse(
                id=m.id,
                nombre=m.nombre,
                apellido=m.apellido,
                matricula=m.matricula,
                especialidad=m.especialidad,
                username=m.username,
                pacientes_en_espera=count,
            )
        )
    return result
```

- [ ] **Step 5: Agregar el endpoint en `backend/routers/medico.py`**

Reemplazar el contenido completo del archivo:

```python
from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from dependencies import get_db
from models.ingreso_guardia import EstadoIngreso
from schemas.medico import MedicoCreate, MedicoResponse, MedicoConCargaResponse
from services import medico as medico_service

router = APIRouter(prefix="/medicos", tags=["medicos"])


@router.post("/", response_model=MedicoResponse, status_code=status.HTTP_201_CREATED)
def crear_medico(data: MedicoCreate, db: Session = Depends(get_db)):
    try:
        return medico_service.crear_medico(db, data)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(e))


@router.get("/", response_model=List[MedicoResponse])
def listar_medicos(db: Session = Depends(get_db)):
    return medico_service.obtener_medicos(db)


@router.get("/con-carga", response_model=List[MedicoConCargaResponse])
def listar_medicos_con_carga(
    estado: EstadoIngreso = EstadoIngreso.EN_ESPERA,
    db: Session = Depends(get_db),
):
    return medico_service.obtener_medicos_con_carga(db, estado)
```

- [ ] **Step 6: Verificar que los 4 tests nuevos pasan y los anteriores siguen pasando**

```bash
cd backend && python -m pytest tests/test_medico_endpoints.py -v
```

Expected: todos los tests PASSED (7 anteriores + 4 nuevos = 11 total).

- [ ] **Step 7: Correr el suite completo**

```bash
cd backend && python -m pytest -v
```

Expected: todos los tests PASSED.

- [ ] **Step 8: Commit**

```bash
git add backend/schemas/medico.py backend/services/medico.py backend/routers/medico.py backend/tests/test_medico_endpoints.py
git commit -m "feat: endpoint GET /medicos/con-carga con conteo de pacientes por estado"
```

---

## Task 2: Frontend — `listarMedicosConCarga()` en `medicoService.js`

**Files:**
- Modify: `frontend/services/medicoService.js`

### Contexto

Agregar una función que consume el nuevo endpoint. El `estado` es opcional y por defecto `'EN_ESPERA'`. La función lanza `Error` si el backend devuelve error, igual que las funciones existentes en el archivo.

- [ ] **Step 1: Agregar `listarMedicosConCarga` en `frontend/services/medicoService.js`**

Reemplazar el contenido completo del archivo:

```js
const BASE = 'http://localhost:8000'

export async function listarMedicos() {
  const res = await fetch(`${BASE}/medicos/`)
  if (!res.ok) throw new Error('Error al obtener médicos')
  return res.json()
}

export async function listarMedicosConCarga(estado = 'EN_ESPERA') {
  const res = await fetch(`${BASE}/medicos/con-carga?estado=${estado}`)
  if (!res.ok) throw new Error('Error al obtener médicos con carga')
  return res.json()
}

export async function crearMedico(data) {
  const res = await fetch(`${BASE}/medicos/`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(data),
  })
  if (res.status === 409) {
    const err = await res.json()
    throw new Error(err.detail ?? 'Matrícula o usuario ya registrado')
  }
  if (!res.ok) throw new Error('Error al registrar médico')
  return res.json()
}
```

- [ ] **Step 2: Commit**

```bash
git add frontend/services/medicoService.js
git commit -m "feat: agregar listarMedicosConCarga en medicoService"
```

---

## Task 3: Frontend — selector de médico en `FormularioIngreso.vue`

**Files:**
- Modify: `frontend/components/FormularioIngreso.vue`

### Contexto

El formulario actual (`frontend/components/FormularioIngreso.vue`) tiene: `v-select` de prioridad (requerido), `v-textarea` de observaciones (opcional), `v-alert` de error, y botón de submit. El script importa `crearIngreso` de `ingresoService` y llama a `asignarMedico` — que ya existe en `ingresoService.js` — no está importado todavía.

Agregar:
- `v-select` de médico (opcional, clearable) con las opciones calculadas a partir de `listarMedicosConCarga()`
- Cada opción muestra: `"Apellido, Nombre (Especialidad) — N en espera"`
- `onMounted` que carga los médicos
- Si falla la carga: select deshabilitado con hint de error
- Si la lista está vacía: select deshabilitado con "No hay médicos disponibles"
- Al guardar con médico seleccionado: `POST /ingresos/` → `PATCH /ingresos/{id}/medico`
- Si el PATCH falla después del POST: emite `@ingreso-creado` igual + muestra `v-alert` de warning

- [ ] **Step 1: Reemplazar `frontend/components/FormularioIngreso.vue`**

```vue
<template>
  <v-card>
    <v-card-text>
      <div class="text-subtitle-1 font-weight-medium mb-1">Registrar ingreso a guardia</div>
      <div class="text-body-2 text-medium-emphasis mb-4">{{ nombrePaciente }}</div>

      <v-form ref="formRef" @submit.prevent="guardar">
        <v-row>
          <v-col cols="12" sm="6">
            <v-select
              v-model="prioridad"
              :items="prioridades"
              label="Prioridad"
              variant="outlined"
              :rules="[requerido]"
            />
          </v-col>
          <v-col cols="12" sm="6">
            <v-select
              v-model="medicoId"
              :items="opcionesMedicos"
              item-title="label"
              item-value="id"
              label="Médico asignado (opcional)"
              variant="outlined"
              clearable
              :loading="cargandoMedicos"
              :disabled="cargandoMedicos || opcionesMedicos.length === 0"
              :hint="hintMedicos"
              persistent-hint
            />
          </v-col>
          <v-col cols="12">
            <v-textarea
              v-model="observaciones"
              label="Observaciones (opcional)"
              variant="outlined"
              rows="3"
            />
          </v-col>
        </v-row>

        <v-alert v-if="error" type="error" variant="tonal" class="mb-4">{{ error }}</v-alert>
        <v-alert v-if="advertencia" type="warning" variant="tonal" class="mb-4">{{ advertencia }}</v-alert>

        <v-btn type="submit" color="primary" variant="flat" :loading="cargando">
          Registrar ingreso
        </v-btn>
      </v-form>
    </v-card-text>
  </v-card>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { crearIngreso, asignarMedico } from '~/services/ingresoService'
import { listarMedicosConCarga } from '~/services/medicoService'

const props = defineProps({
  pacienteId: { type: Number, required: true },
  nombrePaciente: { type: String, default: '' },
})
const emit = defineEmits(['ingreso-creado'])

const formRef = ref(null)
const cargando = ref(false)
const cargandoMedicos = ref(false)
const error = ref('')
const advertencia = ref('')
const prioridad = ref(null)
const observaciones = ref('')
const medicoId = ref(null)
const medicos = ref([])
const errorCargaMedicos = ref(false)

const prioridades = ['BAJA', 'MEDIA', 'ALTA']
const requerido = (v) => !!v || 'Campo requerido'

const opcionesMedicos = computed(() =>
  medicos.value.map((m) => ({
    id: m.id,
    label: `${m.apellido}, ${m.nombre} (${m.especialidad}) — ${m.pacientes_en_espera} en espera`,
  }))
)

const hintMedicos = computed(() => {
  if (errorCargaMedicos.value) return 'No se pudieron cargar los médicos'
  if (!cargandoMedicos.value && medicos.value.length === 0) return 'No hay médicos disponibles'
  return ''
})

onMounted(async () => {
  cargandoMedicos.value = true
  try {
    medicos.value = await listarMedicosConCarga()
  } catch {
    errorCargaMedicos.value = true
  } finally {
    cargandoMedicos.value = false
  }
})

async function guardar() {
  const { valid } = await formRef.value.validate()
  if (!valid) return

  cargando.value = true
  error.value = ''
  advertencia.value = ''

  try {
    const data = {
      paciente_id: props.pacienteId,
      prioridad: prioridad.value,
      ...(observaciones.value ? { observaciones: observaciones.value } : {}),
    }
    const ingreso = await crearIngreso(data)

    if (medicoId.value) {
      try {
        await asignarMedico(ingreso.id, medicoId.value)
      } catch {
        advertencia.value =
          'Ingreso registrado, pero no se pudo asignar el médico. Podés asignarlo desde la tabla.'
      }
    }

    emit('ingreso-creado', ingreso)
  } catch (e) {
    error.value = e?.message || 'Error inesperado'
  } finally {
    cargando.value = false
  }
}
</script>
```

- [ ] **Step 2: Verificar manualmente en el browser**

Con el backend corriendo (`cd backend && uvicorn main:app --reload`) y el frontend (`cd frontend && npm run dev`):

1. Ir a `http://localhost:3000/recepcion`
2. Buscar o registrar un paciente
3. En el formulario de ingreso: verificar que el selector de médico aparece (si hay médicos cargados)
4. Si no hay médicos: el select muestra "No hay médicos disponibles"
5. Seleccionar un médico y registrar el ingreso
6. Verificar que el ingreso aparece en la tabla

- [ ] **Step 3: Commit**

```bash
git add frontend/components/FormularioIngreso.vue
git commit -m "feat: selector de médico con conteo en FormularioIngreso"
```
