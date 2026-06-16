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
import { ref, onMounted } from 'vue'
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
  navigateTo('/recepcion/nuevo')
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
