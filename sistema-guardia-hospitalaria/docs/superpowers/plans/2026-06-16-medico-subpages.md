# Vista médico — Sub-páginas

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Separar la vista del médico en dos sub-páginas: "Pacientes en guardia" (EN_ESPERA, cualquier médico puede tomarlos) y "Mis pacientes" (EN_ATENCION asignados al médico logueado).

**Architecture:** `pages/medico.vue` se convierte en parent Nuxt 3 con guard de autenticación que renderiza `<NuxtPage />`. Dos nuevos componentes de tabla (`TablaGuardia.vue` y `TablaActivosMedico.vue`) reemplazan al actual `TablaPacientesMedico.vue`. Las sub-páginas manejan el sidebar independientemente.

**Tech Stack:** Nuxt 3, Vue 3, Vuetify 3, Pinia (`authStore`), `useSidebarItems` composable.

---

## Archivos

| Archivo | Acción |
|---|---|
| `frontend/components/TablaGuardia.vue` | CREAR |
| `frontend/components/TablaActivosMedico.vue` | CREAR |
| `frontend/pages/medico.vue` | MODIFICAR (parent con login guard + `<NuxtPage />`) |
| `frontend/pages/medico/index.vue` | CREAR (redirect) |
| `frontend/pages/medico/guardia.vue` | CREAR |
| `frontend/pages/medico/activos.vue` | CREAR |
| `frontend/components/TablaPacientesMedico.vue` | ELIMINAR |

---

## Task 1: TablaGuardia.vue

**Archivos:**
- Crear: `frontend/components/TablaGuardia.vue`

Muestra pacientes EN_ESPERA. El médico puede tomarlos. No tiene props (lee el medicoId del store). Expone `recargar()`.

- [ ] **Step 1: Crear el componente**

Crear `frontend/components/TablaGuardia.vue` con este contenido exacto:

```vue
<template>
  <v-card>
    <v-card-text>
      <div class="text-subtitle-1 font-weight-medium mb-4">Pacientes en guardia</div>

      <v-data-table
        :headers="headers"
        :items="ingresos"
        item-value="id"
        :loading="cargando"
        no-data-text="No hay pacientes en espera"
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
        <template #item.fecha_ingreso="{ item }">
          {{ formatFecha(item.fecha_ingreso) }}
        </template>
        <template #item.acciones="{ item }">
          <v-btn size="small" color="primary" variant="tonal" @click="abrirDialogTomar(item)">
            Tomar
          </v-btn>
        </template>
      </v-data-table>
    </v-card-text>
  </v-card>

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
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useAuthStore } from '~/stores/authStore'
import { listarIngresos, cambiarEstado, asignarMedico } from '~/services/ingresoService'

const emit = defineEmits(['error'])
const authStore = useAuthStore()

const cargando = ref(false)
const procesando = ref(false)
const ingresos = ref([])
const ingresoSeleccionado = ref(null)
const dialogTomar = ref(false)

const headers = [
  { title: 'Paciente', key: 'paciente_nombre', sortable: false },
  { title: 'DNI', key: 'paciente_dni', sortable: false },
  { title: 'Prioridad', key: 'prioridad', sortable: false },
  { title: 'Ingreso', key: 'fecha_ingreso', sortable: false },
  { title: 'Acciones', key: 'acciones', sortable: false },
]

function colorPrioridad(p) {
  return { BAJA: 'success', MEDIA: 'warning', ALTA: 'error' }[p] ?? 'grey'
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
    ingresos.value = await listarIngresos('EN_ESPERA')
  } catch {
    emit('error', 'Error al cargar pacientes en guardia.')
  } finally {
    cargando.value = false
  }
}

function abrirDialogTomar(ingreso) {
  ingresoSeleccionado.value = ingreso
  dialogTomar.value = true
}

async function confirmarTomar() {
  procesando.value = true
  try {
    await asignarMedico(ingresoSeleccionado.value.id, authStore.medico.id)
    await cambiarEstado(ingresoSeleccionado.value.id, 'EN_ATENCION')
    dialogTomar.value = false
  } catch {
    emit('error', 'Error al tomar el paciente.')
  } finally {
    procesando.value = false
    await cargarIngresos()
  }
}

defineExpose({ recargar: cargarIngresos })
onMounted(cargarIngresos)
</script>
```

- [ ] **Step 2: Commit**

```bash
git add frontend/components/TablaGuardia.vue
git commit -m "feat: componente TablaGuardia para pacientes EN_ESPERA"
```

---

## Task 2: TablaActivosMedico.vue

**Archivos:**
- Crear: `frontend/components/TablaActivosMedico.vue`

Muestra pacientes EN_ATENCION filtrados por `medicoId`. Acciones: observaciones y alta. El dialog de alta guarda en `observaciones_medico` (no en `observaciones`). Expone `recargar()`.

- [ ] **Step 1: Crear el componente**

Crear `frontend/components/TablaActivosMedico.vue` con este contenido exacto:

```vue
<template>
  <v-card>
    <v-card-text>
      <div class="text-subtitle-1 font-weight-medium mb-4">Mis pacientes activos</div>

      <v-data-table
        :headers="headers"
        :items="ingresosFiltrados"
        item-value="id"
        :loading="cargando"
        no-data-text="No tenés pacientes en atención"
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
        <template #item.fecha_ingreso="{ item }">
          {{ formatFecha(item.fecha_ingreso) }}
        </template>
        <template #item.acciones="{ item }">
          <div class="d-flex gap-2">
            <v-btn size="small" color="secondary" variant="tonal" @click="abrirDialogObservaciones(item)">
              Obs.
            </v-btn>
            <v-btn size="small" color="success" variant="tonal" @click="abrirDialogAlta(item)">
              Alta
            </v-btn>
          </div>
        </template>
      </v-data-table>
    </v-card-text>
  </v-card>

  <DialogObservaciones
    v-model="dialogObservaciones"
    :ingreso="ingresoSeleccionado"
    @guardado="cargarIngresos"
    @error="emit('error', $event)"
  />

  <v-dialog v-model="dialogAlta" max-width="480">
    <v-card>
      <v-card-title class="text-subtitle-1 font-weight-medium pa-4 pb-2">Dar alta</v-card-title>
      <v-card-subtitle class="px-4 pb-2">
        {{ ingresoSeleccionado?.paciente?.apellido }}, {{ ingresoSeleccionado?.paciente?.nombre }}
      </v-card-subtitle>
      <v-card-text class="pt-2">
        <div class="text-body-2 text-medium-emphasis mb-2">Observaciones finales (opcional)</div>
        <v-textarea
          v-model="textoAlta"
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
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { listarIngresos, cambiarEstado, actualizarObservacionesMedico } from '~/services/ingresoService'

const props = defineProps({
  medicoId: { type: Number, required: true },
})
const emit = defineEmits(['error'])

const cargando = ref(false)
const procesando = ref(false)
const ingresos = ref([])
const ingresoSeleccionado = ref(null)
const dialogObservaciones = ref(false)
const dialogAlta = ref(false)
const textoAlta = ref('')

const ingresosFiltrados = computed(() =>
  ingresos.value.filter(
    (i) => i.estado === 'EN_ATENCION' && i.medico_id === props.medicoId,
  ),
)

const headers = [
  { title: 'Paciente', key: 'paciente_nombre', sortable: false },
  { title: 'DNI', key: 'paciente_dni', sortable: false },
  { title: 'Prioridad', key: 'prioridad', sortable: false },
  { title: 'Ingreso', key: 'fecha_ingreso', sortable: false },
  { title: 'Acciones', key: 'acciones', sortable: false },
]

function colorPrioridad(p) {
  return { BAJA: 'success', MEDIA: 'warning', ALTA: 'error' }[p] ?? 'grey'
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

function abrirDialogObservaciones(ingreso) {
  ingresoSeleccionado.value = ingreso
  dialogObservaciones.value = true
}

function abrirDialogAlta(ingreso) {
  ingresoSeleccionado.value = ingreso
  textoAlta.value = ingreso.observaciones_medico ?? ''
  dialogAlta.value = true
}

async function confirmarAlta() {
  procesando.value = true
  try {
    await actualizarObservacionesMedico(ingresoSeleccionado.value.id, textoAlta.value || null)
    await cambiarEstado(ingresoSeleccionado.value.id, 'ALTA')
    dialogAlta.value = false
  } catch {
    emit('error', 'Error al dar el alta.')
  } finally {
    procesando.value = false
    await cargarIngresos()
  }
}

defineExpose({ recargar: cargarIngresos })
onMounted(cargarIngresos)
</script>
```

- [ ] **Step 2: Commit**

```bash
git add frontend/components/TablaActivosMedico.vue
git commit -m "feat: componente TablaActivosMedico para pacientes EN_ATENCION del médico"
```

---

## Task 3: Routing — medico.vue + sub-páginas + eliminar TablaPacientesMedico.vue

**Archivos:**
- Modificar: `frontend/pages/medico.vue`
- Crear: `frontend/pages/medico/index.vue`
- Crear: `frontend/pages/medico/guardia.vue`
- Crear: `frontend/pages/medico/activos.vue`
- Eliminar: `frontend/components/TablaPacientesMedico.vue`

**Contexto importante:** En Nuxt 3, cuando `pages/medico.vue` coexiste con el directorio `pages/medico/`, `medico.vue` se convierte en el parent layout para todas las rutas bajo `/medico/*`. Dentro del bloque `v-else` (cuando está logueado), se incluye `<NuxtPage />` para renderizar la sub-página activa.

- [ ] **Step 1: Reemplazar medico.vue**

Reemplazar `frontend/pages/medico.vue` con:

```vue
<template>
  <div>
    <LoginMedico
      v-if="!authStore.estaLogueado"
      @login-exitoso="navigateTo('/medico/guardia')"
    />

    <v-container v-else class="py-6" style="max-width: 1100px">
      <div class="d-flex align-center justify-space-between mb-6">
        <div class="text-h5 font-weight-medium">Médico</div>
        <v-chip color="primary" variant="tonal">
          Dr/a. {{ authStore.medico?.apellido }}, {{ authStore.medico?.nombre }}
        </v-chip>
      </div>
      <NuxtPage />
    </v-container>
  </div>
</template>

<script setup>
import { watch, onMounted } from 'vue'
import { useAuthStore } from '~/stores/authStore'
import { useSidebarItems } from '~/composables/useSidebarItems'

const authStore = useAuthStore()
const { items } = useSidebarItems()

watch(
  () => authStore.estaLogueado,
  (logueado) => {
    if (!logueado) {
      items.value = []
      navigateTo('/medico')
    }
  },
)

onMounted(() => {
  authStore.cargarSesion()
})
</script>
```

- [ ] **Step 2: Crear medico/index.vue**

Crear el directorio `frontend/pages/medico/` y dentro crear `index.vue`:

```vue
<script setup>
await navigateTo('/medico/guardia', { replace: true })
</script>
```

- [ ] **Step 3: Crear medico/guardia.vue**

Crear `frontend/pages/medico/guardia.vue`:

```vue
<template>
  <div>
    <TablaGuardia ref="tablaRef" @error="mostrarError" />
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
import { ref, onMounted } from 'vue'
import { useAuthStore } from '~/stores/authStore'
import { useSidebarItems } from '~/composables/useSidebarItems'

const authStore = useAuthStore()
const { items } = useSidebarItems()
const tablaRef = ref(null)
const snackbar = ref({ visible: false, mensaje: '', color: 'error' })

const SIDEBAR_LINKS = [
  { label: 'Pacientes en guardia', icon: 'mdi-clipboard-list',  to: '/medico/guardia' },
  { label: 'Mis pacientes',        icon: 'mdi-clipboard-pulse', to: '/medico/activos' },
  { label: 'Cerrar sesión',        icon: 'mdi-logout',          onClick: () => authStore.logout() },
]

onMounted(() => { items.value = SIDEBAR_LINKS })

function mostrarError(msg) {
  snackbar.value = { visible: true, mensaje: msg, color: 'error' }
}
</script>
```

- [ ] **Step 4: Crear medico/activos.vue**

Crear `frontend/pages/medico/activos.vue`:

```vue
<template>
  <div>
    <TablaActivosMedico
      :medico-id="authStore.medico?.id"
      @error="mostrarError"
    />
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
import { ref, onMounted } from 'vue'
import { useAuthStore } from '~/stores/authStore'
import { useSidebarItems } from '~/composables/useSidebarItems'

const authStore = useAuthStore()
const { items } = useSidebarItems()
const snackbar = ref({ visible: false, mensaje: '', color: 'error' })

const SIDEBAR_LINKS = [
  { label: 'Pacientes en guardia', icon: 'mdi-clipboard-list',  to: '/medico/guardia' },
  { label: 'Mis pacientes',        icon: 'mdi-clipboard-pulse', to: '/medico/activos' },
  { label: 'Cerrar sesión',        icon: 'mdi-logout',          onClick: () => authStore.logout() },
]

onMounted(() => { items.value = SIDEBAR_LINKS })

function mostrarError(msg) {
  snackbar.value = { visible: true, mensaje: msg, color: 'error' }
}
</script>
```

- [ ] **Step 5: Eliminar TablaPacientesMedico.vue**

```bash
git rm frontend/components/TablaPacientesMedico.vue
```

- [ ] **Step 6: Commit**

```bash
git add frontend/pages/medico.vue frontend/pages/medico/index.vue frontend/pages/medico/guardia.vue frontend/pages/medico/activos.vue
git commit -m "feat: sub-páginas /medico/guardia y /medico/activos con sidebar de navegación"
```
