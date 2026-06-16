# Vista médico — Sub-páginas por rol

## Problema

La vista `/medico` muestra todos los pacientes activos (EN_ESPERA y EN_ATENCION) en una sola tabla con un toggle de filtro. El médico no tiene una vista dedicada a sus propios pacientes separada de los que están disponibles para tomar.

## Solución

Reestructurar `/medico` con sub-páginas Nuxt 3. `medico.vue` pasa a ser el parent que maneja el guard de autenticación y renderiza `<NuxtPage />`. Las sub-páginas manejan cada vista. El sidebar refleja la navegación entre vistas.

## Alcance

- Modificar `pages/medico.vue` para convertirlo en parent con login guard.
- Crear `pages/medico/index.vue` que redirige a `/medico/guardia`.
- Crear `pages/medico/guardia.vue` con `TablaGuardia.vue`.
- Crear `pages/medico/activos.vue` con `TablaActivosMedico.vue`.
- Crear `components/TablaGuardia.vue`.
- Crear `components/TablaActivosMedico.vue`.
- Eliminar `components/TablaPacientesMedico.vue` (reemplazado por los dos nuevos).
- Sin cambios de backend.

---

## Estructura de archivos

```
pages/
  medico.vue              → MODIFICAR (parent: login guard + <NuxtPage />)
  medico/
    index.vue             → CREAR (redirect a /medico/guardia)
    guardia.vue           → CREAR (usa TablaGuardia)
    activos.vue           → CREAR (usa TablaActivosMedico)

components/
  TablaGuardia.vue        → CREAR
  TablaActivosMedico.vue  → CREAR
  TablaPacientesMedico.vue → ELIMINAR
```

---

## `pages/medico.vue` — Parent con login guard

Responsabilidad: chequear autenticación. Si no está logueado, mostrar `LoginMedico`. Si está logueado, mostrar el header con el nombre del médico y `<NuxtPage />`.

- Al montar: `authStore.cargarSesion()`.
- Si `authStore.estaLogueado` es false: renderiza `<LoginMedico @login-exitoso="navigateTo('/medico/guardia')" />`.
- Si `authStore.estaLogueado` es true: renderiza header + `<NuxtPage />`.
- Header: título "Médico" + chip "Dr/a. Apellido, Nombre".
- El snackbar de error se mueve a cada sub-página (cada una maneja sus propios errores).
- No maneja sidebar (lo hacen las sub-páginas).
- Al desloguearse (`watch` sobre `estaLogueado`): si pasa a false, `navigateTo('/medico')` para volver al login.

## `pages/medico/index.vue`

Redirige a `/medico/guardia`:

```vue
<script setup>
await navigateTo('/medico/guardia', { replace: true })
</script>
```

## `pages/medico/guardia.vue`

Responsabilidad: mostrar pacientes EN_ESPERA y permitir tomarlos.

- Setea sidebar en `onMounted` con los tres ítems (ver Sidebar más abajo).
- Renderiza `<TablaGuardia @error="mostrarError" />`.
- Snackbar para errores.

## `pages/medico/activos.vue`

Responsabilidad: mostrar los pacientes EN_ATENCION asignados al médico logueado.

- Setea sidebar en `onMounted`.
- Necesita el `medicoId` del store: `authStore.medico?.id`.
- Renderiza `<TablaActivosMedico :medico-id="authStore.medico?.id" @error="mostrarError" />`.
- Snackbar para errores.

---

## Sidebar

Ambas sub-páginas setean los mismos tres ítems:

```js
const SIDEBAR_LINKS = [
  { label: 'Pacientes en guardia', icon: 'mdi-clipboard-list',  to: '/medico/guardia' },
  { label: 'Mis pacientes',        icon: 'mdi-clipboard-pulse', to: '/medico/activos' },
  { label: 'Cerrar sesión',        icon: 'mdi-logout',          onClick: () => authStore.logout() },
]
```

El ítem "Cerrar sesión" usa `onClick`. El layout ya soporta ambos patrones (`to` y `onClick`).

---

## `components/TablaGuardia.vue`

Responsabilidad: mostrar pacientes EN_ESPERA y permitir que el médico los tome.

**Props:** ninguna (carga sus propios datos).

**Emits:** `@error(mensaje: string)`

**Datos:** llama a `listarIngresos('EN_ESPERA')` al montar y al confirmar tomar.

**Columnas:** Paciente (apellido, nombre), DNI, Prioridad, Ingreso (fecha/hora), Acciones.

**Acciones:** botón "Tomar" por fila.

**Dialog Tomar:** confirmación antes de ejecutar. Al confirmar:
1. `asignarMedico(ingresoId, medicoId)` — `medicoId` viene del store (`useAuthStore().medico.id`).
2. `cambiarEstado(ingresoId, 'EN_ATENCION')`.
3. Recarga la tabla. El paciente ya no aparece (estado cambió a EN_ATENCION).

**Sin filtros de estado** — siempre muestra solo EN_ESPERA.

**Expone:** `recargar()` via `defineExpose`.

## `components/TablaActivosMedico.vue`

Responsabilidad: mostrar los pacientes EN_ATENCION asignados al médico logueado con acciones de observaciones y alta.

**Props:** `medicoId: Number` (requerido).

**Emits:** `@error(mensaje: string)`

**Datos:** llama a `listarIngresos()` (sin filtro de estado) al montar. Filtra en el frontend:
```js
const ingresosFiltrados = computed(() =>
  ingresos.value.filter(
    (i) => i.estado === 'EN_ATENCION' && i.medico_id === props.medicoId
  )
)
```

**Columnas:** Paciente (apellido, nombre), DNI, Prioridad, Ingreso (fecha/hora), Acciones.

**Acciones por fila:** botón "Obs." (abre `DialogObservaciones`) + botón "Alta" (dialog de confirmación con textarea de observaciones finales).

**Dialog Alta:** textarea "Observaciones finales (opcional)", pre-cargado con `ingreso.observaciones_medico ?? ''`. Al confirmar:
1. `actualizarObservacionesMedico(ingresoId, textoAlta || null)` — guarda en el campo del médico, no en el de recepción.
2. `cambiarEstado(ingresoId, 'ALTA')`.
3. Recarga la tabla.

**Expone:** `recargar()` via `defineExpose`.

---

## Flujo de autenticación

1. Usuario entra a `/medico` → `medico.vue` carga sesión de `sessionStorage`.
2. Si no está logueado: muestra `LoginMedico`. Al hacer login exitoso → `navigateTo('/medico/guardia')`.
3. Si ya estaba logueado (sesión en sessionStorage): `medico.vue` renderiza `<NuxtPage />` → `index.vue` redirige a `/medico/guardia`.
4. Al cerrar sesión: `authStore.logout()` → `estaLogueado` pasa a false → `watch` en `medico.vue` llama a `navigateTo('/medico')` → se muestra el login.

---

## Reglas de negocio

- Solo el médico logueado puede tomar pacientes y verlos en "Mis pacientes".
- Un paciente EN_ESPERA puede ser tomado por cualquier médico logueado.
- "Mis pacientes activos" muestra solo los que tienen `medico_id === medicoId` Y `estado === 'EN_ATENCION'`.
- No se modifica el backend.
