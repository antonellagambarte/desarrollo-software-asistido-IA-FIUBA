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
          <v-col cols="12" sm="6">
            <v-select
              v-model="medicoId"
              :items="opcionesMedicos"
              item-title="label"
              item-value="id"
              label="Médico asignado (opcional)"
              variant="outlined"
              clearable
              :loading="cargandoMedicos"
              :disabled="cargandoMedicos || errorCargaMedicos || opcionesMedicos.length === 0"
              :hint="hintMedicos"
              persistent-hint
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

        <v-alert v-if="error" type="error" variant="tonal" class="mb-4">{{ error }}</v-alert>

        <v-btn type="submit" color="primary" variant="flat" :loading="cargando">
          Registrar ingreso
        </v-btn>
      </v-form>
    </v-card-text>
  </v-card>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { crearIngreso, asignarMedico } from '~/services/ingresoService'
import { listarMedicosConCarga } from '~/services/medicoService'

const props = defineProps({
  pacienteId: { type: Number, required: true },
  nombrePaciente: { type: String, default: '' },
})
const emit = defineEmits(['ingreso-creado'])

const formRef = ref(null)
const cargando = ref(false)
const cargandoMedicos = ref(false)
const error = ref('')
const prioridad = ref(null)
const observaciones = ref('')
const medicoId = ref(null)
const medicos = ref([])
const errorCargaMedicos = ref(false)

const prioridades = ['BAJA', 'MEDIA', 'ALTA']
const requerido = (v) => !!v || 'Campo requerido'

const opcionesMedicos = computed(() =>
  medicos.value.map((m) => ({
    id: m.id,
    label: `${m.apellido}, ${m.nombre} (${m.especialidad}) — ${m.pacientes_en_espera} en espera`,
  }))
)

const hintMedicos = computed(() => {
  if (errorCargaMedicos.value) return 'No se pudieron cargar los médicos'
  if (!cargandoMedicos.value && medicos.value.length === 0) return 'No hay médicos disponibles'
  return ''
})

onMounted(async () => {
  cargandoMedicos.value = true
  try {
    medicos.value = await listarMedicosConCarga()
  } catch {
    errorCargaMedicos.value = true
  } finally {
    cargandoMedicos.value = false
  }
})

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

    let advertencia = null
    if (medicoId.value) {
      try {
        await asignarMedico(ingreso.id, medicoId.value)
      } catch {
        advertencia = 'Ingreso registrado, pero no se pudo asignar el médico. Podés asignarlo desde la tabla.'
      }
    }

    emit('ingreso-creado', ingreso, advertencia)
  } catch (e) {
    error.value = e?.message || 'Error inesperado'
  } finally {
    cargando.value = false
  }
}
</script>
