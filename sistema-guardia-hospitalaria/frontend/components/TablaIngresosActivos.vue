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
        <template #item.especialidad_requerida="{ item }">
          <v-chip v-if="item.especialidad_requerida" size="small" variant="tonal" color="info">
            {{ item.especialidad_requerida }}
          </v-chip>
          <span v-else class="text-medium-emphasis text-body-2">—</span>
        </template>
        <template #item.medico_nombre="{ item }">
          {{ item.medico ? `${item.medico.apellido}, ${item.medico.nombre}` : '—' }}
        </template>
        <template #item.acciones="{ item }">
          <v-btn
            v-if="item.estado !== 'ALTA'"
            size="small"
            variant="tonal"
            color="primary"
            @click="abrirEdicion(item)"
          >
            Editar
          </v-btn>
        </template>
      </v-data-table>
    </v-card-text>
  </v-card>

  <v-dialog v-model="dialogEdicion" max-width="480">
    <v-card>
      <v-card-title class="text-subtitle-1 font-weight-medium pa-4 pb-2">
        Editar ingreso
      </v-card-title>
      <v-card-subtitle class="px-4 pb-2">
        {{ ingresoEditando?.paciente?.apellido }}, {{ ingresoEditando?.paciente?.nombre }}
      </v-card-subtitle>
      <v-card-text class="pt-2">
        <v-select
          v-model="edicionPrioridad"
          :items="prioridades"
          label="Prioridad"
          variant="outlined"
          class="mb-3"
        />
        <v-select
          v-model="edicionEspecialidad"
          :items="ESPECIALIDADES"
          label="Especialidad requerida"
          variant="outlined"
          class="mb-3"
        />
        <v-select
          v-model="edicionMedicoId"
          :items="opcionesMedicos"
          item-title="label"
          item-value="id"
          label="Médico asignado (opcional)"
          variant="outlined"
          clearable
          :loading="cargandoMedicos"
        />
      </v-card-text>
      <v-card-actions class="pa-4 pt-0">
        <v-spacer />
        <v-btn variant="text" @click="dialogEdicion = false">Cancelar</v-btn>
        <v-btn color="primary" :loading="guardando" @click="guardarEdicion">Guardar</v-btn>
      </v-card-actions>
    </v-card>
  </v-dialog>

  <v-snackbar v-model="snackbar.visible" :color="snackbar.color" :timeout="3000" location="bottom right">
    {{ snackbar.mensaje }}
  </v-snackbar>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { listarIngresos, actualizarPrioridad, actualizarEspecialidad, asignarMedico } from '~/services/ingresoService'
import { ESPECIALIDADES } from '~/utils/especialidades'
import { listarMedicosConCarga } from '~/services/medicoService'
import { useWebSocket } from '~/composables/useWebSocket'

const props = defineProps({
  busqueda: { type: String, default: '' },
})

const emit = defineEmits(['error'])

const rootRef = ref(null)
const cargando = ref(false)
const ingresos = ref([])
const filtro = ref('todos')

const dialogEdicion = ref(false)
const ingresoEditando = ref(null)
const edicionPrioridad = ref(null)
const edicionEspecialidad = ref(null)
const edicionMedicoId = ref(null)
const guardando = ref(false)
const cargandoMedicos = ref(false)
const medicos = ref([])
const snackbar = ref({ visible: false, mensaje: '', color: 'success' })

const prioridades = ['BAJA', 'MEDIA', 'ALTA']

const opcionesMedicos = computed(() =>
  medicos.value.map((m) => ({
    id: m.id,
    label: `${m.apellido}, ${m.nombre} (${m.especialidad})`,
  }))
)

const headers = [
  { title: 'Paciente', key: 'paciente_nombre', sortable: false },
  { title: 'DNI', key: 'paciente_dni', sortable: false },
  { title: 'Prioridad', key: 'prioridad', sortable: false },
  { title: 'Especialidad', key: 'especialidad_requerida', sortable: false },
  { title: 'Estado', key: 'estado', sortable: false },
  { title: 'Ingreso', key: 'fecha_ingreso', sortable: false },
  { title: 'Médico', key: 'medico_nombre', sortable: false },
  { title: '', key: 'acciones', sortable: false },
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
  if (!iso) return '—'
  const isoUtc = /[Z+]/.test(iso) ? iso : iso + 'Z'
  const d = new Date(isoUtc)
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

async function abrirEdicion(ingreso) {
  ingresoEditando.value = ingreso
  edicionPrioridad.value = ingreso.prioridad
  edicionEspecialidad.value = ingreso.especialidad_requerida ?? null
  edicionMedicoId.value = ingreso.medico_id ?? null
  dialogEdicion.value = true

  if (medicos.value.length === 0) {
    cargandoMedicos.value = true
    try {
      medicos.value = await listarMedicosConCarga()
    } finally {
      cargandoMedicos.value = false
    }
  }
}

async function guardarEdicion() {
  guardando.value = true
  try {
    const id = ingresoEditando.value.id
    const promesas = []

    if (edicionPrioridad.value !== ingresoEditando.value.prioridad) {
      promesas.push(actualizarPrioridad(id, edicionPrioridad.value))
    }
    if (edicionEspecialidad.value !== (ingresoEditando.value.especialidad_requerida ?? null)) {
      promesas.push(actualizarEspecialidad(id, edicionEspecialidad.value))
    }
    if (edicionMedicoId.value !== (ingresoEditando.value.medico_id ?? null)) {
      promesas.push(asignarMedico(id, edicionMedicoId.value))
    }

    await Promise.all(promesas)
    dialogEdicion.value = false
    snackbar.value = { visible: true, mensaje: 'Ingreso actualizado.', color: 'success' }
    await cargarIngresos()
  } catch {
    snackbar.value = { visible: true, mensaje: 'Error al guardar los cambios.', color: 'error' }
  } finally {
    guardando.value = false
  }
}

defineExpose({
  recargar: cargarIngresos,
  scrollIntoView: () => rootRef.value?.$el?.scrollIntoView({ behavior: 'smooth' }),
})

onMounted(cargarIngresos)
useWebSocket(cargarIngresos)
</script>
