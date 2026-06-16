<template>
  <v-dialog
    :model-value="modelValue"
    max-width="480"
    @update:model-value="$emit('update:modelValue', $event)"
  >
    <v-card>
      <v-card-title class="text-subtitle-1 font-weight-medium pa-4 pb-2">
        Observaciones
      </v-card-title>
      <v-card-subtitle class="px-4 pb-2">
        {{ ingreso?.paciente?.apellido }}, {{ ingreso?.paciente?.nombre }}
      </v-card-subtitle>
      <v-card-text class="pt-2">
        <div class="text-caption text-medium-emphasis mb-1">Observaciones de recepción</div>
        <div
          class="text-body-2 mb-4 pa-3 rounded"
          style="min-height: 48px; background: rgba(var(--v-theme-surface-variant), 1)"
        >
          {{ ingreso?.observaciones || 'Sin observaciones de recepción' }}
        </div>

        <div class="text-caption text-medium-emphasis mb-1">Observaciones del médico</div>
        <v-textarea
          v-model="textoMedico"
          variant="outlined"
          rows="4"
          placeholder="Escribí tus observaciones..."
          hide-details
        />
      </v-card-text>
      <v-card-actions class="pa-4 pt-0">
        <v-spacer />
        <v-btn variant="text" @click="cerrar">Cancelar</v-btn>
        <v-btn color="primary" :loading="guardando" @click="guardar">Guardar</v-btn>
      </v-card-actions>
    </v-card>
  </v-dialog>
</template>

<script setup>
import { ref, watch } from 'vue'
import { actualizarObservacionesMedico } from '~/services/ingresoService'

const props = defineProps({
  modelValue: Boolean,
  ingreso: Object,
})

const emit = defineEmits(['update:modelValue', 'guardado', 'error'])

const textoMedico = ref('')
const guardando = ref(false)

watch(
  () => props.modelValue,
  (val) => {
    if (val) textoMedico.value = props.ingreso?.observaciones_medico ?? ''
  },
)

function cerrar() {
  emit('update:modelValue', false)
}

async function guardar() {
  if (!props.ingreso) return
  guardando.value = true
  try {
    await actualizarObservacionesMedico(props.ingreso.id, textoMedico.value || null)
    emit('guardado')
    cerrar()
  } catch (e) {
    emit('error', e.message)
  } finally {
    guardando.value = false
  }
}
</script>
