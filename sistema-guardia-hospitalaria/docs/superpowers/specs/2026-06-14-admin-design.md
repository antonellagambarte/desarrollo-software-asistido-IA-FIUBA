# Diseño: Vista Administración

**Fecha:** 2026-06-14
**Alcance:** Página `/admin` de acceso libre para listar y registrar médicos.

---

## Contexto

La vista Admin es la tercera página del sistema. Su único propósito es permitir cargar médicos al sistema (nombre, apellido, matrícula, especialidad, usuario y contraseña). No requiere autenticación. Usa el layout existente con el sidebar a la izquierda que muestra únicamente el título "Guardia Hospitalaria", sin items de navegación adicionales.

---

## Backend — cambios

### Modelo `Medico`

Cambiar la columna `especialidad` de `nullable=True` a `nullable=False`.

```python
especialidad = Column(String, nullable=False)
```

### Schema `MedicoCreate`

Cambiar `especialidad` de opcional a requerido:

```python
# Antes
especialidad: Optional[str] = None

# Después
especialidad: str
```

`MedicoResponse` no cambia.

### Tests

Los tests existentes que crean médicos sin especialidad deben actualizarse para incluir el campo. Afecta a:

- `tests/test_models.py`: `test_medico_especialidad_opcional` → eliminar o reemplazar por un test que verifique que la especialidad es requerida.
- `tests/test_medico_endpoints.py`: `MEDICO_SIN_ESPECIALIDAD` → agregar especialidad.
- `tests/test_schemas.py`: `test_medico_create_campos_requeridos` → agregar especialidad.

No se crean nuevos endpoints. `POST /medicos/` y `GET /medicos/` ya cubren lo necesario.

---

## Frontend — estructura de archivos

```
frontend/
├── services/
│   └── medicoService.js          MODIFICAR (agregar crearMedico)
├── components/
│   └── FormularioMedico.vue      CREAR
└── pages/
    └── admin.vue                 CREAR
```

---

## Frontend — detalle por archivo

### `services/medicoService.js` — función nueva

```js
export async function crearMedico(data)
// POST /medicos/ → retorna MedicoResponse
// Lanza Error con mensaje si el backend devuelve error
// 409 → matrícula o usuario ya existente
```

### `components/FormularioMedico.vue`

Formulario Vuetify (`v-form`) con los siguientes campos, todos requeridos:

| Campo | Tipo de input |
|---|---|
| Nombre | texto |
| Apellido | texto |
| Matrícula | texto |
| Especialidad | texto |
| Usuario | texto |
| Contraseña | password |

Comportamiento:

- Llama a `crearMedico(data)` al confirmar.
- Emite `@medico-creado` con el objeto `MedicoResponse` al registrar con éxito.
- Limpia todos los campos tras un registro exitoso.
- Muestra error inline (`v-alert type="error"`) si el backend devuelve 409 (matrícula o usuario duplicado). No usa snackbar para errores de validación del servidor.

### `pages/admin.vue`

Layout normal con sidebar (el sidebar queda vacío de items — solo muestra el título "Guardia Hospitalaria" del layout base).

Estructura de la página:

- Título de página "Administración" (`text-h5`) con botón "Nuevo médico" alineado a la derecha.
- Tabla `v-data-table` con columnas: Apellido + Nombre (concatenados), Matrícula, Especialidad, Usuario.
- `v-dialog` con `FormularioMedico` que se abre al hacer clic en "Nuevo médico".
- Snackbar de éxito al registrar un médico nuevo.
- Snackbar de error si falla la carga inicial de la lista.

Ciclo de vida:

- `onMounted`: llama `listarMedicos()` para popular la tabla; establece `items.value = []` en el sidebar.
- `onUnmounted`: limpia `items.value = []`.
- Al recibir `@medico-creado` del formulario: cierra el dialog y recarga la tabla.

---

## Flujo de datos

```
admin.vue
  └── onMounted → listarMedicos() → tabla
  └── [Nuevo médico] → v-dialog → FormularioMedico
        └── crearMedico() → @medico-creado → cerrar dialog → recargar tabla
```

---

## Manejo de errores

| Caso | Comportamiento |
|---|---|
| Error al cargar lista | Snackbar de error |
| Matrícula o usuario duplicado (409) | Error inline en el formulario |
| Error de red al registrar | Error inline en el formulario |
| Registro exitoso | Snackbar de éxito + limpia formulario + recarga tabla |

---

## Fuera de alcance

- Editar médicos existentes.
- Eliminar médicos.
- Autenticación para acceder a `/admin`.
- Gestión de otras entidades (pacientes, ingresos).
