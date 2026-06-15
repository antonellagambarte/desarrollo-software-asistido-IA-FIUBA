# Diseño: Rediseño de Vista Recepción

**Fecha:** 2026-06-14
**Alcance:** Separar la vista recepción en tres rutas independientes con navegación por sidebar, y agregar búsqueda parcial de pacientes.

---

## Contexto

La vista `/recepcion` actual muestra todos sus componentes en una sola página. Los ítems del sidebar hacen scroll/focus pero no separan visualmente las secciones. El rediseño convierte cada sección en una ruta propia de Nuxt, con la URL reflejando la sub-vista activa.

---

## Estructura de rutas

```
pages/recepcion/
├── index.vue      → redirige a /recepcion/buscar
├── buscar.vue     → sub-vista: buscar e ingresar paciente
├── nuevo.vue      → sub-vista: registrar nuevo paciente
└── activos.vue    → sub-vista: pacientes activos en guardia
```

`pages/recepcion.vue` (actual) se elimina.

---

## Sidebar

Los ítems del sidebar pasan a usar `to` (ruta) en lugar de `onClick`. El composable `useSidebarItems` ya soporta objetos arbitrarios — cada página setea los tres ítems con `navigateTo`. El layout usa `:to="item.to"` en `v-list-item`, lo que habilita el resaltado automático del ítem activo via Vue Router.

Cada una de las tres páginas registra los mismos tres ítems en `onMounted` y los limpia en `onUnmounted`.

```js
// ítems comunes (referencia, cada página los registra)
[
  { label: 'Buscar paciente',   icon: 'mdi-magnify',        to: '/recepcion/buscar' },
  { label: 'Nuevo paciente',    icon: 'mdi-account-plus',   to: '/recepcion/nuevo' },
  { label: 'Pacientes activos', icon: 'mdi-clipboard-list', to: '/recepcion/activos' },
]
```

### Cambio en `useSidebarItems`

Los ítems ahora admiten `to?: string` en lugar de `onClick`. El layout renderiza `v-list-item` con `:to="item.to"` cuando el campo existe, o sigue usando `@click="item.onClick"` cuando no (compatibilidad con otras páginas como `/admin` y `/medico`).

---

## Sub-vista: `/recepcion/buscar`

### Flujo

1. Campo de texto + botón "Buscar" — llama a `GET /pacientes/?q=texto`.
2. Si hay resultados: se muestra una lista de pacientes con nombre, apellido y DNI. El usuario hace clic en uno para seleccionarlo.
3. Si no hay resultados: mensaje "No se encontró ningún paciente" + enlace "Registrar nuevo paciente" que navega a `/recepcion/nuevo?dni=<texto buscado>`.
4. Con paciente seleccionado: se muestra una tarjeta con los datos del paciente y, debajo, `FormularioIngreso`. Un botón "✕ cambiar" en la tarjeta vuelve a la lista de resultados (sin limpiar el campo de búsqueda).
5. Al completar el ingreso: limpia el estado (campo de búsqueda, resultados, paciente seleccionado). Queda listo para una nueva búsqueda.

### Estado local

| Ref | Tipo | Descripción |
|---|---|---|
| `query` | string | Texto del campo de búsqueda |
| `resultados` | PacienteResponse[] | Lista de resultados devueltos por el backend |
| `pacienteSeleccionado` | PacienteResponse \| null | Paciente elegido de la lista |
| `cargando` | boolean | Indica que la búsqueda está en curso |
| `error` | string | Error de búsqueda (snackbar) |

### Componentes usados

- `BuscadorPaciente` — **no se usa**. La lógica de búsqueda pasa a estar inline en la página (el componente actual solo soporta exact match por DNI; el nuevo flujo requiere búsqueda parcial con resultados múltiples).
- `FormularioIngreso` — se muestra cuando `pacienteSeleccionado !== null`.

---

## Sub-vista: `/recepcion/nuevo`

### Flujo

1. Muestra `FormularioPaciente` con `dniInicial` pre-llenado desde `useRoute().query.dni` (si viene de buscar).
2. Al crear el paciente (`@paciente-creado`): guarda el paciente en `pacienteCreado` ref y muestra `FormularioIngreso` debajo.
3. Al completar el ingreso (`@ingreso-creado`): limpia el estado. `FormularioPaciente` vuelve a quedar vacío, listo para otro paciente.

### Estado local

| Ref | Tipo | Descripción |
|---|---|---|
| `pacienteCreado` | PacienteResponse \| null | Paciente recién registrado |

### Componentes usados

- `FormularioPaciente`
- `FormularioIngreso` (condicional: `v-if="pacienteCreado"`)

---

## Sub-vista: `/recepcion/activos`

### Flujo

1. Campo de texto libre arriba — filtra en tiempo real.
2. `TablaIngresosActivos` debajo, recibe prop `busqueda` con el texto ingresado.
3. El componente filtra `ingresosFiltrados` por `paciente.nombre`, `paciente.apellido` y `paciente.dni` (case-insensitive, sobre los resultados ya filtrados por estado).

### Cambios en `TablaIngresosActivos.vue`

- Nueva prop `busqueda: String` (default `''`).
- El computed `ingresosFiltrados` aplica adicionalmente el filtro de texto cuando `busqueda` no está vacío.

---

## Backend — nuevo endpoint

### `GET /pacientes/?q=texto`

- Query param `q` (string, requerido). Si está vacío o ausente, retorna `[]`.
- Busca coincidencias **parciales** (LIKE case-insensitive) en `dni`, `nombre` y `apellido`.
- Retorna `list[PacienteResponse]`.
- El endpoint existente `GET /pacientes/{dni}` (exact match) no se modifica.

**Implementación sugerida (SQLAlchemy):**

```python
def buscar_pacientes(db: Session, q: str) -> list[Paciente]:
    if not q or not q.strip():
        return []
    term = f"%{q.strip()}%"
    return (
        db.query(Paciente)
        .filter(
            or_(
                Paciente.dni.ilike(term),
                Paciente.nombre.ilike(term),
                Paciente.apellido.ilike(term),
            )
        )
        .order_by(Paciente.apellido, Paciente.nombre)
        .all()
    )
```

### Nuevo service en frontend

```js
// pacienteService.js
export async function buscarPacientes(q) {
  // GET /pacientes/?q={q}
  // Retorna list[PacienteResponse]
  // Lanza Error si !res.ok
}
```

---

## Archivos afectados

| Archivo | Acción |
|---|---|
| `pages/recepcion.vue` | Eliminar |
| `pages/recepcion/index.vue` | Crear (redirect a /recepcion/buscar) |
| `pages/recepcion/buscar.vue` | Crear |
| `pages/recepcion/nuevo.vue` | Crear |
| `pages/recepcion/activos.vue` | Crear |
| `frontend/layouts/default.vue` | Modificar (soporte `to` en sidebar items) |
| `frontend/components/TablaIngresosActivos.vue` | Modificar (prop `busqueda`) |
| `frontend/services/pacienteService.js` | Modificar (agregar `buscarPacientes`) |
| `backend/routers/paciente.py` | Modificar (agregar `GET /pacientes/?q=`) |
| `backend/services/paciente.py` | Modificar (agregar `buscar_pacientes`) |
| `backend/tests/test_paciente_endpoints.py` | Modificar (agregar tests del nuevo endpoint) |

---

## Manejo de errores

| Caso | Comportamiento |
|---|---|
| Error al buscar pacientes | Snackbar de error en `/recepcion/buscar` |
| Búsqueda sin resultados | Mensaje inline + enlace a `/recepcion/nuevo?dni=...` |
| Error al crear paciente | Error inline en `FormularioPaciente` (ya existente) |
| Error al registrar ingreso | Error inline en `FormularioIngreso` (ya existente) |
| Error al cargar pacientes activos | Snackbar de error en `/recepcion/activos` |

---

## Fuera de alcance

- Modificar `BuscadorPaciente.vue` (queda en desuso para recepción pero no se elimina).
- Paginación de resultados de búsqueda.
- Búsqueda por otros campos (teléfono, etc.).
- Autenticación para acceder a las sub-vistas.
