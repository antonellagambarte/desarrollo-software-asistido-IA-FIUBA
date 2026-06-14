<template>
  <v-card>
    <v-card-text>
      <div class="text-subtitle-1 font-weight-medium mb-1">Registrar ingreso a guardia</div>
      <div class="text-body-2 text-medium-emphasis mb-4">{{ nombrePaciente }}</div>

      <v-form ref="formRef" @submit.prevent="guardar">
        <v-row>
          <v-col cols="12" sm="6">
            <v-select
              v-model="prioridad"
              :items="prioridades"
              label="Prioridad"
              variant="outlined"
              :rules="[requerido]"
            />
          </v-col>
          <v-col cols="12">
            <v-textarea
              v-model="observaciones"
              label="Observaciones (opcional)"
              variant="outlined"
              rows="3"
            />
          </v-col>
        </v-row>

        <v-alert v-if="error" type="error" variant="tonal" class="mb-4">
          {{ error }}
        </v-alert>

        <v-btn type="submit" color="primary" variant="flat" :loading="cargando">
          Registrar ingreso
        </v-btn>
      </v-form>
    </v-card-text>
  </v-card>
</template>

<script setup>
import { ref } from 'vue'
import { crearIngreso } from '~/services/ingresoService'

const props = defineProps({
  pacienteId: { type: Number, required: true },
  nombrePaciente: { type: String, default: '' },
})
const emit = defineEmits(['ingreso-creado'])

const formRef = ref(null)
const cargando = ref(false)
const error = ref('')
const prioridad = ref(null)
const observaciones = ref('')

const prioridades = ['BAJA', 'MEDIA', 'ALTA']
const requerido = (v) => !!v || 'Campo requerido'

async function guardar() {
  const { valid } = await formRef.value.validate()
  if (!valid) return

  cargando.value = true
  error.value = ''

  try {
    const data = {
      paciente_id: props.pacienteId,
      prioridad: prioridad.value,
      ...(observaciones.value ? { observaciones: observaciones.value } : {}),
    }
    const ingreso = await crearIngreso(data)
    emit('ingreso-creado', ingreso)
  } catch (e) {
    error.value = e.message
  } finally {
    cargando.value = false
  }
}
</script>
