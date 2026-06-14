# Diseño: Vista Recepción

**Fecha:** 2026-06-14
**Alcance:** Layout global de la app y página `/recepcion` completa. Sin autenticación.

---

## Contexto

La aplicación tiene dos vistas independientes: `/recepcion` (para el personal de recepción) y `/medico` (para médicos). No hay autenticación — cada rol accede directamente a su URL. Las vistas no deben ofrecer navegación cruzada entre sí.

Este documento cubre el layout global y la implementación de `/recepcion`.

---

## Layout global (`layouts/default.vue`)

La app usa un layout con dos zonas:

- **Sidebar izquierda** (~220px, permanente): específica de cada página. Muestra el nombre del sistema arriba y los ítems de acción de la página activa.
- **Área de contenido** (`v-main`): ocupa el resto de la pantalla. Evita líneas muy largas en pantallas anchas porque el sidebar actúa como limitador natural.

Implementado con `v-navigation-drawer` (permanente) + `v-main` de Vuetify.

El sidebar **no contiene links de navegación entre páginas**. Cada página define sus propios ítems de sidebar usando un composable compartido `useSidebarItems` (basado en `useState` de Nuxt 3), que el layout lee para renderizar los ítems.

---

## Sidebar de `/recepcion`

Tres ítems de acción:

| Ítem | Ícono | Comportamiento |
|---|---|---|
| Buscar paciente | 🔍 | Pone el foco en el campo DNI del buscador |
| Nuevo paciente | 👤 | Activa directamente el formulario de registro (sin buscar) |
| Pacientes activos | 📋 | Hace scroll a la tabla de activos |

---

## Flujo principal de `/recepcion`

La página sigue un flujo vertical paso a paso. Los bloques aparecen condicionalmente según el estado de la interacción.

### Bloque 1 — Buscador (siempre visible)

- Campo de texto para DNI + botón "Buscar"
- Enter en el campo dispara la búsqueda
- **Resultado encontrado:** muestra alerta de éxito con nombre, apellido y edad del paciente. Aparece el Bloque 3 (formulario de ingreso).
- **No encontrado:** muestra alerta de advertencia "No se encontró paciente con DNI {X}" + botón "Registrar nuevo paciente". Al hacer click aparece el Bloque 2.
- **Error de red u otro:** snackbar de error.

### Bloque 2 — Formulario de registro de paciente (condicional)

Aparece cuando el paciente no fue encontrado y se hace click en "Registrar nuevo paciente". También se activa desde el ítem "Nuevo paciente" del sidebar.

Campos:

| Campo | Tipo | Requerido |
|---|---|---|
| DNI | texto (prellenado si viene de búsqueda) | sí |
| Nombre | texto | sí |
| Apellido | texto | sí |
| Fecha de nacimiento | date | sí |
| Teléfono | texto | no |

Al guardar exitosamente:
- El formulario desaparece.
- Aparece alerta con los datos del paciente recién creado.
- Aparece el Bloque 3.

Error 409 (DNI duplicado): mensaje de error inline en el formulario.

### Bloque 3 — Formulario de ingreso a guardia (condicional)

Aparece cuando hay un paciente activo (encontrado o recién registrado).

Muestra el nombre del paciente como referencia ("Registrando ingreso para: Gómez, Laura").

Campos:

| Campo | Tipo | Requerido |
|---|---|---|
| Prioridad | select: BAJA / MEDIA / ALTA | sí |
| Observaciones | textarea | no |

Al guardar exitosamente:
- Snackbar de éxito: "Ingreso registrado correctamente".
- Se limpia todo el estado de la página (buscador, formularios, paciente activo).
- La tabla de activos se recarga.

### Bloque 4 — Tabla de pacientes activos (siempre visible)

Siempre visible al pie de la página. Se carga al montar y se actualiza tras cada ingreso registrado.

**Filtro:** selector de estado encima de la tabla con opciones: Todos / En espera / En atención.

**Columnas:**

| Columna | Fuente |
|---|---|
| Paciente | `apellido, nombre` |
| DNI | `paciente.dni` |
| Prioridad | chip de color: BAJA=verde, MEDIA=naranja, ALTA=rojo |
| Estado | chip de color: EN_ESPERA=azul, EN_ATENCION=amarillo |
| Ingreso | `fecha_ingreso` formateada como dd/mm HH:mm |
| Médico | `medico.apellido, medico.nombre` o "—" si no asignado |

Read-only desde recepción. Sin acciones en las filas.

---

## Servicios (`services/`)

Las páginas y componentes no realizan llamadas HTTP directas. Todo pasa por servicios.

- **`pacienteService.js`**: `buscarPacientePorDni(dni)`, `crearPaciente(data)`
- **`ingresoService.js`**: `crearIngreso(data)`, `listarIngresos(estado?)` — `estado` es opcional; sin él devuelve todos

---

## Estructura de archivos

```
frontend/
├── composables/
│   └── useSidebarItems.js    CREAR — useState compartido entre páginas y layout
├── layouts/
│   └── default.vue           MODIFICAR — agregar sidebar + v-main
├── services/
│   ├── pacienteService.js    CREAR
│   └── ingresoService.js     CREAR
├── components/
│   ├── AppSidebar.vue        CREAR — sidebar con ítems configurables
│   ├── BuscadorPaciente.vue  CREAR
│   ├── FormularioPaciente.vue CREAR
│   ├── FormularioIngreso.vue  CREAR
│   └── TablaIngresosActivos.vue CREAR
└── pages/
    └── recepcion.vue         MODIFICAR — integra todo
```

---

## Estado de la página

Estado local (sin Pinia — no hay estado compartido con otras páginas):

- `pacienteActual` — paciente encontrado o recién creado, o `null`
- `mostrarFormPaciente` — boolean
- `mostrarFormIngreso` — boolean
- `filtroEstado` — `null` | `'EN_ESPERA'` | `'EN_ATENCION'`
- `ingresos` — lista de ingresos activos

---

## Manejo de errores

- Errores de validación de formulario: mensajes inline (Vuetify validation).
- DNI duplicado (409): mensaje inline en el formulario de paciente.
- Paciente no encontrado (404): alerta en el buscador (no snackbar).
- Errores de red o servidor: snackbar de error.
- Éxitos (paciente creado, ingreso registrado): snackbar de éxito.

---

## Fuera de alcance

- Autenticación o autorización por rol.
- Acciones sobre ingresos desde recepción (cambiar estado, asignar médico) — eso es de `/medico`.
- Edición de pacientes ya registrados.
