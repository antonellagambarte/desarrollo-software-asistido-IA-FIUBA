const BASE = 'http://localhost:8000'

export async function listarMedicos() {
  const res = await fetch(`${BASE}/medicos/`)
  if (!res.ok) throw new Error('Error al obtener médicos')
  return res.json()
}

export async function listarMedicosConCarga(estado = 'EN_ESPERA') {
  const res = await fetch(`${BASE}/medicos/con-carga?estado=${estado}`)
  if (!res.ok) throw new Error('Error al obtener médicos con carga')
  return res.json()
}

export async function crearMedico(data) {
  const res = await fetch(`${BASE}/medicos/`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(data),
  })
  if (res.status === 409) {
    const err = await res.json()
    throw new Error(err.detail ?? 'Matrícula o usuario ya registrado')
  }
  if (!res.ok) throw new Error('Error al registrar médico')
  return res.json()
}
