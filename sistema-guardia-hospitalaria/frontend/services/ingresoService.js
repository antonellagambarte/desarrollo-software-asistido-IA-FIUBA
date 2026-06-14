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

export async function cambiarEstado(ingresoId, estado) {
  const res = await fetch(`${BASE}/ingresos/${ingresoId}/estado`, {
    method: 'PATCH',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ estado }),
  })
  if (!res.ok) throw new Error('Error al cambiar estado')
  return res.json()
}

export async function asignarMedico(ingresoId, medicoId) {
  const res = await fetch(`${BASE}/ingresos/${ingresoId}/medico`, {
    method: 'PATCH',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ medico_id: medicoId }),
  })
  if (!res.ok) throw new Error('Error al asignar médico')
  return res.json()
}

export async function actualizarObservaciones(ingresoId, observaciones) {
  const res = await fetch(`${BASE}/ingresos/${ingresoId}/observaciones`, {
    method: 'PATCH',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ observaciones }),
  })
  if (!res.ok) throw new Error('Error al actualizar observaciones')
  return res.json()
}
