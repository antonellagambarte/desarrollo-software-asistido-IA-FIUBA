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
import { ref, onMounted } from 'vue'
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
