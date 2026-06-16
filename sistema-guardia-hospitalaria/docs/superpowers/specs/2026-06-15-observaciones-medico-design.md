# Observaciones del médico — Diseño

## Problema

El campo `observaciones` del modelo `IngresoGuardia` es compartido entre recepción y el médico. El dialog del médico lo pre-carga y permite sobreescribirlo, lo que destruye la información cargada por recepción. Las observaciones de recepción y las del médico son información de dos actores distintos y deben almacenarse por separado.

## Solución

Agregar un campo `observaciones_medico` al modelo `IngresoGuardia`. El campo `observaciones` existente queda reservado para recepción y solo se escribe al crear el ingreso o desde la vista `/recepcion`. El médico escribe exclusivamente en `observaciones_medico` a través de un endpoint y un dialog reestructurado.

## Alcance

- Backend: nueva columna, nuevo endpoint, nuevo service, nuevos tests.
- Frontend: nuevo método en `ingresoService.js`, reestructura de `DialogObservaciones.vue`.
- No se modifica `FormularioIngreso.vue` (el campo de recepción ya funciona correctamente).
- No se agrega edición de observaciones de recepción desde `/recepcion/activos` (fuera de alcance de este cambio).

---

## Backend

### Modelo — `IngresoGuardia`

Agregar columna:

```python
observaciones_medico = Column(Text, nullable=True)
```

El campo `observaciones` existente no se renombra ni modifica.

### Schema — `IngresoGuardiaResponse`

Agregar campo:

```python
observaciones_medico: Optional[str] = None
```

### Endpoint

```
PATCH /ingresos/{ingreso_id}/observaciones-medico
```

**Request body:**
```json
{ "observaciones_medico": "texto" }
```
`observaciones_medico` es `Optional[str]` — acepta `null` para borrar.

**Respuesta exitosa:** `200 OK` con `IngresoGuardiaResponse` actualizado.

**Errores:**
- `404` si el ingreso no existe.
- `400` si el ingreso está en estado `ALTA`.

### Service

```python
def actualizar_observaciones_medico(db: Session, ingreso_id: int, texto: Optional[str]) -> IngresoGuardia:
```

- Levanta `LookupError` si el ingreso no existe.
- Levanta `ValueError` si el estado es `ALTA`.
- Escribe `ingreso.observaciones_medico = texto` y hace commit.

### Schema request

```python
class ActualizarObservacionesMedicoRequest(BaseModel):
    observaciones_medico: Optional[str] = None
```

### Tests

Archivo: `tests/test_ingreso_endpoints.py`

- `test_actualizar_observaciones_medico_ok` — estado `EN_ATENCION`, guarda y devuelve el campo.
- `test_actualizar_observaciones_medico_no_modifica_observaciones_recepcion` — verifica que `observaciones` (recepción) no cambia.
- `test_actualizar_observaciones_medico_en_alta_retorna_400` — estado `ALTA`, espera 400.
- `test_actualizar_observaciones_medico_ingreso_inexistente_retorna_404`.

---

## Frontend

### `ingresoService.js`

Agregar función:

```js
export async function actualizarObservacionesMedico(ingresoId, texto) {
  const res = await fetch(`${BASE}/ingresos/${ingresoId}/observaciones-medico`, {
    method: 'PATCH',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ observaciones_medico: texto || null }),
  })
  if (!res.ok) throw new Error('Error al guardar observaciones del médico')
  return res.json()
}
```

### `DialogObservaciones.vue`

Reestructura:

**Sección superior (read-only):** Muestra `props.ingreso?.observaciones`.
- Label: "Observaciones de recepción".
- Si está vacío o `null`: mostrar texto en gris "Sin observaciones de recepción".
- No es editable.

**Sección inferior (editable):** Textarea para las observaciones del médico.
- Label: "Observaciones del médico".
- Al abrir el dialog: pre-cargar con `props.ingreso?.observaciones_medico ?? ''`.
- Al guardar: llamar a `actualizarObservacionesMedico(props.ingreso.id, texto)`.

**Al guardar:** emite `'guardado'` y cierra. En caso de error: emite `'error'` con el mensaje.

La función `actualizarObservaciones` (recepción) que actualmente usa el componente se reemplaza por `actualizarObservacionesMedico`.

---

## Reglas de negocio

- `observaciones` (recepción): solo se escribe al crear el ingreso. No se modifica desde la vista del médico.
- `observaciones_medico`: solo se escribe desde la vista del médico, solo cuando el ingreso no está en `ALTA`.
- Ambos campos son opcionales y pueden ser `null`.
