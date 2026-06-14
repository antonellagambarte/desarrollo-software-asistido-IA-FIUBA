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
  } catch {
    emit('error', 'Error al tomar el paciente.')
  } finally {
    procesando.value = false
    await cargarIngresos()
  }
}

async function confirmarAlta() {
  procesando.value = true
  try {
    await actualizarObservaciones(ingresoSeleccionado.value.id, textoAltaObs.value || null)
    await cambiarEstado(ingresoSeleccionado.value.id, 'ALTA')
    dialogAlta.value = false
  } catch {
    emit('error', 'Error al dar el alta.')
  } finally {
    procesando.value = false
    await cargarIngresos()
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
