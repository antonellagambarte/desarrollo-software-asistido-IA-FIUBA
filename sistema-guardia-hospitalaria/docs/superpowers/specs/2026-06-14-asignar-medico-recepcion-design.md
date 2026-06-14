# Diseño: Asignación de médico en recepción

**Fecha:** 2026-06-14
**Alcance:** Agregar selector de médico (opcional) al formulario de ingreso en la vista recepción, con conteo de pacientes en espera por médico.

---

## Contexto

Al registrar un ingreso a guardia, recepción puede opcionalmente asignar un médico en ese momento. Para facilitar la elección, el selector muestra cuántos pacientes en estado EN_ESPERA tiene asignado cada médico actualmente.

El endpoint `PATCH /ingresos/{id}/medico` ya existe. Se reutiliza para la asignación post-creación.

---

## Backend

### Nuevo schema: `MedicoConCargaResponse`

Extiende `MedicoResponse` con un campo adicional:

```python
class MedicoConCargaResponse(MedicoResponse):
    pacientes_en_espera: int
```

Archivo: `backend/schemas/medico.py`

### Nuevo endpoint: `GET /medicos/con-carga`

```
GET /medicos/con-carga?estado=EN_ESPERA
```

- Query param `estado` de tipo `EstadoIngreso`, opcional, default `EstadoIngreso.EN_ESPERA`.
- Devuelve todos los médicos con el conteo de ingresos asignados al médico con el estado indicado.
- No requiere autenticación.
- Response: `list[MedicoConCargaResponse]`

**Lógica de conteo:** query con subquery o join que cuenta los `IngresoGuardia` donde `medico_id = medico.id` y `estado = estado_param`.

Archivo: `backend/routers/medico.py`

### Tests

Agregar en `tests/test_medico_endpoints.py`:

- `GET /medicos/con-carga` sin médicos devuelve `[]`
- `GET /medicos/con-carga` con médicos pero sin ingresos devuelve `pacientes_en_espera: 0` para todos
- `GET /medicos/con-carga` con ingresos EN_ESPERA asignados devuelve el conteo correcto
- `GET /medicos/con-carga?estado=EN_ATENCION` devuelve conteo de EN_ATENCION (no EN_ESPERA)

---

## Frontend

### `services/medicoService.js` — función nueva

```js
export async function listarMedicosConCarga(estado = 'EN_ESPERA') {
  // GET /medicos/con-carga?estado={estado}
  // Devuelve array de MedicoConCarga: { ...MedicoResponse, pacientes_en_espera: number }
  // Lanza Error con mensaje si el backend devuelve error
}
```

### `components/FormularioIngreso.vue` — cambios

Agregar al formulario existente:

- `v-select` opcional con label "Médico asignado (opcional)"
- Se carga llamando `listarMedicosConCarga()` en `onMounted`
- Cada opción muestra: `"Apellido, Nombre (Especialidad) — N en espera"`
- El campo no tiene regla de validación (es opcional)
- Si falla la carga de médicos: el select queda deshabilitado con hint "No se pudieron cargar los médicos"
- Si la lista está vacía: el select queda deshabilitado con hint "No hay médicos disponibles"

**Flujo de guardado cuando se selecciona médico:**

```
1. POST /ingresos/ → ingreso creado (sin médico)
2. PATCH /ingresos/{ingreso.id}/medico → asigna médico
3. emit('ingreso-creado', ingreso)
```

**Si el PATCH falla** (después de que el POST ya creó el ingreso):
- Emite `@ingreso-creado` igual (el ingreso existe)
- Muestra warning inline: "Ingreso registrado, pero no se pudo asignar el médico. Podés asignarlo desde la tabla."

**Si el POST falla:** error inline en el formulario, sin cambios.

### Manejo de errores completo

| Caso | Comportamiento |
|---|---|
| Error al cargar médicos | Select deshabilitado con hint de error; formulario sigue funcionando |
| Lista de médicos vacía | Select deshabilitado con "No hay médicos disponibles" |
| POST /ingresos/ falla | Error inline, nada más |
| PATCH /medico falla (ingreso ya creado) | Emite `@ingreso-creado` + warning inline en el formulario |
| Ningún médico seleccionado | Solo POST, sin PATCH |

---

## Flujo de datos

```
FormularioIngreso (onMounted)
  └── listarMedicosConCarga() → popula v-select con conteo

FormularioIngreso (al guardar)
  └── crearIngreso(data) → POST /ingresos/
        └── [si medicoId] asignarMedico(ingreso.id, medicoId) → PATCH /ingresos/{id}/medico
              └── emit('ingreso-creado', ingreso)
```

---

## Fuera de alcance

- Modificar `IngresoGuardiaCreate` para incluir `medico_id`.
- Reasignación de médico desde la vista recepción (ya existe en la vista médico).
- Actualización en tiempo real del conteo mientras el selector está abierto.
