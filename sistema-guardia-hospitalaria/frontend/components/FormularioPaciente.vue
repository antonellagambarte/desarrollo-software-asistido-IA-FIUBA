<template>
  <v-card>
    <v-card-text>
      <div class="text-subtitle-1 font-weight-medium mb-4">Registrar paciente</div>

      <v-form ref="formRef" @submit.prevent="guardar">
        <v-row>
          <v-col cols="12" sm="6">
            <v-text-field
              v-model="campos.dni"
              label="DNI"
              variant="outlined"
              :rules="[requerido]"
            />
          </v-col>
          <v-col cols="12" sm="6">
            <v-text-field
              v-model="campos.nombre"
              label="Nombre"
              variant="outlined"
              :rules="[requerido]"
            />
          </v-col>
          <v-col cols="12" sm="6">
            <v-text-field
              v-model="campos.apellido"
              label="Apellido"
              variant="outlined"
              :rules="[requerido]"
            />
          </v-col>
          <v-col cols="12" sm="6">
            <v-text-field
              v-model="campos.fecha_nacimiento"
              label="Fecha de nacimiento"
              type="date"
              variant="outlined"
              :rules="[requerido]"
            />
          </v-col>
          <v-col cols="12" sm="6">
            <v-text-field
              v-model="campos.telefono"
              label="Teléfono (opcional)"
              variant="outlined"
            />
          </v-col>
        </v-row>

        <v-alert v-if="error" type="error" variant="tonal" class="mb-4">
          {{ error }}
        </v-alert>

        <div class="d-flex gap-3">
          <v-btn type="submit" color="primary" variant="flat" :loading="cargando">
            Registrar paciente
          </v-btn>
          <v-btn variant="text" @click="$emit('cancelar')">Cancelar</v-btn>
        </div>
      </v-form>
    </v-card-text>
  </v-card>
</template>

<script setup>
import { ref, reactive } from 'vue'
import { crearPaciente } from '~/services/pacienteService'

const props = defineProps({
  dniInicial: { type: String, default: '' },
})
const emit = defineEmits(['paciente-creado', 'cancelar'])

const formRef = ref(null)
const cargando = ref(false)
const error = ref('')

const campos = reactive({
  dni: props.dniInicial,
  nombre: '',
  apellido: '',
  fecha_nacimiento: '',
  telefono: '',
})

const requerido = (v) => !!v || 'Campo requerido'

async function guardar() {
  const { valid } = await formRef.value.validate()
  if (!valid) return

  cargando.value = true
  error.value = ''

  try {
    const data = {
      dni: campos.dni,
      nombre: campos.nombre,
      apellido: campos.apellido,
      fecha_nacimiento: campos.fecha_nacimiento,
      ...(campos.telefono ? { telefono: campos.telefono } : {}),
    }
    const paciente = await crearPaciente(data)
    emit('paciente-creado', paciente)
  } catch (e) {
    error.value = e.message
  } finally {
    cargando.value = false
  }
}
</script>
