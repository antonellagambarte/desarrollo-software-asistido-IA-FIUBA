<template>
  <v-card>
    <v-card-text>
      <div class="text-subtitle-1 font-weight-medium mb-4">Mis pacientes activos</div>

      <v-data-table
        :headers="headers"
        :items="ingresosFiltrados"
        item-value="id"
        :loading="cargando"
        no-data-text="No tenés pacientes asignados"
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
        <template #item.estado="{ item }">
          <v-chip
            :color="colorEstado(item.estado)"
            size="small"
            variant="tonal"
          >
            {{ item.estado === 'EN_ESPERA' ? 'En espera' : 'En atención' }}
          </v-chip>
        </template>
        <template #item.acciones="{ item }">
          <div class="d-flex ga-2">
            <template v-if="item.estado === 'EN_ESPERA'">
              <v-btn size="small" color="primary" variant="tonal" :loading="procesandoId === item.id" @click="atender(item)">
                Atender
              </v-btn>
            </template>
            <template v-else>
              <v-btn size="small" color="secondary" variant="tonal" @click="abrirDialogObservaciones(item)">
                Obs.
              </v-btn>
              <v-btn size="small" color="success" variant="tonal" @click="abrirDialogAlta(item)">
                Alta
              </v-btn>
            </template>
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
import { useWebSocket } from '~/composables/useWebSocket'

const props = defineProps({
  medicoId: { type: Number, required: true },
})
const emit = defineEmits(['error'])

const cargando = ref(false)
const procesando = ref(false)
const procesandoId = ref(null)
const ingresos = ref([])
const ingresoSeleccionado = ref(null)
const dialogObservaciones = ref(false)
const dialogAlta = ref(false)
const textoAlta = ref('')

const ingresosFiltrados = computed(() =>
  ingresos.value.filter((i) => i.medico_id === props.medicoId && i.estado !== 'ALTA'),
)

const headers = [
  { title: 'Paciente', key: 'paciente_nombre', sortable: false },
  { title: 'DNI', key: 'paciente_dni', sortable: false },
  { title: 'Prioridad', key: 'prioridad', sortable: false },
  { title: 'Estado', key: 'estado', sortable: false },
  { title: 'Ingreso', key: 'fecha_ingreso', sortable: false },
  { title: 'Acciones', key: 'acciones', sortable: false },
]

function colorPrioridad(p) {
  return { BAJA: 'success', MEDIA: 'warning', ALTA: 'error' }[p] ?? 'grey'
}

function colorEstado(e) {
  return { EN_ESPERA: 'warning', EN_ATENCION: 'primary' }[e] ?? 'grey'
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
    ingresos.value = await listarIngresos()
  } catch {
    emit('error', 'Error al cargar pacientes.')
  } finally {
    cargando.value = false
  }
}

async function atender(ingreso) {
  procesandoId.value = ingreso.id
  try {
    await cambiarEstado(ingreso.id, 'EN_ATENCION')
    await cargarIngresos()
  } catch {
    emit('error', 'Error al iniciar la atención.')
  } finally {
    procesandoId.value = null
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
    ingresoSeleccionado.value = null
  } catch {
    emit('error', 'Error al dar el alta.')
  } finally {
    procesando.value = false
    await cargarIngresos()
  }
}

defineExpose({ recargar: cargarIngresos })
onMounted(cargarIngresos)
useWebSocket(cargarIngresos)
</script>
