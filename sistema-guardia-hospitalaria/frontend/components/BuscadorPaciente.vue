<template>
  <v-card>
    <v-card-text>
      <div class="text-subtitle-1 font-weight-medium mb-4">Buscar paciente</div>

      <div class="d-flex gap-3 align-start">
        <v-text-field
          ref="campoRef"
          v-model="dni"
          label="DNI"
          variant="outlined"
          density="compact"
          hide-details
          style="max-width: 240px"
          @keyup.enter="buscar"
        />
        <v-btn color="primary" variant="flat" :loading="cargando" @click="buscar">
          Buscar
        </v-btn>
      </div>

      <v-alert v-if="pacienteEncontrado" type="success" variant="tonal" class="mt-4">
        Paciente encontrado: <strong>{{ pacienteEncontrado.apellido }}, {{ pacienteEncontrado.nombre }}</strong>
        ({{ pacienteEncontrado.edad }} años)
      </v-alert>

      <v-alert v-if="resultadoNoEncontrado" type="warning" variant="tonal" class="mt-4">
        <div>No se encontró paciente con DNI <strong>{{ dniConsultado }}</strong>.</div>
        <v-btn variant="text" size="small" class="mt-2 pl-0" @click="emitirNoEncontrado">
          Registrar nuevo paciente
        </v-btn>
      </v-alert>
    </v-card-text>
  </v-card>
</template>

<script setup>
import { ref } from 'vue'
import { buscarPacientePorDni } from '~/services/pacienteService'

const emit = defineEmits(['paciente-encontrado', 'no-encontrado', 'error'])

const campoRef = ref(null)
const dni = ref('')
const cargando = ref(false)
const resultadoNoEncontrado = ref(false)
const dniConsultado = ref('')
const pacienteEncontrado = ref(null)

defineExpose({
  focus: () => campoRef.value?.focus(),
  reset: () => {
    dni.value = ''
    pacienteEncontrado.value = null
    resultadoNoEncontrado.value = false
    dniConsultado.value = ''
  },
})

async function buscar() {
  const dniTrimmed = dni.value.trim()
  if (!dniTrimmed) return

  cargando.value = true
  pacienteEncontrado.value = null
  resultadoNoEncontrado.value = false

  try {
    const paciente = await buscarPacientePorDni(dniTrimmed)
    if (paciente) {
      pacienteEncontrado.value = paciente
      emit('paciente-encontrado', paciente)
    } else {
      dniConsultado.value = dniTrimmed
      resultadoNoEncontrado.value = true
    }
  } catch {
    emit('error', 'Error al buscar paciente. Intentá de nuevo.')
  } finally {
    cargando.value = false
  }
}

function emitirNoEncontrado() {
  emit('no-encontrado', dniConsultado.value)
}
</script>
