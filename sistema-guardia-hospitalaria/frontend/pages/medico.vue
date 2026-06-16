<template>
  <div>
    <LoginMedico
      v-if="!authStore.estaLogueado"
      @login-exitoso="navigateTo('/medico/guardia')"
    />

    <v-container v-else class="py-6" style="max-width: 1100px">
      <div class="d-flex align-center justify-space-between mb-6">
        <div class="text-h5 font-weight-medium">Médico</div>
        <v-chip color="primary" variant="tonal">
          Dr/a. {{ authStore.medico?.apellido }}, {{ authStore.medico?.nombre }}
        </v-chip>
      </div>
      <NuxtPage />
    </v-container>
  </div>
</template>

<script setup>
import { watch, onMounted } from 'vue'
import { useAuthStore } from '~/stores/authStore'
import { useSidebarItems } from '~/composables/useSidebarItems'

const authStore = useAuthStore()
const { items } = useSidebarItems()

watch(
  () => authStore.estaLogueado,
  (logueado) => {
    if (!logueado) {
      items.value = []
      navigateTo('/medico')
    }
  },
)

onMounted(() => {
  authStore.cargarSesion()
})
</script>
