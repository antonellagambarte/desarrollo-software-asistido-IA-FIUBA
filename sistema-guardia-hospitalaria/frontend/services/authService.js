const BASE = 'http://localhost:8000'

export async function login(username, password) {
  const res = await fetch(`${BASE}/auth/login`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ username, password }),
  })
  if (res.status === 401) throw new Error('Usuario o contraseña incorrectos')
  if (!res.ok) throw new Error('Error al iniciar sesión')
  return res.json()
}
