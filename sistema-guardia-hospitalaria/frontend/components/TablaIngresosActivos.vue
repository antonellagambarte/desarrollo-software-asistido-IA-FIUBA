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
