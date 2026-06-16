# Observaciones del médico — Plan de implementación

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Separar las observaciones de recepción de las del médico: el campo `observaciones` existente queda para recepción, y se agrega `observaciones_medico` para el médico, con su propio endpoint y un dialog reestructurado.

**Architecture:** Nueva columna `observaciones_medico` en `IngresoGuardia`. Endpoint dedicado `PATCH /ingresos/{id}/observaciones-medico`. El `DialogObservaciones.vue` muestra las de recepción en read-only y las del médico en un textarea editable.

**Tech Stack:** FastAPI, SQLAlchemy, SQLite, Nuxt 3, Vue 3, Vuetify 3.

---

## Archivos a modificar

| Archivo | Cambio |
|---|---|
| `backend/models/ingreso_guardia.py` | Agregar columna `observaciones_medico` |
| `backend/schemas/ingreso_guardia.py` | Agregar campo en response + nuevo request schema |
| `backend/services/ingreso_guardia.py` | Agregar función `actualizar_observaciones_medico` |
| `backend/routers/ingreso_guardia.py` | Agregar endpoint + import nuevo schema |
| `backend/tests/test_ingreso_guardia_endpoints.py` | Agregar 4 tests nuevos |
| `frontend/services/ingresoService.js` | Agregar función `actualizarObservacionesMedico` |
| `frontend/components/DialogObservaciones.vue` | Reestructurar: read-only recepción + editable médico |

---

## Task 1: Backend — modelo, schema, service, endpoint y tests

**Archivos:**
- Modificar: `backend/models/ingreso_guardia.py`
- Modificar: `backend/schemas/ingreso_guardia.py`
- Modificar: `backend/services/ingreso_guardia.py`
- Modificar: `backend/routers/ingreso_guardia.py`
- Modificar: `backend/tests/test_ingreso_guardia_endpoints.py`

Todo el backend en una tarea porque los tests cubren modelo + service + endpoint juntos (no hay capa intermedia testeable en aislamiento sin un cliente HTTP).

- [ ] **Step 1: Agregar columna al modelo**

En `backend/models/ingreso_guardia.py`, agregar después de la línea `observaciones = Column(Text, nullable=True)`:

```python
observaciones_medico = Column(Text, nullable=True)
```

El archivo queda así en la sección de columnas de `IngresoGuardia`:

```python
observaciones = Column(Text, nullable=True)
observaciones_medico = Column(Text, nullable=True)
```

- [ ] **Step 2: Actualizar schemas**

En `backend/schemas/ingreso_guardia.py`:

2a. En `IngresoGuardiaResponse`, agregar después de `observaciones: Optional[str] = None`:

```python
observaciones_medico: Optional[str] = None
```

2b. Al final del archivo, agregar el nuevo request schema:

```python
class ActualizarObservacionesMedicoRequest(BaseModel):
    observaciones_medico: Optional[str] = None
```

El archivo completo queda:

```python
from datetime import datetime
from typing import Optional
from pydantic import BaseModel, ConfigDict
from models.ingreso_guardia import EstadoIngreso, Prioridad
from schemas.paciente import PacienteResponse
from schemas.medico import MedicoResponse


class IngresoGuardiaCreate(BaseModel):
    paciente_id: int
    prioridad: Prioridad
    observaciones: Optional[str] = None


class CambioEstadoRequest(BaseModel):
    estado: EstadoIngreso


class AsignacionMedicoRequest(BaseModel):
    medico_id: int


class IngresoGuardiaResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    paciente_id: int
    medico_id: Optional[int] = None
    estado: EstadoIngreso
    prioridad: Prioridad
    fecha_ingreso: datetime
    observaciones: Optional[str] = None
    observaciones_medico: Optional[str] = None
    paciente: PacienteResponse
    medico: Optional[MedicoResponse] = None


class ActualizarObservacionesRequest(BaseModel):
    observaciones: Optional[str] = None


class ActualizarObservacionesMedicoRequest(BaseModel):
    observaciones_medico: Optional[str] = None
```

- [ ] **Step 3: Escribir los tests que van a fallar**

Al final de `backend/tests/test_ingreso_guardia_endpoints.py`, agregar:

```python
# --- PATCH /ingresos/{id}/observaciones-medico ---

def test_actualizar_observaciones_medico_ok(client, ingreso_id):
    client.patch(f"/ingresos/{ingreso_id}/estado", json={"estado": "EN_ATENCION"})
    response = client.patch(
        f"/ingresos/{ingreso_id}/observaciones-medico",
        json={"observaciones_medico": "Paciente con fiebre alta"},
    )
    assert response.status_code == 200
    assert response.json()["observaciones_medico"] == "Paciente con fiebre alta"


def test_actualizar_observaciones_medico_no_modifica_observaciones_recepcion(client, paciente_id):
    ingreso = client.post(
        "/ingresos/",
        json={"paciente_id": paciente_id, "prioridad": "ALTA", "observaciones": "Dolor en el pecho"},
    ).json()
    client.patch(f"/ingresos/{ingreso['id']}/estado", json={"estado": "EN_ATENCION"})
    client.patch(
        f"/ingresos/{ingreso['id']}/observaciones-medico",
        json={"observaciones_medico": "Presión alta"},
    )
    data = client.get("/ingresos/").json()
    actualizado = next(i for i in data if i["id"] == ingreso["id"])
    assert actualizado["observaciones"] == "Dolor en el pecho"
    assert actualizado["observaciones_medico"] == "Presión alta"


def test_actualizar_observaciones_medico_en_alta_retorna_400(client, ingreso_id):
    client.patch(f"/ingresos/{ingreso_id}/estado", json={"estado": "EN_ATENCION"})
    client.patch(f"/ingresos/{ingreso_id}/estado", json={"estado": "ALTA"})
    response = client.patch(
        f"/ingresos/{ingreso_id}/observaciones-medico",
        json={"observaciones_medico": "Obs tardía"},
    )
    assert response.status_code == 400


def test_actualizar_observaciones_medico_ingreso_inexistente_retorna_404(client):
    response = client.patch(
        "/ingresos/9999/observaciones-medico",
        json={"observaciones_medico": "Obs"},
    )
    assert response.status_code == 404
```

- [ ] **Step 4: Verificar que los tests fallan**

```bash
cd backend
python -m pytest tests/test_ingreso_guardia_endpoints.py -k "observaciones_medico" -v
```

Esperado: 4 tests en FAILED (404 Not Found — el endpoint no existe todavía).

- [ ] **Step 5: Implementar el service**

En `backend/services/ingreso_guardia.py`, agregar al final:

```python
def actualizar_observaciones_medico(db: Session, ingreso_id: int, observaciones_medico: Optional[str]) -> IngresoGuardia:
    ingreso = db.get(IngresoGuardia, ingreso_id)
    if ingreso is None:
        raise LookupError(f"Ingreso con id {ingreso_id} no encontrado")
    if ingreso.estado == EstadoIngreso.ALTA:
        raise ValueError("El ingreso con estado ALTA no puede modificarse")
    ingreso.observaciones_medico = observaciones_medico
    db.commit()
    db.refresh(ingreso)
    return ingreso
```

- [ ] **Step 6: Agregar el endpoint al router**

En `backend/routers/ingreso_guardia.py`:

6a. Actualizar el bloque de imports del schema para incluir `ActualizarObservacionesMedicoRequest`:

```python
from schemas.ingreso_guardia import (
    IngresoGuardiaCreate,
    IngresoGuardiaResponse,
    CambioEstadoRequest,
    AsignacionMedicoRequest,
    ActualizarObservacionesRequest,
    ActualizarObservacionesMedicoRequest,
)
```

6b. Al final del archivo, agregar:

```python
@router.patch("/{ingreso_id}/observaciones-medico", response_model=IngresoGuardiaResponse)
def actualizar_observaciones_medico(ingreso_id: int, data: ActualizarObservacionesMedicoRequest, db: Session = Depends(get_db)):
    try:
        return ingreso_service.actualizar_observaciones_medico(db, ingreso_id, data.observaciones_medico)
    except LookupError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
```

- [ ] **Step 7: Verificar que todos los tests pasan**

```bash
cd backend
python -m pytest --tb=short -q
```

Esperado: todos los tests existentes más los 4 nuevos en PASSED.

- [ ] **Step 8: Commit**

```bash
git add backend/models/ingreso_guardia.py backend/schemas/ingreso_guardia.py backend/services/ingreso_guardia.py backend/routers/ingreso_guardia.py backend/tests/test_ingreso_guardia_endpoints.py
git commit -m "feat: campo observaciones_medico y endpoint PATCH /ingresos/{id}/observaciones-medico"
```

---

## Task 2: Frontend — actualizarObservacionesMedico en ingresoService.js

**Archivos:**
- Modificar: `frontend/services/ingresoService.js`

- [ ] **Step 1: Agregar función al servicio**

En `frontend/services/ingresoService.js`, agregar al final:

```js
export async function actualizarObservacionesMedico(ingresoId, observaciones) {
  const res = await fetch(`${BASE}/ingresos/${ingresoId}/observaciones-medico`, {
    method: 'PATCH',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ observaciones_medico: observaciones || null }),
  })
  if (!res.ok) throw new Error('Error al guardar observaciones del médico')
  return res.json()
}
```

- [ ] **Step 2: Verificar que el archivo compila sin errores**

```bash
cd frontend
node --input-type=module <<'EOF'
import { actualizarObservacionesMedico } from './services/ingresoService.js'
console.log(typeof actualizarObservacionesMedico)
EOF
```

Esperado: `function`

- [ ] **Step 3: Commit**

```bash
git add frontend/services/ingresoService.js
git commit -m "feat: función actualizarObservacionesMedico en ingresoService"
```

---

## Task 3: Frontend — DialogObservaciones.vue

**Archivos:**
- Modificar: `frontend/components/DialogObservaciones.vue`

El componente actual usa `actualizarObservaciones` y pre-llena un solo textarea con `props.ingreso?.observaciones`. Hay que reestructurarlo para mostrar las de recepción en read-only arriba y las del médico en un textarea editable abajo.

- [ ] **Step 1: Reemplazar el contenido del componente**

Reemplazar `frontend/components/DialogObservaciones.vue` completo con:

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
        <div class="text-caption text-medium-emphasis mb-1">Observaciones de recepción</div>
        <div
          class="text-body-2 mb-4 pa-3 rounded"
          style="min-height: 48px; background: rgba(var(--v-theme-surface-variant), 1)"
        >
          {{ ingreso?.observaciones || 'Sin observaciones de recepción' }}
        </div>

        <div class="text-caption text-medium-emphasis mb-1">Observaciones del médico</div>
        <v-textarea
          v-model="textoMedico"
          variant="outlined"
          rows="4"
          placeholder="Escribí tus observaciones..."
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
import { actualizarObservacionesMedico } from '~/services/ingresoService'

const props = defineProps({
  modelValue: Boolean,
  ingreso: Object,
})

const emit = defineEmits(['update:modelValue', 'guardado', 'error'])

const textoMedico = ref('')
const guardando = ref(false)

watch(
  () => props.modelValue,
  (val) => {
    if (val) textoMedico.value = props.ingreso?.observaciones_medico ?? ''
  },
)

function cerrar() {
  emit('update:modelValue', false)
}

async function guardar() {
  if (!props.ingreso) return
  guardando.value = true
  try {
    await actualizarObservacionesMedico(props.ingreso.id, textoMedico.value || null)
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

- [ ] **Step 2: Verificar en el navegador**

Con el backend corriendo (`cd backend && uvicorn main:app --reload`) y el frontend corriendo (`cd frontend && npm run dev`):

1. Ir a `/admin` y verificar que hay al menos un médico registrado.
2. Ir a `/recepcion/nuevo`, registrar un paciente nuevo con observaciones de recepción (ej: "Dolor abdominal").
3. Ir a `/medico`, iniciar sesión.
4. Tomar el paciente (cambiar estado a EN_ATENCION).
5. Abrir el dialog de observaciones.
6. Verificar que se muestran "Dolor abdominal" en la sección de recepción (read-only).
7. Escribir observaciones del médico y guardar.
8. Verificar que al reabrir el dialog las observaciones del médico están guardadas y las de recepción no cambiaron.

- [ ] **Step 3: Commit**

```bash
git add frontend/components/DialogObservaciones.vue
git commit -m "feat: DialogObservaciones muestra obs de recepción en read-only y obs del médico editables"
```
