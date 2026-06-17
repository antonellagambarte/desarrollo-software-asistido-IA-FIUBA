<template>
  <v-container class="py-6" style="max-width: 1300px">
    <div class="text-h5 font-weight-medium mb-6">Recepción</div>

    <v-text-field
      v-model="busqueda"
      label="Buscar por nombre, apellido o DNI"
      variant="outlined"
      density="compact"
      prepend-inner-icon="mdi-magnify"
      clearable
      class="mb-4"
    />

    <TablaIngresosActivos :busqueda="busqueda" @error="mostrarError" />

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

const busqueda = ref('')
const snackbar = ref({ visible: false, mensaje: '', color: 'error' })

const SIDEBAR_LINKS = [
  { label: 'Buscar paciente',   icon: 'mdi-magnify',        to: '/recepcion/buscar' },
  { label: 'Nuevo paciente',    icon: 'mdi-account-plus',   to: '/recepcion/nuevo' },
  { label: 'Pacientes activos', icon: 'mdi-clipboard-list', to: '/recepcion/activos' },
]

onMounted(() => { items.value = SIDEBAR_LINKS })

function mostrarError(msg) {
  snackbar.value = { visible: true, mensaje: msg, color: 'error' }
}
</script>
