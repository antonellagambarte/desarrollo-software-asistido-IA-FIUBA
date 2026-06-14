<template>
  <v-container class="py-6" style="max-width: 960px">
    <div class="text-h5 font-weight-medium mb-6">Recepción</div>

    <div class="d-flex flex-column gap-4">
      <BuscadorPaciente
        ref="buscadorRef"
        @paciente-encontrado="onPacienteEncontrado"
        @no-encontrado="onNoPacienteEncontrado"
        @error="mostrarError"
      />

      <FormularioPaciente
        v-if="mostrarFormPaciente"
        :dni-inicial="dniParaNuevoPaciente"
        @paciente-creado="onPacienteCreado"
        @cancelar="mostrarFormPaciente = false"
      />

      <FormularioIngreso
        v-if="pacienteActual && mostrarFormIngreso"
        :paciente-id="pacienteActual.id"
        :nombre-paciente="`Registrando ingreso para: ${pacienteActual.apellido}, ${pacienteActual.nombre}`"
        @ingreso-creado="onIngresoCreado"
      />

      <TablaIngresosActivos ref="tablaRef" @error="mostrarError" />
    </div>

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

const buscadorRef = ref(null)
const tablaRef = ref(null)

const pacienteActual = ref(null)
const mostrarFormPaciente = ref(false)
const mostrarFormIngreso = ref(false)
const dniParaNuevoPaciente = ref('')

const snackbar = ref({ visible: false, mensaje: '', color: 'error' })

function mostrarError(msg) {
  snackbar.value = { visible: true, mensaje: msg, color: 'error' }
}

function mostrarExito(msg) {
  snackbar.value = { visible: true, mensaje: msg, color: 'success' }
}

function onPacienteEncontrado(paciente) {
  pacienteActual.value = paciente
  mostrarFormPaciente.value = false
  mostrarFormIngreso.value = true
}

function onNoPacienteEncontrado(dni) {
  dniParaNuevoPaciente.value = dni
  mostrarFormPaciente.value = true
  mostrarFormIngreso.value = false
  pacienteActual.value = null
}

function onPacienteCreado(paciente) {
  pacienteActual.value = paciente
  mostrarFormPaciente.value = false
  mostrarFormIngreso.value = true
  mostrarExito('Paciente registrado correctamente.')
}

async function onIngresoCreado() {
  mostrarExito('Ingreso registrado correctamente.')
  limpiarEstado()
  await tablaRef.value?.recargar()
}

function limpiarEstado() {
  pacienteActual.value = null
  mostrarFormPaciente.value = false
  mostrarFormIngreso.value = false
  dniParaNuevoPaciente.value = ''
  buscadorRef.value?.reset()
}

function activarNuevoPaciente() {
  limpiarEstado()
  mostrarFormPaciente.value = true
}

onMounted(() => {
  items.value = [
    {
      label: 'Buscar paciente',
      icon: 'mdi-magnify',
      onClick: () => buscadorRef.value?.focus(),
    },
    {
      label: 'Nuevo paciente',
      icon: 'mdi-account-plus',
      onClick: activarNuevoPaciente,
    },
    {
      label: 'Pacientes activos',
      icon: 'mdi-clipboard-list',
      onClick: () => tablaRef.value?.scrollIntoView(),
    },
  ]
})

onUnmounted(() => {
  items.value = []
})
</script>
