import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { login as loginService } from '~/services/authService'

export const useAuthStore = defineStore('auth', () => {
  const medico = ref(null)

  const estaLogueado = computed(() => medico.value !== null)

  function cargarSesion() {
    if (!process.client) return
    const stored = localStorage.getItem('medico_sesion')
    if (stored) {
      try {
        medico.value = JSON.parse(stored)
      } catch {
        medico.value = null
      }
    }
  }

  async function login(username, password) {
    const data = await loginService(username, password)
    medico.value = data
    localStorage.setItem('medico_sesion', JSON.stringify(data))
  }

  function logout() {
    medico.value = null
    localStorage.removeItem('medico_sesion')
  }

  return { medico, estaLogueado, cargarSesion, login, logout }
})
