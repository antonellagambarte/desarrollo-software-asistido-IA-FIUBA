<template>
  <div class="d-flex align-center justify-center" style="min-height: 85vh;">
    <v-card width="380" class="pa-4">
      <div class="text-center mb-6">
        <div class="text-h6 font-weight-bold text-primary">Guardia Hospitalaria</div>
        <div class="text-body-2 text-medium-emphasis mt-1">Acceso para médicos</div>
      </div>

      <v-form @submit.prevent="onSubmit">
        <v-text-field
          v-model="username"
          label="Usuario"
          variant="outlined"
          density="comfortable"
          class="mb-3"
          autocomplete="username"
          :disabled="cargando"
        />
        <v-text-field
          v-model="password"
          label="Contraseña"
          type="password"
          variant="outlined"
          density="comfortable"
          class="mb-4"
          autocomplete="current-password"
          :disabled="cargando"
        />

        <v-alert
          v-if="error"
          type="error"
          variant="tonal"
          density="compact"
          class="mb-4"
        >
          {{ error }}
        </v-alert>

        <v-btn type="submit" color="primary" block :loading="cargando">
          Ingresar
        </v-btn>
      </v-form>
    </v-card>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { useAuthStore } from '~/stores/authStore'

const emit = defineEmits(['login-exitoso'])

const authStore = useAuthStore()

const username = ref('')
const password = ref('')
const cargando = ref(false)
const error = ref('')

async function onSubmit() {
  if (!username.value || !password.value) return
  error.value = ''
  cargando.value = true
  try {
    await authStore.login(username.value, password.value)
    emit('login-exitoso')
  } catch (e) {
    error.value = e.message
  } finally {
    cargando.value = false
  }
}
</script>
