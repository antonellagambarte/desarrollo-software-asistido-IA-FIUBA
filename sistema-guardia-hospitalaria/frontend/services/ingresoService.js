const BASE = 'http://localhost:8000'

export async function crearIngreso(data) {
  const res = await fetch(`${BASE}/ingresos/`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(data),
  })
  if (!res.ok) throw new Error('Error al registrar ingreso')
  return res.json()
}

export async function listarIngresos(estado = null) {
  const url = estado ? `${BASE}/ingresos/?estado=${estado}` : `${BASE}/ingresos/`
  const res = await fetch(url)
  if (!res.ok) throw new Error('Error al obtener ingresos')
  return res.json()
}
