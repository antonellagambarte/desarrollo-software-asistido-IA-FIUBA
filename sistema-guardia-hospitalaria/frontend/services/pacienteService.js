const BASE = 'http://localhost:8000'

export async function buscarPacientePorDni(dni) {
  const res = await fetch(`${BASE}/pacientes/${dni}`)
  if (res.status === 404) return null
  if (!res.ok) throw new Error('Error al buscar paciente')
  return res.json()
}

export async function crearPaciente(data) {
  const res = await fetch(`${BASE}/pacientes/`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(data),
  })
  if (res.status === 409) throw new Error('Ya existe un paciente con ese DNI')
  if (!res.ok) throw new Error('Error al registrar paciente')
  return res.json()
}

export async function buscarPacientes(q) {
  const res = await fetch(`${BASE}/pacientes/?q=${encodeURIComponent(q)}`)
  if (!res.ok) throw new Error('Error al buscar pacientes')
  return res.json()
}
