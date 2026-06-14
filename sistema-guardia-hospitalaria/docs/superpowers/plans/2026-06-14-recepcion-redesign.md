# Rediseño Vista Recepción — Plan de Implementación

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Separar la vista `/recepcion` en tres rutas independientes con navegación por sidebar y agregar búsqueda parcial de pacientes.

**Architecture:** Tres páginas Nuxt (`buscar.vue`, `nuevo.vue`, `activos.vue`) bajo `pages/recepcion/`. Cada página registra los mismos tres ítems de sidebar via `useSidebarItems` usando `to` (ruta) en lugar de `onClick`. El layout `default.vue` soporta ambos con `:to="item.to || undefined"` y `@click="item.onClick && item.onClick()"`. El backend expone `GET /pacientes/?q=` para búsqueda parcial case-insensitive sobre DNI, nombre y apellido.

**Tech Stack:** FastAPI + SQLAlchemy + SQLite (backend), Nuxt 3 + Vue 3 + Vuetify 3 (frontend)

---

## File Map

| Archivo | Acción | Responsabilidad |
|---|---|---|
| `backend/services/paciente.py` | Modificar | Agregar `buscar_pacientes(db, q)` con `ilike` + `or_` |
| `backend/routers/paciente.py` | Modificar | Agregar `q: Optional[str]` a `GET /pacientes/` |
| `backend/tests/test_paciente_endpoints.py` | Modificar | 5 tests nuevos para búsqueda parcial |
| `frontend/services/pacienteService.js` | Modificar | Agregar `buscarPacientes(q)` |
| `frontend/layouts/default.vue` | Modificar | Soporte `:to` en `v-list-item` del sidebar |
| `frontend/components/TablaIngresosActivos.vue` | Modificar | Prop `busqueda` que filtra `ingresosFiltrados` |
| `frontend/pages/recepcion/index.vue` | Crear | Redirect a `/recepcion/buscar` |
| `frontend/pages/recepcion/buscar.vue` | Crear | Búsqueda parcial → seleccionar → FormularioIngreso |
| `frontend/pages/recepcion/nuevo.vue` | Crear | FormularioPaciente → FormularioIngreso |
| `frontend/pages/recepcion/activos.vue` | Crear | Filtro de texto + TablaIngresosActivos |
| `frontend/pages/recepcion.vue` | Eliminar | Reemplazada por las páginas anteriores |

---

## Task 1: Backend — búsqueda parcial de pacientes

**Files:**
- Modify: `backend/services/paciente.py`
- Modify: `backend/routers/paciente.py`
- Modify: `backend/tests/test_paciente_endpoints.py`

- [ ] **Step 1: Escribir los tests que fallarán**

Agregar al final de `backend/tests/test_paciente_endpoints.py`:

```python
def test_buscar_pacientes_por_nombre(client):
    client.post("/pacientes/", json=PACIENTE_DATA)          # Juan Pérez
    client.post("/pacientes/", json=PACIENTE_SIN_TELEFONO)  # María García
    response = client.get("/pacientes/?q=juan")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert data[0]["nombre"] == "Juan"


def test_buscar_pacientes_por_apellido(client):
    client.post("/pacientes/", json=PACIENTE_DATA)
    client.post("/pacientes/", json=PACIENTE_SIN_TELEFONO)
    response = client.get("/pacientes/?q=garc")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert data[0]["apellido"] == "García"


def test_buscar_pacientes_por_dni_parcial(client):
    client.post("/pacientes/", json=PACIENTE_DATA)          # DNI 12345678
    client.post("/pacientes/", json=PACIENTE_SIN_TELEFONO)  # DNI 87654321
    response = client.get("/pacientes/?q=1234")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert data[0]["dni"] == "12345678"


def test_buscar_pacientes_sin_resultados(client):
    client.post("/pacientes/", json=PACIENTE_DATA)
    response = client.get("/pacientes/?q=xyz_no_existe")
    assert response.status_code == 200
    assert response.json() == []


def test_buscar_pacientes_q_vacio_retorna_lista_vacia(client):
    client.post("/pacientes/", json=PACIENTE_DATA)
    response = client.get("/pacientes/?q=")
    assert response.status_code == 200
    assert response.json() == []
```

- [ ] **Step 2: Verificar que los tests fallan**

```bash
cd backend
pytest tests/test_paciente_endpoints.py -k "buscar" -v
```

Esperado: 5 FAILED (el endpoint actual no acepta `q`)

- [ ] **Step 3: Implementar `buscar_pacientes` en el service**

Reemplazar el contenido de `backend/services/paciente.py`:

```python
from typing import List, Optional
from sqlalchemy import or_
from sqlalchemy.orm import Session
from models.paciente import Paciente
from schemas.paciente import PacienteCreate


def crear_paciente(db: Session, data: PacienteCreate) -> Paciente:
    if db.query(Paciente).filter(Paciente.dni == data.dni).first():
        raise ValueError(f"Ya existe un paciente con DNI {data.dni}")
    paciente = Paciente(**data.model_dump())
    db.add(paciente)
    db.commit()
    db.refresh(paciente)
    return paciente


def obtener_pacientes(db: Session) -> List[Paciente]:
    return db.query(Paciente).all()


def obtener_paciente_por_dni(db: Session, dni: str) -> Optional[Paciente]:
    return db.query(Paciente).filter(Paciente.dni == dni).first()


def buscar_pacientes(db: Session, q: str) -> List[Paciente]:
    if not q or not q.strip():
        return []
    term = f"%{q.strip()}%"
    return (
        db.query(Paciente)
        .filter(
            or_(
                Paciente.dni.ilike(term),
                Paciente.nombre.ilike(term),
                Paciente.apellido.ilike(term),
            )
        )
        .order_by(Paciente.apellido, Paciente.nombre)
        .all()
    )
```

- [ ] **Step 4: Agregar `q` al endpoint `GET /pacientes/`**

Reemplazar el contenido de `backend/routers/paciente.py`:

```python
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from dependencies import get_db
from schemas.paciente import PacienteCreate, PacienteResponse
from services import paciente as paciente_service

router = APIRouter(prefix="/pacientes", tags=["pacientes"])


@router.post("/", response_model=PacienteResponse, status_code=status.HTTP_201_CREATED)
def crear_paciente(data: PacienteCreate, db: Session = Depends(get_db)):
    try:
        return paciente_service.crear_paciente(db, data)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(e))


@router.get("/", response_model=List[PacienteResponse])
def listar_pacientes(q: Optional[str] = None, db: Session = Depends(get_db)):
    if q:
        return paciente_service.buscar_pacientes(db, q)
    return paciente_service.obtener_pacientes(db)


@router.get("/{dni}", response_model=PacienteResponse)
def obtener_paciente(dni: str, db: Session = Depends(get_db)):
    paciente = paciente_service.obtener_paciente_por_dni(db, dni)
    if paciente is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Paciente con DNI {dni} no encontrado",
        )
    return paciente
```

- [ ] **Step 5: Verificar que todos los tests pasan**

```bash
cd backend
pytest tests/test_paciente_endpoints.py -v
```

Esperado: 13 PASSED (8 originales + 5 nuevos)

- [ ] **Step 6: Commit**

```bash
git add backend/services/paciente.py backend/routers/paciente.py backend/tests/test_paciente_endpoints.py
git commit -m "feat: búsqueda parcial de pacientes por DNI, nombre y apellido"
```

---

## Task 2: Frontend — `buscarPacientes()` en `pacienteService.js`

**Files:**
- Modify: `frontend/services/pacienteService.js`

- [ ] **Step 1: Agregar la función `buscarPacientes`**

Reemplazar el contenido de `frontend/services/pacienteService.js`:

```js
const BASE = 'http://localhost:8000'

export async function buscarPacientePorDni(dni) {
  const res = await fetch(`${BASE}/pacientes/${dni}`)
  if (res.status === 404) return null
  if (!res.ok) throw new Error('Error al buscar paciente')
  return res.json()
}

export async function crearPaciente(data) {
  const res = await fetch(`${BASE}/pacientes/`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(data),
  })
  if (res.status === 409) throw new Error('Ya existe un paciente con ese DNI')
  if (!res.ok) throw new Error('Error al registrar paciente')
  return res.json()
}

export async function buscarPacientes(q) {
  const res = await fetch(`${BASE}/pacientes/?q=${encodeURIComponent(q)}`)
  if (!res.ok) throw new Error('Error al buscar pacientes')
  return res.json()
}
```

- [ ] **Step 2: Commit**

```bash
git add frontend/services/pacienteService.js
git commit -m "feat: función buscarPacientes en pacienteService"
```

---

## Task 3: Frontend — soporte `to` en sidebar del layout

**Files:**
- Modify: `frontend/layouts/default.vue`

Cuando un ítem tiene `to`, Vuetify renderiza el `v-list-item` como `RouterLink` y aplica el resaltado activo automáticamente via Vue Router. Cuando tiene `onClick`, el handler manual sigue funcionando (compatibilidad con `/medico`).

- [ ] **Step 1: Modificar `default.vue`**

Reemplazar el contenido de `frontend/layouts/default.vue`:

```vue
<template>
  <v-app>
    <v-navigation-drawer permanent width="220" color="primary">
      <div class="pa-4 pb-3">
        <div class="text-subtitle-2 font-weight-bold text-white opacity-90">
          Guardia Hospitalaria
        </div>
      </div>
      <v-divider color="rgba(255,255,255,0.25)" />
      <v-list nav density="compact" class="mt-2" bg-color="transparent">
        <v-list-item
          v-for="item in sidebarItems"
          :key="item.label"
          :prepend-icon="item.icon"
          :title="item.label"
          rounded="lg"
          base-color="white"
          :to="item.to || undefined"
          @click="item.onClick && item.onClick()"
        />
      </v-list>
    </v-navigation-drawer>

    <v-main>
      <slot />
    </v-main>
  </v-app>
</template>

<script setup>
import { useSidebarItems } from '~/composables/useSidebarItems'

const { items: sidebarItems } = useSidebarItems()
</script>
```

- [ ] **Step 2: Commit**

```bash
git add frontend/layouts/default.vue
git commit -m "feat: soporte de campo to en ítems del sidebar para navegación por ruta"
```

---

## Task 4: Frontend — prop `busqueda` en `TablaIngresosActivos.vue`

**Files:**
- Modify: `frontend/components/TablaIngresosActivos.vue`

Se agrega la prop `busqueda` (string, default `''`). El computed `ingresosFiltrados` aplica un filtro adicional de texto sobre `paciente.nombre`, `paciente.apellido` y `paciente.dni` cuando `busqueda` no está vacío.

- [ ] **Step 1: Modificar `TablaIngresosActivos.vue`**

Reemplazar el contenido de `frontend/components/TablaIngresosActivos.vue`:

```vue
<template>
  <v-card ref="rootRef">
    <v-card-text>
      <div class="d-flex align-center justify-space-between flex-wrap gap-3 mb-4">
        <div class="text-subtitle-1 font-weight-medium">Pacientes activos en guardia</div>
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
        <template #item.medico_nombre="{ item }">
          {{ item.medico ? `${item.medico.apellido}, ${item.medico.nombre}` : '—' }}
        </template>
      </v-data-table>
    </v-card-text>
  </v-card>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { listarIngresos } from '~/services/ingresoService'

const props = defineProps({
  busqueda: { type: String, default: '' },
})

const emit = defineEmits(['error'])

const rootRef = ref(null)
const cargando = ref(false)
const ingresos = ref([])
const filtro = ref('todos')

const headers = [
  { title: 'Paciente', key: 'paciente_nombre', sortable: false },
  { title: 'DNI', key: 'paciente_dni', sortable: false },
  { title: 'Prioridad', key: 'prioridad', sortable: false },
  { title: 'Estado', key: 'estado', sortable: false },
  { title: 'Ingreso', key: 'fecha_ingreso', sortable: false },
  { title: 'Médico', key: 'medico_nombre', sortable: false },
]

const ingresosFiltrados = computed(() => {
  const activos = ingresos.value.filter((i) => i.estado !== 'ALTA')
  let filtrados = filtro.value === 'todos' ? activos : activos.filter((i) => i.estado === filtro.value)
  if (props.busqueda.trim()) {
    const term = props.busqueda.trim().toLowerCase()
    filtrados = filtrados.filter(
      (i) =>
        i.paciente.nombre.toLowerCase().includes(term) ||
        i.paciente.apellido.toLowerCase().includes(term) ||
        i.paciente.dni.toLowerCase().includes(term),
    )
  }
  return filtrados
})

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
    emit('error', 'Error al cargar pacientes activos.')
  } finally {
    cargando.value = false
  }
}

defineExpose({
  recargar: cargarIngresos,
  scrollIntoView: () => rootRef.value?.$el?.scrollIntoView({ behavior: 'smooth' }),
})

onMounted(cargarIngresos)
</script>
```

- [ ] **Step 2: Commit**

```bash
git add frontend/components/TablaIngresosActivos.vue
git commit -m "feat: prop busqueda en TablaIngresosActivos para filtrar por nombre/apellido/DNI"
```

---

## Task 5: Reestructurar rutas — `index.vue` + eliminar `recepcion.vue`

**Files:**
- Create: `frontend/pages/recepcion/index.vue`
- Delete: `frontend/pages/recepcion.vue`

En Nuxt 3, si coexisten `pages/recepcion.vue` y `pages/recepcion/buscar.vue`, Nuxt trata `recepcion.vue` como layout padre de las sub-páginas y espera un `<NuxtPage />` interno. Hay que eliminar `recepcion.vue` para que las sub-páginas funcionen correctamente como rutas independientes.

- [ ] **Step 1: Crear `pages/recepcion/index.vue`**

Crear el archivo `frontend/pages/recepcion/index.vue` con:

```vue
<script setup>
await navigateTo('/recepcion/buscar', { replace: true })
</script>
```

- [ ] **Step 2: Eliminar `pages/recepcion.vue`**

```bash
git rm frontend/pages/recepcion.vue
```

- [ ] **Step 3: Commit**

```bash
git add frontend/pages/recepcion/index.vue
git commit -m "feat: index.vue redirige a /recepcion/buscar, elimina recepcion.vue monolítica"
```

---

## Task 6: `pages/recepcion/buscar.vue`

**Files:**
- Create: `frontend/pages/recepcion/buscar.vue`

Flujo: campo de búsqueda → lista de resultados → seleccionar paciente → FormularioIngreso. "✕ cambiar" vuelve a la lista sin limpiar el campo. Al completar el ingreso, limpia todo el estado y queda listo para una nueva búsqueda. `navigateTo` y `FormularioIngreso` / `FormularioPaciente` son auto-importados por Nuxt 3.

- [ ] **Step 1: Crear `pages/recepcion/buscar.vue`**

```vue
<template>
  <v-container class="py-6" style="max-width: 960px">
    <div class="text-h5 font-weight-medium mb-6">Recepción</div>

    <v-card class="mb-4" v-if="!pacienteSeleccionado">
      <v-card-text>
        <div class="text-subtitle-1 font-weight-medium mb-4">Buscar paciente</div>
        <div class="d-flex gap-3">
          <v-text-field
            v-model="query"
            label="Nombre, apellido o DNI"
            variant="outlined"
            density="compact"
            hide-details
            @keyup.enter="buscar"
          />
          <v-btn color="primary" variant="flat" :loading="cargando" @click="buscar">
            Buscar
          </v-btn>
        </div>
      </v-card-text>
    </v-card>

    <v-card v-if="buscado && !pacienteSeleccionado" class="mb-4">
      <v-card-text>
        <template v-if="resultados.length > 0">
          <div class="text-body-2 text-medium-emphasis mb-3">
            {{ resultados.length }} resultado{{ resultados.length !== 1 ? 's' : '' }} para "{{ query }}"
          </div>
          <v-list lines="two" class="pa-0">
            <v-list-item
              v-for="p in resultados"
              :key="p.id"
              :title="`${p.apellido}, ${p.nombre}`"
              :subtitle="`DNI ${p.dni} · ${p.edad} años`"
              rounded="lg"
              class="mb-1"
              style="cursor: pointer"
              @click="seleccionarPaciente(p)"
            >
              <template #append>
                <v-icon color="primary">mdi-chevron-right</v-icon>
              </template>
            </v-list-item>
          </v-list>
        </template>
        <template v-else>
          <p class="text-body-2 mb-4">No se encontró ningún paciente para "{{ query }}".</p>
          <v-btn variant="outlined" color="primary" @click="irANuevoPaciente">
            + Registrar nuevo paciente
          </v-btn>
        </template>
      </v-card-text>
    </v-card>

    <template v-if="pacienteSeleccionado">
      <v-card class="mb-4">
        <v-card-text class="d-flex justify-space-between align-center">
          <div>
            <div class="text-caption text-primary font-weight-medium mb-1">Paciente seleccionado</div>
            <div class="text-subtitle-1 font-weight-medium">
              {{ pacienteSeleccionado.apellido }}, {{ pacienteSeleccionado.nombre }}
            </div>
            <div class="text-body-2 text-medium-emphasis">
              DNI {{ pacienteSeleccionado.dni }} · {{ pacienteSeleccionado.edad }} años
            </div>
          </div>
          <v-btn variant="text" size="small" @click="cambiarPaciente">✕ cambiar</v-btn>
        </v-card-text>
      </v-card>

      <FormularioIngreso
        :paciente-id="pacienteSeleccionado.id"
        :nombre-paciente="`${pacienteSeleccionado.apellido}, ${pacienteSeleccionado.nombre}`"
        @ingreso-creado="onIngresoCreado"
      />
    </template>

    <v-snackbar
      v-model="snackbar.visible"
      :color="snackbar.color"
      :timeout="3500"
      location="bottom right"
    >
      {{ snackbar.mensaje }}
    </v-snackbar>
  </v-container>
</template>

<script setup>
import { ref, onMounted, onUnmounted } from 'vue'
import { useSidebarItems } from '~/composables/useSidebarItems'
import { buscarPacientes } from '~/services/pacienteService'

const { items } = useSidebarItems()

const query = ref('')
const resultados = ref([])
const buscado = ref(false)
const pacienteSeleccionado = ref(null)
const cargando = ref(false)
const snackbar = ref({ visible: false, mensaje: '', color: 'error' })

const SIDEBAR_LINKS = [
  { label: 'Buscar paciente',   icon: 'mdi-magnify',        to: '/recepcion/buscar' },
  { label: 'Nuevo paciente',    icon: 'mdi-account-plus',   to: '/recepcion/nuevo' },
  { label: 'Pacientes activos', icon: 'mdi-clipboard-list', to: '/recepcion/activos' },
]

onMounted(() => { items.value = SIDEBAR_LINKS })
onUnmounted(() => { items.value = [] })

async function buscar() {
  if (!query.value.trim()) return
  cargando.value = true
  buscado.value = false
  pacienteSeleccionado.value = null
  try {
    resultados.value = await buscarPacientes(query.value)
    buscado.value = true
  } catch {
    snackbar.value = { visible: true, mensaje: 'Error al buscar pacientes.', color: 'error' }
  } finally {
    cargando.value = false
  }
}

function seleccionarPaciente(p) {
  pacienteSeleccionado.value = p
}

function cambiarPaciente() {
  pacienteSeleccionado.value = null
}

function irANuevoPaciente() {
  navigateTo(`/recepcion/nuevo?dni=${encodeURIComponent(query.value)}`)
}

function onIngresoCreado(_ingreso, advertencia) {
  if (advertencia) {
    snackbar.value = { visible: true, mensaje: advertencia, color: 'warning' }
  } else {
    snackbar.value = { visible: true, mensaje: 'Ingreso registrado correctamente.', color: 'success' }
  }
  query.value = ''
  resultados.value = []
  buscado.value = false
  pacienteSeleccionado.value = null
}
</script>
```

- [ ] **Step 2: Verificar en browser**

```bash
cd frontend && npm run dev
# Abrir http://localhost:3000/recepcion/buscar
# Verificar:
# - Campo de búsqueda aparece
# - Buscar por nombre/apellido/DNI retorna resultados del backend
# - Hacer click en un resultado muestra la tarjeta del paciente y FormularioIngreso
# - "✕ cambiar" vuelve a la lista de resultados (sin limpiar el campo)
# - Sin resultados: aparece el botón "Registrar nuevo paciente"
# - El botón navega a /recepcion/nuevo?dni=<query>
# - El ítem "Buscar paciente" en el sidebar aparece resaltado
# - Registrar un ingreso limpia el estado y muestra snackbar de éxito
```

- [ ] **Step 3: Commit**

```bash
git add frontend/pages/recepcion/buscar.vue
git commit -m "feat: página /recepcion/buscar con búsqueda parcial y selección de paciente"
```

---

## Task 7: `pages/recepcion/nuevo.vue`

**Files:**
- Create: `frontend/pages/recepcion/nuevo.vue`

Flujo: FormularioPaciente con `dniInicial` pre-llenado desde `?dni=` en la URL → al crear el paciente aparece una tarjeta de confirmación y FormularioIngreso → al completar el ingreso, limpia el estado y vuelve a FormularioPaciente vacío. `useRoute()` y `navigateTo()` son auto-importados por Nuxt 3.

- [ ] **Step 1: Crear `pages/recepcion/nuevo.vue`**

```vue
<template>
  <v-container class="py-6" style="max-width: 960px">
    <div class="text-h5 font-weight-medium mb-6">Recepción</div>

    <FormularioPaciente
      v-if="!pacienteCreado"
      :dni-inicial="dniInicial"
      @paciente-creado="onPacienteCreado"
      @cancelar="navigateTo('/recepcion/buscar')"
    />

    <template v-if="pacienteCreado">
      <v-card class="mb-4">
        <v-card-text>
          <div class="text-caption font-weight-medium mb-1" style="color: rgb(var(--v-theme-success))">
            ✓ Paciente registrado
          </div>
          <div class="text-subtitle-1 font-weight-medium">
            {{ pacienteCreado.apellido }}, {{ pacienteCreado.nombre }}
          </div>
          <div class="text-body-2 text-medium-emphasis">DNI {{ pacienteCreado.dni }}</div>
        </v-card-text>
      </v-card>

      <FormularioIngreso
        :paciente-id="pacienteCreado.id"
        :nombre-paciente="`${pacienteCreado.apellido}, ${pacienteCreado.nombre}`"
        @ingreso-creado="onIngresoCreado"
      />
    </template>

    <v-snackbar
      v-model="snackbar.visible"
      :color="snackbar.color"
      :timeout="3500"
      location="bottom right"
    >
      {{ snackbar.mensaje }}
    </v-snackbar>
  </v-container>
</template>

<script setup>
import { ref, onMounted, onUnmounted } from 'vue'
import { useSidebarItems } from '~/composables/useSidebarItems'

const { items } = useSidebarItems()
const route = useRoute()

const dniInicial = route.query.dni ?? ''
const pacienteCreado = ref(null)
const snackbar = ref({ visible: false, mensaje: '', color: 'success' })

const SIDEBAR_LINKS = [
  { label: 'Buscar paciente',   icon: 'mdi-magnify',        to: '/recepcion/buscar' },
  { label: 'Nuevo paciente',    icon: 'mdi-account-plus',   to: '/recepcion/nuevo' },
  { label: 'Pacientes activos', icon: 'mdi-clipboard-list', to: '/recepcion/activos' },
]

onMounted(() => { items.value = SIDEBAR_LINKS })
onUnmounted(() => { items.value = [] })

function onPacienteCreado(paciente) {
  pacienteCreado.value = paciente
  snackbar.value = { visible: true, mensaje: 'Paciente registrado correctamente.', color: 'success' }
}

function onIngresoCreado(_ingreso, advertencia) {
  if (advertencia) {
    snackbar.value = { visible: true, mensaje: advertencia, color: 'warning' }
  } else {
    snackbar.value = { visible: true, mensaje: 'Ingreso registrado correctamente.', color: 'success' }
  }
  pacienteCreado.value = null
}
</script>
```

- [ ] **Step 2: Verificar en browser**

```bash
# Con frontend ya corriendo (http://localhost:3000)
# Abrir http://localhost:3000/recepcion/nuevo → FormularioPaciente vacío
# Abrir http://localhost:3000/recepcion/nuevo?dni=12345 → campo DNI pre-llenado con "12345"
# Verificar:
# - Completar y enviar el formulario → tarjeta "✓ Paciente registrado" + FormularioIngreso
# - Completar el ingreso → snackbar de éxito, vuelve a FormularioPaciente vacío
# - Botón "Cancelar" navega a /recepcion/buscar
# - El ítem "Nuevo paciente" en el sidebar aparece resaltado
```

- [ ] **Step 3: Commit**

```bash
git add frontend/pages/recepcion/nuevo.vue
git commit -m "feat: página /recepcion/nuevo con FormularioPaciente y FormularioIngreso en secuencia"
```

---

## Task 8: `pages/recepcion/activos.vue`

**Files:**
- Create: `frontend/pages/recepcion/activos.vue`

Página con un campo de texto libre arriba que filtra en tiempo real la `TablaIngresosActivos` vía la prop `busqueda`. La tabla carga los ingresos en `onMounted` automáticamente.

- [ ] **Step 1: Crear `pages/recepcion/activos.vue`**

```vue
<template>
  <v-container class="py-6" style="max-width: 960px">
    <div class="text-h5 font-weight-medium mb-6">Recepción</div>

    <v-text-field
      v-model="busqueda"
      label="Buscar por nombre, apellido o DNI"
      variant="outlined"
      density="compact"
      prepend-inner-icon="mdi-magnify"
      clearable
      class="mb-4"
    />

    <TablaIngresosActivos :busqueda="busqueda" @error="mostrarError" />

    <v-snackbar
      v-model="snackbar.visible"
      :color="snackbar.color"
      :timeout="3500"
      location="bottom right"
    >
      {{ snackbar.mensaje }}
    </v-snackbar>
  </v-container>
</template>

<script setup>
import { ref, onMounted, onUnmounted } from 'vue'
import { useSidebarItems } from '~/composables/useSidebarItems'

const { items } = useSidebarItems()

const busqueda = ref('')
const snackbar = ref({ visible: false, mensaje: '', color: 'error' })

const SIDEBAR_LINKS = [
  { label: 'Buscar paciente',   icon: 'mdi-magnify',        to: '/recepcion/buscar' },
  { label: 'Nuevo paciente',    icon: 'mdi-account-plus',   to: '/recepcion/nuevo' },
  { label: 'Pacientes activos', icon: 'mdi-clipboard-list', to: '/recepcion/activos' },
]

onMounted(() => { items.value = SIDEBAR_LINKS })
onUnmounted(() => { items.value = [] })

function mostrarError(msg) {
  snackbar.value = { visible: true, mensaje: msg, color: 'error' }
}
</script>
```

- [ ] **Step 2: Verificar en browser**

```bash
# Con frontend ya corriendo (http://localhost:3000)
# Abrir http://localhost:3000/recepcion/activos
# Verificar:
# - La tabla carga los ingresos activos al montar
# - Tipear en el campo de búsqueda filtra la tabla en tiempo real
# - Los filtros de estado (Todos / En espera / En atención) siguen funcionando
# - Limpiar el campo con la X restaura todos los resultados del estado seleccionado
# - El ítem "Pacientes activos" en el sidebar aparece resaltado
# Verificar flujo completo de navegación:
# - http://localhost:3000/recepcion redirige a /recepcion/buscar
# - Todos los ítems del sidebar navegan a su ruta y la resaltan correctamente
```

- [ ] **Step 3: Commit**

```bash
git add frontend/pages/recepcion/activos.vue
git commit -m "feat: página /recepcion/activos con filtro de texto sobre TablaIngresosActivos"
```
