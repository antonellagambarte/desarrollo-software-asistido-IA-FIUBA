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
  if (!iso) return '—'
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
</script>
