# Vista Médico — Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Implementar la página `/medico` con login mínimo (usuario/contraseña), tabla de pacientes activos con filtro por estado y acciones para tomar pacientes, registrar observaciones y dar altas.

**Architecture:** El backend extiende el modelo `Medico` con credenciales hashed (passlib/bcrypt), agrega `POST /auth/login` y `PATCH /ingresos/{id}/observaciones`. El frontend agrega un store Pinia para la sesión del médico y una página `/medico` con componentes `LoginMedico`, `TablaPacientesMedico` y `DialogObservaciones`.

**Tech Stack:** FastAPI + SQLAlchemy + passlib[bcrypt] (backend); Nuxt 3 + Vuetify 3 + Pinia (frontend).

---

## Mapa de archivos

```
backend/
  security.py                       CREAR — hash_password / verify_password
  models/medico.py                  MODIFICAR — agregar username, password_hash
  schemas/medico.py                 MODIFICAR — MedicoCreate + MedicoResponse independiente
  schemas/auth.py                   CREAR — LoginRequest
  schemas/ingreso_guardia.py        MODIFICAR — agregar ActualizarObservacionesRequest
  services/medico.py                MODIFICAR — hashear password, validar username único
  services/auth.py                  CREAR — verificar_credenciales()
  services/ingreso_guardia.py       MODIFICAR — agregar actualizar_observaciones()
  routers/auth.py                   CREAR — POST /auth/login
  routers/ingreso_guardia.py        MODIFICAR — agregar PATCH /{id}/observaciones
  main.py                           MODIFICAR — registrar router auth

frontend/
  services/authService.js           CREAR — login()
  services/medicoService.js         CREAR — listarMedicos()
  services/ingresoService.js        MODIFICAR — agregar cambiarEstado, asignarMedico, actualizarObservaciones
  stores/authStore.js               CREAR — medico, estaLogueado, login, logout, cargarSesion
  pages/medico.vue                  CREAR — página principal
  components/LoginMedico.vue        CREAR — formulario login
  components/TablaPacientesMedico.vue CREAR — tabla con filtro + dialogs
  components/DialogObservaciones.vue  CREAR — dialog editar observaciones
```

---

## Task 1: Backend — credenciales en modelo Medico

**Files:**
- Create: `backend/security.py`
- Modify: `backend/models/medico.py`
- Modify: `backend/schemas/medico.py`
- Modify: `backend/services/medico.py`

- [ ] **Step 1: Instalar passlib**

```bash
cd backend
pip install passlib[bcrypt]
```

Si existe `requirements.txt`, agregar la línea `passlib[bcrypt]`.

- [ ] **Step 2: Crear `backend/security.py`**

```python
from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def hash_password(password: str) -> str:
    return pwd_context.hash(password)


def verify_password(plain: str, hashed: str) -> bool:
    return pwd_context.verify(plain, hashed)
```

- [ ] **Step 3: Agregar columnas al modelo `backend/models/medico.py`**

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
    username = Column(String, unique=True, nullable=False)
    password_hash = Column(String, nullable=False)

    ingresos = relationship("IngresoGuardia", back_populates="medico")
```

- [ ] **Step 4: Actualizar `backend/schemas/medico.py`**

`MedicoResponse` deja de heredar de `MedicoCreate` para no exponer `password`.

```python
from typing import Optional
from pydantic import BaseModel, ConfigDict


class MedicoCreate(BaseModel):
    nombre: str
    apellido: str
    matricula: str
    especialidad: Optional[str] = None
    username: str
    password: str


class MedicoResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    nombre: str
    apellido: str
    matricula: str
    especialidad: Optional[str] = None
    username: str
```

- [ ] **Step 5: Actualizar `backend/services/medico.py`**

```python
from typing import List
from sqlalchemy.orm import Session
from models.medico import Medico
from schemas.medico import MedicoCreate
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
```

- [ ] **Step 6: Eliminar `guardia.db` para que SQLAlchemy recree la tabla con las nuevas columnas**

```bash
rm -f backend/guardia.db
```

> ⚠️ Esto borra todos los datos existentes. Es el enfoque correcto para desarrollo local sin migraciones.

- [ ] **Step 7: Verificar que el backend arranca sin errores**

```bash
cd backend
uvicorn main:app --reload
```

Esperado: `Application startup complete.` sin errores de columnas faltantes.

- [ ] **Step 8: Commit**

```bash
git add backend/security.py backend/models/medico.py backend/schemas/medico.py backend/services/medico.py
git commit -m "feat: credenciales (username + password_hash) en modelo Medico"
```

---

## Task 2: Backend — POST /auth/login

**Files:**
- Create: `backend/schemas/auth.py`
- Create: `backend/services/auth.py`
- Create: `backend/routers/auth.py`
- Modify: `backend/main.py`

- [ ] **Step 1: Crear `backend/schemas/auth.py`**

```python
from pydantic import BaseModel


class LoginRequest(BaseModel):
    username: str
    password: str
```

- [ ] **Step 2: Crear `backend/services/auth.py`**

```python
from sqlalchemy.orm import Session
from models.medico import Medico
from security import verify_password


def verificar_credenciales(db: Session, username: str, password: str) -> Medico:
    medico = db.query(Medico).filter(Medico.username == username).first()
    if medico is None or not verify_password(password, medico.password_hash):
        raise ValueError("Credenciales incorrectas")
    return medico
```

- [ ] **Step 3: Crear `backend/routers/auth.py`**

```python
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
```

- [ ] **Step 4: Registrar el router en `backend/main.py`**

Agregar las dos líneas marcadas con `# NUEVO`:

```python
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from database import Base, engine
import models  # noqa: F401
from routers.paciente import router as paciente_router
from routers.medico import router as medico_router
from routers.ingreso_guardia import router as ingreso_router
from routers.auth import router as auth_router  # NUEVO

Base.metadata.create_all(bind=engine)

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:3001"],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(paciente_router)
app.include_router(medico_router)
app.include_router(ingreso_router)
app.include_router(auth_router)  # NUEVO


@app.get("/")
def root():
    return {"status": "ok"}
```

- [ ] **Step 5: Probar manualmente — crear médico y hacer login**

Con el servidor corriendo (`uvicorn main:app --reload`), ejecutar:

```bash
# Crear un médico con credenciales
curl -s -X POST http://localhost:8000/medicos/ \
  -H "Content-Type: application/json" \
  -d '{"nombre":"Ana","apellido":"García","matricula":"MP-1234","username":"dragarcia","password":"clave123"}' | python3 -m json.tool

# Login correcto — esperar 200 con objeto médico
curl -s -X POST http://localhost:8000/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username":"dragarcia","password":"clave123"}' | python3 -m json.tool

# Login incorrecto — esperar 401
curl -s -o /dev/null -w "%{http_code}" -X POST http://localhost:8000/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username":"dragarcia","password":"mal"}'
```

Resultados esperados: 201 en creación, 200 con datos del médico en login correcto, `401` en login incorrecto.

- [ ] **Step 6: Commit**

```bash
git add backend/schemas/auth.py backend/services/auth.py backend/routers/auth.py backend/main.py
git commit -m "feat: endpoint POST /auth/login para médicos"
```

---

## Task 3: Backend — PATCH /ingresos/{id}/observaciones

**Files:**
- Modify: `backend/schemas/ingreso_guardia.py`
- Modify: `backend/services/ingreso_guardia.py`
- Modify: `backend/routers/ingreso_guardia.py`

- [ ] **Step 1: Agregar `ActualizarObservacionesRequest` en `backend/schemas/ingreso_guardia.py`**

Agregar al final del archivo (no modificar los schemas existentes):

```python
class ActualizarObservacionesRequest(BaseModel):
    observaciones: Optional[str] = None
```

El import de `Optional` ya existe en el archivo.

- [ ] **Step 2: Agregar `actualizar_observaciones` en `backend/services/ingreso_guardia.py`**

Agregar al final del archivo:

```python
def actualizar_observaciones(db: Session, ingreso_id: int, observaciones: Optional[str]) -> IngresoGuardia:
    ingreso = db.get(IngresoGuardia, ingreso_id)
    if ingreso is None:
        raise LookupError(f"Ingreso con id {ingreso_id} no encontrado")
    if ingreso.estado == EstadoIngreso.ALTA:
        raise ValueError("El ingreso con estado ALTA no puede modificarse")
    ingreso.observaciones = observaciones
    db.commit()
    db.refresh(ingreso)
    return ingreso
```

- [ ] **Step 3: Agregar el endpoint en `backend/routers/ingreso_guardia.py`**

Primero, agregar `ActualizarObservacionesRequest` al import de schemas (línea 6):

```python
from schemas.ingreso_guardia import (
    IngresoGuardiaCreate,
    IngresoGuardiaResponse,
    CambioEstadoRequest,
    AsignacionMedicoRequest,
    ActualizarObservacionesRequest,
)
```

Luego agregar el endpoint al final del archivo:

```python
@router.patch("/{ingreso_id}/observaciones", response_model=IngresoGuardiaResponse)
def actualizar_observaciones(ingreso_id: int, data: ActualizarObservacionesRequest, db: Session = Depends(get_db)):
    try:
        return ingreso_service.actualizar_observaciones(db, ingreso_id, data.observaciones)
    except LookupError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
```

- [ ] **Step 4: Probar el endpoint manualmente**

Primero crear un ingreso de prueba, luego:

```bash
# Reemplazar {id} por el id del ingreso creado
curl -s -X PATCH http://localhost:8000/ingresos/1/observaciones \
  -H "Content-Type: application/json" \
  -d '{"observaciones":"Paciente refiere dolor abdominal leve"}' | python3 -m json.tool
```

Esperado: 200 con el ingreso actualizado, campo `observaciones` con el nuevo texto.

- [ ] **Step 5: Commit**

```bash
git add backend/schemas/ingreso_guardia.py backend/services/ingreso_guardia.py backend/routers/ingreso_guardia.py
git commit -m "feat: endpoint PATCH /ingresos/{id}/observaciones"
```

---

## Task 4: Frontend — servicios

**Files:**
- Create: `frontend/services/authService.js`
- Create: `frontend/services/medicoService.js`
- Modify: `frontend/services/ingresoService.js`

- [ ] **Step 1: Crear `frontend/services/authService.js`**

```js
const BASE = 'http://localhost:8000'

export async function login(username, password) {
  const res = await fetch(`${BASE}/auth/login`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ username, password }),
  })
  if (res.status === 401) throw new Error('Usuario o contraseña incorrectos')
  if (!res.ok) throw new Error('Error al iniciar sesión')
  return res.json()
}
```

- [ ] **Step 2: Crear `frontend/services/medicoService.js`**

```js
const BASE = 'http://localhost:8000'

export async function listarMedicos() {
  const res = await fetch(`${BASE}/medicos/`)
  if (!res.ok) throw new Error('Error al obtener médicos')
  return res.json()
}
```

- [ ] **Step 3: Agregar funciones a `frontend/services/ingresoService.js`**

El archivo existente tiene `crearIngreso` y `listarIngresos`. Agregar al final:

```js
export async function cambiarEstado(ingresoId, estado) {
  const res = await fetch(`${BASE}/ingresos/${ingresoId}/estado`, {
    method: 'PATCH',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ estado }),
  })
  if (!res.ok) throw new Error('Error al cambiar estado')
  return res.json()
}

export async function asignarMedico(ingresoId, medicoId) {
  const res = await fetch(`${BASE}/ingresos/${ingresoId}/medico`, {
    method: 'PATCH',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ medico_id: medicoId }),
  })
  if (!res.ok) throw new Error('Error al asignar médico')
  return res.json()
}

export async function actualizarObservaciones(ingresoId, observaciones) {
  const res = await fetch(`${BASE}/ingresos/${ingresoId}/observaciones`, {
    method: 'PATCH',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ observaciones }),
  })
  if (!res.ok) throw new Error('Error al actualizar observaciones')
  return res.json()
}
```

- [ ] **Step 4: Commit**

```bash
git add frontend/services/authService.js frontend/services/medicoService.js frontend/services/ingresoService.js
git commit -m "feat: servicios de auth, medico y nuevas funciones de ingreso"
```

---

## Task 5: Frontend — Pinia auth store

**Files:**
- Create: `frontend/stores/authStore.js`

- [ ] **Step 1: Crear `frontend/stores/authStore.js`**

```js
import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { login as loginService } from '~/services/authService'

export const useAuthStore = defineStore('auth', () => {
  const medico = ref(null)

  const estaLogueado = computed(() => medico.value !== null)

  function cargarSesion() {
    if (!process.client) return
    const stored = localStorage.getItem('medico_sesion')
    if (stored) {
      try {
        medico.value = JSON.parse(stored)
      } catch {
        medico.value = null
      }
    }
  }

  async function login(username, password) {
    const data = await loginService(username, password)
    medico.value = data
    localStorage.setItem('medico_sesion', JSON.stringify(data))
  }

  function logout() {
    medico.value = null
    localStorage.removeItem('medico_sesion')
  }

  return { medico, estaLogueado, cargarSesion, login, logout }
})
```

- [ ] **Step 2: Commit**

```bash
git add frontend/stores/authStore.js
git commit -m "feat: Pinia store de autenticación para médicos"
```

---

## Task 6: Frontend — LoginMedico component

**Files:**
- Create: `frontend/components/LoginMedico.vue`

- [ ] **Step 1: Crear `frontend/components/LoginMedico.vue`**

```vue
<template>
  <div class="d-flex align-center justify-center" style="min-height: 85vh;">
    <v-card width="380" class="pa-4">
      <div class="text-center mb-6">
        <div class="text-h6 font-weight-bold text-primary">Guardia Hospitalaria</div>
        <div class="text-body-2 text-medium-emphasis mt-1">Acceso para médicos</div>
      </div>

      <v-form @submit.prevent="onSubmit">
        <v-text-field
          v-model="username"
          label="Usuario"
          variant="outlined"
          density="comfortable"
          class="mb-3"
          autocomplete="username"
          :disabled="cargando"
        />
        <v-text-field
          v-model="password"
          label="Contraseña"
          type="password"
          variant="outlined"
          density="comfortable"
          class="mb-4"
          autocomplete="current-password"
          :disabled="cargando"
        />

        <v-alert
          v-if="error"
          type="error"
          variant="tonal"
          density="compact"
          class="mb-4"
        >
          {{ error }}
        </v-alert>

        <v-btn type="submit" color="primary" block :loading="cargando">
          Ingresar
        </v-btn>
      </v-form>
    </v-card>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { useAuthStore } from '~/stores/authStore'

const emit = defineEmits(['login-exitoso'])

const authStore = useAuthStore()

const username = ref('')
const password = ref('')
const cargando = ref(false)
const error = ref('')

async function onSubmit() {
  if (!username.value || !password.value) return
  error.value = ''
  cargando.value = true
  try {
    await authStore.login(username.value, password.value)
    emit('login-exitoso')
  } catch (e) {
    error.value = e.message
  } finally {
    cargando.value = false
  }
}
</script>
```

- [ ] **Step 2: Commit**

```bash
git add frontend/components/LoginMedico.vue
git commit -m "feat: componente LoginMedico con manejo de error inline"
```

---

## Task 7: Frontend — DialogObservaciones component

**Files:**
- Create: `frontend/components/DialogObservaciones.vue`

- [ ] **Step 1: Crear `frontend/components/DialogObservaciones.vue`**

```vue
<template>
  <v-dialog
    :model-value="modelValue"
    max-width="480"
    @update:model-value="$emit('update:modelValue', $event)"
  >
    <v-card>
      <v-card-title class="text-subtitle-1 font-weight-medium pa-4 pb-2">
        Observaciones
      </v-card-title>
      <v-card-subtitle class="px-4 pb-2">
        {{ ingreso?.paciente?.apellido }}, {{ ingreso?.paciente?.nombre }}
      </v-card-subtitle>
      <v-card-text class="pt-2">
        <v-textarea
          v-model="texto"
          variant="outlined"
          rows="4"
          placeholder="Escribí las observaciones del paciente..."
          hide-details
        />
      </v-card-text>
      <v-card-actions class="pa-4 pt-0">
        <v-spacer />
        <v-btn variant="text" @click="cerrar">Cancelar</v-btn>
        <v-btn color="primary" :loading="guardando" @click="guardar">Guardar</v-btn>
      </v-card-actions>
    </v-card>
  </v-dialog>
</template>

<script setup>
import { ref, watch } from 'vue'
import { actualizarObservaciones } from '~/services/ingresoService'

const props = defineProps({
  modelValue: Boolean,
  ingreso: Object,
})

const emit = defineEmits(['update:modelValue', 'guardado', 'error'])

const texto = ref('')
const guardando = ref(false)

watch(
  () => props.modelValue,
  (val) => {
    if (val) texto.value = props.ingreso?.observaciones ?? ''
  },
)

function cerrar() {
  emit('update:modelValue', false)
}

async function guardar() {
  guardando.value = true
  try {
    await actualizarObservaciones(props.ingreso.id, texto.value || null)
    emit('guardado')
    cerrar()
  } catch (e) {
    emit('error', e.message)
  } finally {
    guardando.value = false
  }
}
</script>
```

- [ ] **Step 2: Commit**

```bash
git add frontend/components/DialogObservaciones.vue
git commit -m "feat: componente DialogObservaciones reutilizable"
```

---

## Task 8: Frontend — TablaPacientesMedico component

**Files:**
- Create: `frontend/components/TablaPacientesMedico.vue`

- [ ] **Step 1: Crear `frontend/components/TablaPacientesMedico.vue`**

```vue
<template>
  <v-card>
    <v-card-text>
      <div class="d-flex align-center justify-space-between flex-wrap gap-3 mb-4">
        <div class="text-subtitle-1 font-weight-medium">Pacientes en guardia</div>
        <v-btn-toggle v-model="filtro" mandatory density="compact" variant="outlined" divided>
          <v-btn value="todos">Todos</v-btn>
          <v-btn value="EN_ESPERA">En espera</v-btn>
          <v-btn value="EN_ATENCION">En atención</v-btn>
        </v-btn-toggle>
      </div>

      <v-data-table
        :headers="headers"
        :items="ingresosFiltrados"
        item-value="id"
        :loading="cargando"
        no-data-text="No hay pacientes activos"
        density="compact"
        :row-props="rowProps"
      >
        <template #item.paciente_nombre="{ item }">
          {{ item.paciente.apellido }}, {{ item.paciente.nombre }}
        </template>
        <template #item.paciente_dni="{ item }">
          {{ item.paciente.dni }}
        </template>
        <template #item.prioridad="{ item }">
          <v-chip :color="colorPrioridad(item.prioridad)" size="small" variant="flat">
            {{ item.prioridad }}
          </v-chip>
        </template>
        <template #item.estado="{ item }">
          <v-chip :color="colorEstado(item.estado)" size="small" variant="flat">
            {{ etiquetaEstado(item.estado) }}
          </v-chip>
        </template>
        <template #item.fecha_ingreso="{ item }">
          {{ formatFecha(item.fecha_ingreso) }}
        </template>
        <template #item.acciones="{ item }">
          <template v-if="item.estado === 'EN_ESPERA'">
            <v-btn size="small" color="primary" variant="tonal" @click="abrirDialogTomar(item)">
              Tomar
            </v-btn>
          </template>
          <template v-else-if="item.estado === 'EN_ATENCION'">
            <div class="d-flex gap-2">
              <v-btn size="small" color="secondary" variant="tonal" @click="abrirDialogObservaciones(item)">
                Obs.
              </v-btn>
              <v-btn size="small" color="success" variant="tonal" @click="abrirDialogAlta(item)">
                Alta
              </v-btn>
            </div>
          </template>
        </template>
      </v-data-table>
    </v-card-text>
  </v-card>

  <!-- Dialog: Tomar -->
  <v-dialog v-model="dialogTomar" max-width="400">
    <v-card>
      <v-card-title class="text-subtitle-1 font-weight-medium pa-4 pb-2">Tomar paciente</v-card-title>
      <v-card-text>
        ¿Confirmás que vas a atender a
        <strong>{{ ingresoSeleccionado?.paciente?.apellido }}, {{ ingresoSeleccionado?.paciente?.nombre }}</strong>?
      </v-card-text>
      <v-card-actions class="pa-4 pt-0">
        <v-spacer />
        <v-btn variant="text" @click="dialogTomar = false">Cancelar</v-btn>
        <v-btn color="primary" :loading="procesando" @click="confirmarTomar">Confirmar</v-btn>
      </v-card-actions>
    </v-card>
  </v-dialog>

  <!-- Dialog: Alta -->
  <v-dialog v-model="dialogAlta" max-width="480">
    <v-card>
      <v-card-title class="text-subtitle-1 font-weight-medium pa-4 pb-2">Dar alta</v-card-title>
      <v-card-subtitle class="px-4 pb-2">
        {{ ingresoSeleccionado?.paciente?.apellido }}, {{ ingresoSeleccionado?.paciente?.nombre }}
      </v-card-subtitle>
      <v-card-text class="pt-2">
        <div class="text-body-2 text-medium-emphasis mb-2">Observaciones finales (opcional)</div>
        <v-textarea
          v-model="textoAltaObs"
          variant="outlined"
          rows="3"
          placeholder="Observaciones del alta..."
          hide-details
        />
      </v-card-text>
      <v-card-actions class="pa-4 pt-0">
        <v-spacer />
        <v-btn variant="text" @click="dialogAlta = false">Cancelar</v-btn>
        <v-btn color="success" :loading="procesando" @click="confirmarAlta">Confirmar alta</v-btn>
      </v-card-actions>
    </v-card>
  </v-dialog>

  <!-- Dialog: Observaciones -->
  <DialogObservaciones
    v-model="dialogObservaciones"
    :ingreso="ingresoSeleccionado"
    @guardado="onObservacionesGuardadas"
    @error="emit('error', $event)"
  />
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { listarIngresos, cambiarEstado, asignarMedico, actualizarObservaciones } from '~/services/ingresoService'

const props = defineProps({
  medicoId: { type: Number, required: true },
})
const emit = defineEmits(['error'])

const cargando = ref(false)
const procesando = ref(false)
const ingresos = ref([])
const filtro = ref('todos')
const ingresoSeleccionado = ref(null)
const dialogTomar = ref(false)
const dialogAlta = ref(false)
const dialogObservaciones = ref(false)
const textoAltaObs = ref('')

const headers = [
  { title: 'Paciente', key: 'paciente_nombre', sortable: false },
  { title: 'DNI', key: 'paciente_dni', sortable: false },
  { title: 'Prioridad', key: 'prioridad', sortable: false },
  { title: 'Estado', key: 'estado', sortable: false },
  { title: 'Ingreso', key: 'fecha_ingreso', sortable: false },
  { title: 'Acciones', key: 'acciones', sortable: false },
]

const ingresosFiltrados = computed(() => {
  const activos = ingresos.value.filter((i) => i.estado !== 'ALTA')
  if (filtro.value === 'todos') return activos
  return activos.filter((i) => i.estado === filtro.value)
})

function rowProps({ item }) {
  if (item.estado === 'EN_ESPERA') return { class: 'fila-espera' }
  if (item.estado === 'EN_ATENCION') return { class: 'fila-atencion' }
  return {}
}

function colorPrioridad(p) {
  return { BAJA: 'success', MEDIA: 'warning', ALTA: 'error' }[p] ?? 'grey'
}

function colorEstado(e) {
  return { EN_ESPERA: 'info', EN_ATENCION: 'amber' }[e] ?? 'grey'
}

function etiquetaEstado(e) {
  return { EN_ESPERA: 'En espera', EN_ATENCION: 'En atención' }[e] ?? e
}

function formatFecha(iso) {
  const d = new Date(iso)
  const dd = String(d.getDate()).padStart(2, '0')
  const mm = String(d.getMonth() + 1).padStart(2, '0')
  const hh = String(d.getHours()).padStart(2, '0')
  const mi = String(d.getMinutes()).padStart(2, '0')
  return `${dd}/${mm} ${hh}:${mi}`
}

async function cargarIngresos() {
  cargando.value = true
  try {
    ingresos.value = await listarIngresos()
  } catch {
    emit('error', 'Error al cargar pacientes.')
  } finally {
    cargando.value = false
  }
}

function abrirDialogTomar(ingreso) {
  ingresoSeleccionado.value = ingreso
  dialogTomar.value = true
}

function abrirDialogObservaciones(ingreso) {
  ingresoSeleccionado.value = ingreso
  dialogObservaciones.value = true
}

function abrirDialogAlta(ingreso) {
  ingresoSeleccionado.value = ingreso
  textoAltaObs.value = ingreso.observaciones ?? ''
  dialogAlta.value = true
}

async function confirmarTomar() {
  procesando.value = true
  try {
    await asignarMedico(ingresoSeleccionado.value.id, props.medicoId)
    await cambiarEstado(ingresoSeleccionado.value.id, 'EN_ATENCION')
    dialogTomar.value = false
    await cargarIngresos()
  } catch {
    emit('error', 'Error al tomar el paciente.')
  } finally {
    procesando.value = false
  }
}

async function confirmarAlta() {
  procesando.value = true
  try {
    await actualizarObservaciones(ingresoSeleccionado.value.id, textoAltaObs.value || null)
    await cambiarEstado(ingresoSeleccionado.value.id, 'ALTA')
    dialogAlta.value = false
    await cargarIngresos()
  } catch {
    emit('error', 'Error al dar el alta.')
  } finally {
    procesando.value = false
  }
}

async function onObservacionesGuardadas() {
  await cargarIngresos()
}

defineExpose({ recargar: cargarIngresos })
onMounted(cargarIngresos)
</script>

<style scoped>
:deep(.fila-espera td) { background: #fffde7; }
:deep(.fila-atencion td) { background: #f1f8e9; }
</style>
```

- [ ] **Step 2: Commit**

```bash
git add frontend/components/TablaPacientesMedico.vue
git commit -m "feat: TablaPacientesMedico con filtro, colores por estado y dialogs de acción"
```

---

## Task 9: Frontend — página medico.vue

**Files:**
- Create: `frontend/pages/medico.vue`

- [ ] **Step 1: Crear `frontend/pages/medico.vue`**

```vue
<template>
  <div>
    <LoginMedico v-if="!authStore.estaLogueado" @login-exitoso="actualizarSidebar" />

    <v-container v-else class="py-6" style="max-width: 1100px">
      <div class="d-flex align-center justify-space-between mb-6">
        <div class="text-h5 font-weight-medium">Médico</div>
        <v-chip color="primary" variant="tonal">
          Dr/a. {{ authStore.medico?.apellido }}, {{ authStore.medico?.nombre }}
        </v-chip>
      </div>

      <TablaPacientesMedico
        ref="tablaRef"
        :medico-id="authStore.medico.id"
        @error="mostrarError"
      />
    </v-container>

    <v-snackbar
      v-model="snackbar.visible"
      :color="snackbar.color"
      :timeout="3500"
      location="bottom right"
    >
      {{ snackbar.mensaje }}
    </v-snackbar>
  </div>
</template>

<script setup>
import { ref, watch, onMounted, onUnmounted } from 'vue'
import { useAuthStore } from '~/stores/authStore'
import { useSidebarItems } from '~/composables/useSidebarItems'

const authStore = useAuthStore()
const { items } = useSidebarItems()
const tablaRef = ref(null)
const snackbar = ref({ visible: false, mensaje: '', color: 'error' })

function mostrarError(msg) {
  snackbar.value = { visible: true, mensaje: msg, color: 'error' }
}

function actualizarSidebar() {
  if (authStore.estaLogueado) {
    items.value = [
      {
        label: 'Pacientes activos',
        icon: 'mdi-clipboard-pulse',
        onClick: () => tablaRef.value?.recargar(),
      },
      {
        label: 'Cerrar sesión',
        icon: 'mdi-logout',
        onClick: () => authStore.logout(),
      },
    ]
  } else {
    items.value = []
  }
}

watch(() => authStore.estaLogueado, actualizarSidebar)

onMounted(() => {
  authStore.cargarSesion()
  actualizarSidebar()
})

onUnmounted(() => {
  items.value = []
})
</script>
```

- [ ] **Step 2: Verificar el flujo completo en el navegador**

Con backend (`uvicorn main:app --reload`) y frontend (`npm run dev`) corriendo:

1. Abrir `http://localhost:3000/medico` (o 3001 si 3000 está ocupado)
2. Verificar que aparece el formulario de login
3. Ingresar con usuario `dragarcia` / contraseña `clave123` (creado en Task 2, Step 5)
4. Verificar que aparece la tabla de pacientes y el nombre del médico en el chip
5. Verificar que el sidebar muestra "Pacientes activos" y "Cerrar sesión"
6. Desde `/recepcion`, registrar un ingreso y verificar que aparece en la tabla de `/medico`
7. Clic en "Tomar" → confirmar → verificar que la fila cambia a verde y estado "En atención"
8. Clic en "Obs." → escribir texto → guardar → reabrir dialog y verificar que el texto persistió
9. Clic en "Alta" → confirmar → verificar que la fila desaparece de la tabla
10. Clic en "Cerrar sesión" → verificar que vuelve al login
11. Refrescar la página sin cerrar sesión → verificar que no pide login de nuevo

- [ ] **Step 3: Commit**

```bash
git add frontend/pages/medico.vue
git commit -m "feat: página /medico con autenticación y tabla de pacientes"
```
