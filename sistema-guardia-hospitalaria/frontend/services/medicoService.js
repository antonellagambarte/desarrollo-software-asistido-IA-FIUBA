const BASE = 'http://localhost:8000'

export async function listarMedicos() {
  const res = await fetch(`${BASE}/medicos/`)
  if (!res.ok) throw new Error('Error al obtener médicos')
  return res.json()
}
