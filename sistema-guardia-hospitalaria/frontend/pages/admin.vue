<template>
  <v-container class="py-6" style="max-width: 1000px">
    <div class="d-flex align-center justify-space-between mb-6">
      <div class="text-h5 font-weight-medium">Administración</div>
      <v-btn color="primary" prepend-icon="mdi-plus" @click="dialogNuevo = true">
        Nuevo médico
      </v-btn>
    </div>

    <v-data-table
      :headers="headers"
      :items="medicos"
      :loading="cargando"
      no-data-text="No hay médicos registrados"
      density="compact"
    >
      <template #item.nombre_completo="{ item }">
        {{ item.apellido }}, {{ item.nombre }}
      </template>
    </v-data-table>

    <v-dialog v-model="dialogNuevo" max-width="560">
      <v-card>
        <v-card-title class="text-subtitle-1 font-weight-medium pa-4 pb-2">
          Registrar médico
        </v-card-title>
        <v-card-text>
          <FormularioMedico @medico-creado="onMedicoCreado" />
        </v-card-text>
        <v-card-actions class="pa-4 pt-0">
          <v-spacer />
          <v-btn variant="text" @click="dialogNuevo = false">Cerrar</v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>

    <v-snackbar
      v-model="snackbar.visible"
      :color="snackbar.color"
      :timeout="3500"
      location="bottom right"
    >
      {{ snackbar.mensaje }}
    </v-snackbar>
  </v-container>
</template>

<script setup>
import { ref, onMounted, onUnmounted } from 'vue'
import { listarMedicos } from '~/services/medicoService'
import { useSidebarItems } from '~/composables/useSidebarItems'

const { items } = useSidebarItems()
const medicos = ref([])
const cargando = ref(false)
const dialogNuevo = ref(false)
const snackbar = ref({ visible: false, mensaje: '', color: 'success' })

const headers = [
  { title: 'Médico', key: 'nombre_completo', sortable: false },
  { title: 'Matrícula', key: 'matricula', sortable: false },
  { title: 'Especialidad', key: 'especialidad', sortable: false },
  { title: 'Usuario', key: 'username', sortable: false },
]

async function cargarMedicos() {
  cargando.value = true
  try {
    medicos.value = await listarMedicos()
  } catch {
    snackbar.value = { visible: true, mensaje: 'Error al cargar médicos.', color: 'error' }
  } finally {
    cargando.value = false
  }
}

function onMedicoCreado(medico) {
  dialogNuevo.value = false
  medicos.value = [...medicos.value, medico]
  snackbar.value = {
    visible: true,
    mensaje: `Médico ${medico.apellido} registrado correctamente.`,
    color: 'success',
  }
}

onMounted(() => {
  items.value = []
  cargarMedicos()
})

onUnmounted(() => {
  items.value = []
})
</script>
