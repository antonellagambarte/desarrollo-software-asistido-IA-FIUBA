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

export async function obtenerIngresoActivoPorPaciente(pacienteId) {
  const res = await fetch(`${BASE}/ingresos/activo-por-paciente/${pacienteId}`)
  if (!res.ok) throw new Error('Error al verificar ingreso activo')
  return res.json() // null si no hay ingreso activo
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

export async function actualizarEspecialidad(ingresoId, especialidadRequerida) {
  const res = await fetch(`${BASE}/ingresos/${ingresoId}/especialidad`, {
    method: 'PATCH',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ especialidad_requerida: especialidadRequerida }),
  })
  if (!res.ok) throw new Error('Error al actualizar especialidad')
  return res.json()
}

export async function actualizarPrioridad(ingresoId, prioridad) {
  const res = await fetch(`${BASE}/ingresos/${ingresoId}/prioridad`, {
    method: 'PATCH',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ prioridad }),
  })
  if (!res.ok) throw new Error('Error al actualizar prioridad')
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

export async function actualizarObservacionesMedico(ingresoId, observaciones) {
  const res = await fetch(`${BASE}/ingresos/${ingresoId}/observaciones-medico`, {
    method: 'PATCH',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ observaciones_medico: observaciones || null }),
  })
  if (!res.ok) throw new Error('Error al guardar observaciones del médico')
  return res.json()
}
