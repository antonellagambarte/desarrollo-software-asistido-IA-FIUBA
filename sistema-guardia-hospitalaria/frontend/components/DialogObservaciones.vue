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
        <v-textarea
          v-model="texto"
          variant="outlined"
          rows="4"
          placeholder="Escribí las observaciones del paciente..."
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
import { actualizarObservaciones } from '~/services/ingresoService'

const props = defineProps({
  modelValue: Boolean,
  ingreso: Object,
})

const emit = defineEmits(['update:modelValue', 'guardado', 'error'])

const texto = ref('')
const guardando = ref(false)

watch(
  () => props.modelValue,
  (val) => {
    if (val) texto.value = props.ingreso?.observaciones ?? ''
  },
)

function cerrar() {
  emit('update:modelValue', false)
}

async function guardar() {
  guardando.value = true
  try {
    await actualizarObservaciones(props.ingreso.id, texto.value || null)
    emit('guardado')
    cerrar()
  } catch (e) {
    emit('error', e.message)
  } finally {
    guardando.value = false
  }
}
</script>
