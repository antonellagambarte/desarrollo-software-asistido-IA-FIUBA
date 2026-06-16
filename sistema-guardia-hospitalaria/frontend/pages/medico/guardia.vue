<template>
  <div>
    <TablaGuardia ref="tablaRef" @error="mostrarError" />
    <v-snackbar
      v-model="snackbar.visible"
      :color="snackbar.color"
      :timeout="3500"
      location="bottom right"
    >
      {{ snackbar.mensaje }}
    </v-snackbar>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useAuthStore } from '~/stores/authStore'
import { useSidebarItems } from '~/composables/useSidebarItems'

const authStore = useAuthStore()
const { items } = useSidebarItems()
const tablaRef = ref(null)
const snackbar = ref({ visible: false, mensaje: '', color: 'error' })

const SIDEBAR_LINKS = [
  { label: 'Pacientes en guardia', icon: 'mdi-clipboard-list',  to: '/medico/guardia' },
  { label: 'Mis pacientes',        icon: 'mdi-clipboard-pulse', to: '/medico/activos' },
  { label: 'Cerrar sesión',        icon: 'mdi-logout',          onClick: () => authStore.logout() },
]

onMounted(() => { items.value = SIDEBAR_LINKS })

function mostrarError(msg) {
  snackbar.value = { visible: true, mensaje: msg, color: 'error' }
}
</script>
