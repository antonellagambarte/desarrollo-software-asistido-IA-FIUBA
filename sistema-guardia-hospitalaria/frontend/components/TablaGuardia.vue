<template>
  <v-card>
    <v-card-text>
      <div class="d-flex align-center justify-space-between mb-4">
        <div class="text-subtitle-1 font-weight-medium">Pacientes en guardia</div>
        <v-select
          v-model="filtroEspecialidad"
          :items="especialidadesDisponibles"
          label="Filtrar por especialidad"
          variant="outlined"
          density="compact"
          clearable
          hide-details
          style="max-width: 240px"
        />
      </div>

      <v-data-table
        :headers="headers"
        :items="ingresosVisibles"
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
        <template #item.especialidad_requerida="{ item }">
          <v-chip v-if="item.especialidad_requerida" size="small" variant="tonal" color="info">
            {{ item.especialidad_requerida }}
          </v-chip>
          <span v-else class="text-medium-emphasis text-body-2">—</span>
        </template>
        <template #item.medico_asignado="{ item }">
          <span v-if="item.medico" class="text-body-2">
            Dr/a. {{ item.medico.apellido }}, {{ item.medico.nombre }}
          </span>
          <v-chip v-else size="small" variant="tonal" color="grey">Sin asignar</v-chip>
        </template>
        <template #item.acciones="{ item }">
          <v-btn size="small" color="primary" variant="tonal" @click="abrirDialogTomar(item)">
            Tomar
          </v-btn>
        </template>
      </v-data-table>
    </v-card-text>
  </v-card>

  <v-dialog v-model="dialogTomar" max-width="440">
    <v-card>
      <v-card-title class="text-subtitle-1 font-weight-medium pa-4 pb-2">Tomar paciente</v-card-title>
      <v-card-text class="pt-2">
        <v-alert
          v-if="yaAsignadoAOtro"
          type="warning"
          variant="tonal"
          density="compact"
          class="mb-3"
        >
          Este paciente ya está asignado a
          <strong>Dr/a. {{ ingresoSeleccionado?.medico?.apellido }}, {{ ingresoSeleccionado?.medico?.nombre }}</strong>.
          ¿Querés reasignarlo a vos?
        </v-alert>
        <span v-else>
          ¿Confirmás que vas a atender a
          <strong>{{ ingresoSeleccionado?.paciente?.apellido }}, {{ ingresoSeleccionado?.paciente?.nombre }}</strong>?
        </span>
      </v-card-text>
      <v-card-actions class="pa-4 pt-0">
        <v-spacer />
        <v-btn variant="text" @click="dialogTomar = false">Cancelar</v-btn>
        <v-btn :color="yaAsignadoAOtro ? 'warning' : 'primary'" :loading="procesando" @click="confirmarTomar">
          {{ yaAsignadoAOtro ? 'Reasignar' : 'Confirmar' }}
        </v-btn>
      </v-card-actions>
    </v-card>
  </v-dialog>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useAuthStore } from '~/stores/authStore'
import { listarIngresos, cambiarEstado, asignarMedico } from '~/services/ingresoService'
import { useWebSocket } from '~/composables/useWebSocket'

const emit = defineEmits(['error'])
const authStore = useAuthStore()

const cargando = ref(false)
const procesando = ref(false)
const ingresos = ref([])
const filtroEspecialidad = ref(null)

const especialidadesDisponibles = computed(() => {
  const set = new Set(ingresos.value.map((i) => i.especialidad_requerida).filter(Boolean))
  return [...set].sort()
})

const ingresosVisibles = computed(() => {
  const medicoId = authStore.medico?.id ?? null
  return ingresos.value.filter((i) => {
    if (medicoId !== null && i.medico_id === medicoId) return false
    if (filtroEspecialidad.value && i.especialidad_requerida !== filtroEspecialidad.value) return false
    return true
  })
})

const ingresoSeleccionado = ref(null)
const dialogTomar = ref(false)

const yaAsignadoAOtro = computed(() =>
  ingresoSeleccionado.value?.medico_id != null &&
  ingresoSeleccionado.value.medico_id !== authStore.medico?.id,
)

const headers = [
  { title: 'Paciente', key: 'paciente_nombre', sortable: false },
  { title: 'DNI', key: 'paciente_dni', sortable: false },
  { title: 'Prioridad', key: 'prioridad', sortable: false },
  { title: 'Especialidad', key: 'especialidad_requerida', sortable: false },
  { title: 'Médico asignado', key: 'medico_asignado', sortable: false },
  { title: 'Ingreso', key: 'fecha_ingreso', sortable: false },
  { title: 'Acciones', key: 'acciones', sortable: false },
]

function colorPrioridad(p) {
  return { BAJA: 'success', MEDIA: 'warning', ALTA: 'error' }[p] ?? 'grey'
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
  if (!authStore.medico) {
    emit('error', 'No hay médico en sesión.')
    return
  }
  procesando.value = true
  const id = ingresoSeleccionado.value.id
  let medicoAsignado = false
  try {
    await asignarMedico(id, authStore.medico.id)
    medicoAsignado = true
    await cambiarEstado(id, 'EN_ATENCION')
    dialogTomar.value = false
    ingresoSeleccionado.value = null
  } catch {
    if (medicoAsignado) {
      emit('error', 'El médico fue asignado pero no se pudo cambiar el estado. Recargue y verifique.')
    } else {
      emit('error', 'Error al tomar el paciente.')
    }
    dialogTomar.value = false
  } finally {
    procesando.value = false
    await cargarIngresos()
  }
}

defineExpose({ recargar: cargarIngresos })
onMounted(cargarIngresos)
useWebSocket(cargarIngresos)
</script>
