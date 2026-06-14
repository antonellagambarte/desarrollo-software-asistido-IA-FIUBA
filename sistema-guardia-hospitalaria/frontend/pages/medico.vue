<template>
  <div>
    <LoginMedico v-if="!authStore.estaLogueado" @login-exitoso="actualizarSidebar" />

    <v-container v-else class="py-6" style="max-width: 1100px">
      <div class="d-flex align-center justify-space-between mb-6">
        <div class="text-h5 font-weight-medium">Médico</div>
        <v-chip color="primary" variant="tonal">
          Dr/a. {{ authStore.medico?.apellido }}, {{ authStore.medico?.nombre }}
        </v-chip>
      </div>

      <TablaPacientesMedico
        ref="tablaRef"
        :medico-id="authStore.medico.id"
        @error="mostrarError"
      />
    </v-container>

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
import { ref, watch, onMounted, onUnmounted } from 'vue'
import { useAuthStore } from '~/stores/authStore'
import { useSidebarItems } from '~/composables/useSidebarItems'

const authStore = useAuthStore()
const { items } = useSidebarItems()
const tablaRef = ref(null)
const snackbar = ref({ visible: false, mensaje: '', color: 'error' })

function mostrarError(msg) {
  snackbar.value = { visible: true, mensaje: msg, color: 'error' }
}

function actualizarSidebar() {
  if (authStore.estaLogueado) {
    items.value = [
      {
        label: 'Pacientes activos',
        icon: 'mdi-clipboard-pulse',
        onClick: () => tablaRef.value?.recargar(),
      },
      {
        label: 'Cerrar sesión',
        icon: 'mdi-logout',
        onClick: () => authStore.logout(),
      },
    ]
  } else {
    items.value = []
  }
}

watch(() => authStore.estaLogueado, actualizarSidebar)

onMounted(() => {
  authStore.cargarSesion()
  actualizarSidebar()
})

onUnmounted(() => {
  items.value = []
})
</script>
