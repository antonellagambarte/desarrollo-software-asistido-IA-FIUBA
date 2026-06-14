<template>
  <v-form ref="formRef" @submit.prevent="registrar">
    <v-alert
      v-if="error"
      type="error"
      variant="tonal"
      class="mb-4"
      density="compact"
    >
      {{ error }}
    </v-alert>

    <v-row dense>
      <v-col cols="12" sm="6">
        <v-text-field
          v-model="form.nombre"
          label="Nombre"
          :rules="[v => !!v || 'Requerido']"
          variant="outlined"
          density="compact"
        />
      </v-col>
      <v-col cols="12" sm="6">
        <v-text-field
          v-model="form.apellido"
          label="Apellido"
          :rules="[v => !!v || 'Requerido']"
          variant="outlined"
          density="compact"
        />
      </v-col>
      <v-col cols="12" sm="6">
        <v-text-field
          v-model="form.matricula"
          label="Matrícula"
          :rules="[v => !!v || 'Requerido']"
          variant="outlined"
          density="compact"
        />
      </v-col>
      <v-col cols="12" sm="6">
        <v-text-field
          v-model="form.especialidad"
          label="Especialidad"
          :rules="[v => !!v || 'Requerido']"
          variant="outlined"
          density="compact"
        />
      </v-col>
      <v-col cols="12" sm="6">
        <v-text-field
          v-model="form.username"
          label="Usuario"
          :rules="[v => !!v || 'Requerido']"
          variant="outlined"
          density="compact"
          autocomplete="off"
        />
      </v-col>
      <v-col cols="12" sm="6">
        <v-text-field
          v-model="form.password"
          label="Contraseña"
          type="password"
          :rules="[v => !!v || 'Requerido']"
          variant="outlined"
          density="compact"
          autocomplete="new-password"
        />
      </v-col>
    </v-row>

    <div class="d-flex justify-end mt-2">
      <v-btn type="submit" color="primary" :loading="cargando">Registrar</v-btn>
    </div>
  </v-form>
</template>

<script setup>
import { ref, reactive } from 'vue'
import { crearMedico } from '~/services/medicoService'

const emit = defineEmits(['medico-creado'])

const formRef = ref(null)
const cargando = ref(false)
const error = ref('')
const form = reactive({
  nombre: '',
  apellido: '',
  matricula: '',
  especialidad: '',
  username: '',
  password: '',
})

function limpiar() {
  Object.keys(form).forEach(k => (form[k] = ''))
  formRef.value?.reset()
  error.value = ''
}

async function registrar() {
  const { valid } = await formRef.value.validate()
  if (!valid) return
  cargando.value = true
  error.value = ''
  try {
    const medico = await crearMedico({ ...form })
    limpiar()
    emit('medico-creado', medico)
  } catch (e) {
    error.value = e.message
  } finally {
    cargando.value = false
  }
}
</script>
