# Diseño: Vista Médico

**Fecha:** 2026-06-14
**Alcance:** Página `/medico` con autenticación mínima, gestión de pacientes en guardia y acciones de médico (tomar, observar, dar alta).

---

## Contexto

La vista Médico es la segunda página principal del sistema. El médico accede con usuario y contraseña, ve los pacientes activos en guardia y puede tomar pacientes para atención, registrar observaciones y dar altas.

La autenticación aplica **solo a `/medico`**. La página `/recepcion` sigue siendo de acceso libre.

El backend ya cuenta con endpoints para cambiar estado y asignar médico. Faltan: credenciales en el modelo `Medico`, endpoint de login y endpoint para actualizar observaciones.

---

## Backend — cambios

### Modelo `Medico`

Agregar dos columnas a `medicos`:

| Campo | Tipo | Constraint |
|---|---|---|
| `username` | String | unique, not null |
| `password_hash` | String | not null |

### `POST /medicos/` — actualización

`MedicoCreate` incorpora dos campos nuevos:

```
username: str        # único en el sistema
password: str        # plain text en el request; el servicio lo hashea con passlib/bcrypt antes de persistir
```

`MedicoResponse` **no expone** `password_hash` ni `password`.

El servicio valida unicidad de `username` y lanza `ValueError` si ya existe (el router responde 409).

### Nuevo `POST /auth/login`

**Request:**
```json
{ "username": "drgarcia", "password": "secreto" }
```

**Response 200:** objeto `MedicoResponse` completo (id, nombre, apellido, matrícula, especialidad, username).

**Response 401:** `{ "detail": "Credenciales incorrectas" }` — tanto si el usuario no existe como si la contraseña no coincide. No distinguir entre los dos casos (seguridad).

No se usa JWT. El frontend guarda el objeto médico en Pinia y en localStorage.

Router: `routers/auth.py`, prefijo `/auth`, tag `"auth"`.

### Nuevo `PATCH /ingresos/{id}/observaciones`

**Request:**
```json
{ "observaciones": "Texto libre..." }
```

**Response 200:** `IngresoGuardiaResponse` actualizado.

**Response 404:** si el ingreso no existe.

**Response 400:** si el ingreso tiene estado `ALTA` (no se puede modificar).

Schema nuevo: `ActualizarObservacionesRequest` con campo `observaciones: str`.

---

## Frontend — estructura de archivos

```
frontend/
├── services/
│   ├── authService.js            CREAR
│   ├── medicoService.js          CREAR
│   └── ingresoService.js         MODIFICAR
├── stores/
│   └── authStore.js              CREAR
├── pages/
│   └── medico.vue                CREAR
└── components/
    ├── LoginMedico.vue           CREAR
    ├── TablaPacientesMedico.vue  CREAR
    └── DialogObservaciones.vue   CREAR
```

---

## Frontend — detalle por archivo

### `services/authService.js`

```js
export async function login(username, password)
// POST /auth/login → retorna MedicoResponse | lanza Error con mensaje del backend
```

### `services/medicoService.js`

```js
export async function listarMedicos()
// GET /medicos/ → retorna array de MedicoResponse
```

### `services/ingresoService.js` — funciones nuevas

```js
export async function cambiarEstado(ingresoId, estado)
// PATCH /ingresos/{id}/estado → retorna IngresoGuardiaResponse

export async function asignarMedico(ingresoId, medicoId)
// PATCH /ingresos/{id}/medico → retorna IngresoGuardiaResponse

export async function actualizarObservaciones(ingresoId, observaciones)
// PATCH /ingresos/{id}/observaciones → retorna IngresoGuardiaResponse
```

### `stores/authStore.js`

Store Pinia con:

```js
state: {
  medico: null   // objeto MedicoResponse o null
}

actions:
  login(username, password)   // llama authService.login, guarda en state + localStorage
  logout()                    // limpia state + localStorage
  cargarSesion()              // lee localStorage al inicializar, restaura state

getters:
  estaLogueado                // medico !== null
```

Persistencia: clave `medico_sesion` en `localStorage`. Se usa `JSON.stringify` / `JSON.parse`.

### `pages/medico.vue`

- En `onMounted`: llama `authStore.cargarSesion()`.
- Si `!authStore.estaLogueado` → muestra `<LoginMedico>` centrado (sin sidebar, full-screen).
- Si `authStore.estaLogueado` → muestra `<TablaPacientesMedico>` con el layout normal.
- Sidebar items: `Pacientes activos` (scroll a la tabla) y `Cerrar sesión` (llama `authStore.logout()`).
- El nombre del médico logueado se muestra como chip en la esquina superior derecha de la página.

### `components/LoginMedico.vue`

Formulario centrado en pantalla (sin layout de sidebar). Campos:
- `username` (texto, requerido)
- `password` (tipo password, requerido)

Emite `@login-exitoso` con el objeto médico.

Muestra error inline ("Usuario o contraseña incorrectos") si el backend devuelve 401. No distingue usuario inexistente de contraseña incorrecta.

### `components/TablaPacientesMedico.vue`

Props: `medicoId` (id del médico logueado, para asignar al "tomar").

Tabla Vuetify `v-data-table` con:

**Columnas:** Paciente (apellido + nombre), DNI, Prioridad, Estado, Ingreso (fecha/hora), Acciones.

**Filtro:** `v-btn-toggle` con valores `todos / EN_ESPERA / EN_ATENCION`. Excluye siempre los ingresos con estado `ALTA`.

**Color de filas:** fondo amarillo (`#fffde7`) para `EN_ESPERA`, fondo verde (`#f1f8e9`) para `EN_ATENCION`. Implementado con `:row-props`.

**Acciones por estado:**
- `EN_ESPERA` → botón "Tomar" (abre dialog de confirmación)
- `EN_ATENCION` → botones "Obs." y "Alta"

**Dialog Tomar:** confirmación simple. Al confirmar: llama `asignarMedico(ingresoId, medicoId)` y luego `cambiarEstado(ingresoId, 'EN_ATENCION')`. Recarga la tabla. Emite `@error` si falla.

**Dialog Alta:** confirmación con textarea pre-llenada con observaciones actuales (editable). Al confirmar: si el texto de observaciones cambió, llama `actualizarObservaciones()` primero; luego llama `cambiarEstado(ingresoId, 'ALTA')`. Recarga la tabla.

**Dialog Observaciones:** textarea con contenido actual. Al guardar: llama `actualizarObservaciones(ingresoId, texto)`. Muestra snackbar de éxito. Recarga la tabla.

La tabla recarga `onMounted` y expone `recargar()` vía `defineExpose`.

Emite `@error` hacia la página para mostrar snackbar.

### `components/DialogObservaciones.vue`

Props: `modelValue` (boolean, v-model para abrir/cerrar), `ingreso` (objeto IngresoGuardiaResponse).

Emite: `update:modelValue`, `guardado`.

Contiene un `v-textarea` pre-llenado con `ingreso.observaciones`. Al guardar llama `actualizarObservaciones`. Al cerrar resetea el textarea.

---

## Flujo de datos

```
medico.vue
  └── onMounted → cargarSesion()
        ├── no logueado → <LoginMedico> @login-exitoso → authStore.login() → muestra tabla
        └── logueado → <TablaPacientesMedico :medico-id="authStore.medico.id">
                          ├── onMounted → listarIngresos()
                          ├── [Tomar] → asignarMedico() + cambiarEstado(EN_ATENCION) → recargar
                          ├── [Obs.]  → <DialogObservaciones> → actualizarObservaciones() → recargar
                          └── [Alta]  → actualizarObservaciones()? + cambiarEstado(ALTA) → recargar
```

---

## Estados válidos y transiciones

Las reglas de negocio viven en el backend. El frontend solo llama los endpoints; no valida transiciones.

| Acción | Transición |
|---|---|
| Tomar | `EN_ESPERA` → `EN_ATENCION` |
| Alta | `EN_ATENCION` → `ALTA` |
| Observaciones | cualquier estado activo (no ALTA) |

---

## Manejo de errores

- Errores de red o respuestas no-OK → snackbar de error en `medico.vue`.
- Login 401 → error inline en `LoginMedico`, no snackbar.
- Éxito en observaciones → snackbar de éxito.
- Éxito en tomar / alta → tabla recarga silenciosamente (sin snackbar, el cambio visual es suficiente).

---

## Fuera de alcance

- Notificaciones en tiempo real (polling o websockets).
- Registro de historial de acciones del médico.
- Visualización de ingresos con estado ALTA en esta vista.
- Gestión de médicos (crear/editar) desde la interfaz — se hace por API o desde recepción en el futuro.
