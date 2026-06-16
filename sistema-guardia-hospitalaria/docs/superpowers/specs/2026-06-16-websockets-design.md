# WebSockets — Actualización automática de tablas

## Problema

Las tablas de pacientes (guardia, mis pacientes, activos en recepción) solo se actualizan cuando el usuario recarga la página o navega entre secciones. Si un médico toma un paciente o recepción registra un ingreso nuevo, los demás usuarios no ven el cambio hasta que recargan manualmente.

## Solución

Implementar WebSockets para que el backend notifique a todos los clientes conectados cuando ocurre un cambio relevante. Los clientes recargan sus propios datos al recibir la notificación.

## Alcance

- Notificar cuando se crea un ingreso nuevo (`POST /ingresos/`)
- Notificar cuando cambia el estado de un ingreso (`PATCH /ingresos/{id}/estado`)
- Notificar cuando se asigna un médico (`PATCH /ingresos/{id}/medico`)
- No notificar cambios de observaciones (no afectan las tablas)
- Actualizar automáticamente: `TablaGuardia`, `TablaActivosMedico`, `TablaIngresosActivos`

## Fuera de alcance

- Comunicación cliente → servidor por WebSocket (todas las acciones siguen siendo REST)
- Notificaciones específicas por tipo de evento (el cliente recarga todo al recibir cualquier mensaje)
- Autenticación del WebSocket

---

## Arquitectura

```
[recepción crea ingreso]
        │
        ▼
FastAPI endpoint POST /ingresos/
        │
        ├─→ guarda en BD
        │
        └─→ manager.broadcast({"tipo": "actualizacion"})
                    │
                    ├─→ WS cliente 1 (médico en /medico/guardia)
                    ├─→ WS cliente 2 (médico en /medico/activos)
                    └─→ WS cliente 3 (recepción en /recepcion/activos)
```

---

## Backend

### `backend/ws/connection_manager.py` — CREAR

Singleton que gestiona las conexiones WebSocket activas.

```python
from fastapi import WebSocket
from typing import List

class ConnectionManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)

    async def broadcast(self, message: dict):
        for connection in list(self.active_connections):
            try:
                await connection.send_json(message)
            except Exception:
                self.active_connections.remove(connection)

manager = ConnectionManager()
```

**Notas de diseño:**
- `list(self.active_connections)` en broadcast para evitar mutación del iterable si se desconecta un cliente durante el envío
- `try/except` en broadcast: si un cliente se desconectó sin avisar, no rompe el resto del broadcast
- `manager` se instancia a nivel módulo para compartirse entre routers vía import

### `backend/main.py` — MODIFICAR

Agregar el endpoint WebSocket:

```python
from fastapi import WebSocket, WebSocketDisconnect
from ws.connection_manager import manager

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await manager.connect(websocket)
    try:
        while True:
            await websocket.receive_text()  # mantiene la conexión viva
    except WebSocketDisconnect:
        manager.disconnect(websocket)
```

**Nota:** `receive_text()` en loop es necesario para detectar desconexión. El servidor no procesa lo que recibe — solo lo descarta.

### `backend/routers/ingreso_guardia.py` — MODIFICAR

Agregar `await manager.broadcast({"tipo": "actualizacion"})` al final de los tres endpoints relevantes:

- `crear_ingreso` — después del return (antes del response, usando background task o llamando antes)
- `cambiar_estado` — después del return del service
- `asignar_medico` — después del return del service

Patrón en cada endpoint:

```python
from fastapi import BackgroundTasks
from ws.connection_manager import manager

@router.post("/", ...)
def crear_ingreso(data: ..., background_tasks: BackgroundTasks, db: Session = Depends(get_db)):
    ingreso = ingreso_service.crear_ingreso(db, data)
    background_tasks.add_task(manager.broadcast, {"tipo": "actualizacion"})
    return ingreso
```

**Nota:** Los endpoints existentes son síncronos (`def`, no `async def`). Para llamar a `manager.broadcast()` (que es `async`) desde un endpoint síncrono se usan `BackgroundTasks` de FastAPI — se ejecutan después de devolver la respuesta, sin bloquear. `BackgroundTasks` se inyecta como parámetro de la función (FastAPI lo detecta automáticamente).

---

## Frontend

### `frontend/composables/useWebSocket.js` — CREAR

Composable que gestiona la conexión WebSocket con reconexión automática.

```js
import { onMounted, onUnmounted } from 'vue'

export function useWebSocket(onMessage) {
  let ws = null
  let reconnectTimeout = null

  function connect() {
    ws = new WebSocket('ws://localhost:8000/ws')

    ws.onmessage = () => onMessage()

    ws.onclose = () => {
      reconnectTimeout = setTimeout(connect, 3000)
    }

    ws.onerror = () => {
      ws.close()
    }
  }

  onMounted(connect)

  onUnmounted(() => {
    clearTimeout(reconnectTimeout)
    ws?.close()
  })
}
```

**Notas de diseño:**
- `onMessage` recibe el evento pero no lo usa — los componentes recargan todo sin distinguir tipo de cambio
- `onerror` cierra el socket para forzar `onclose` y así activar la reconexión
- `clearTimeout` en `onUnmounted` evita intentos de reconexión después de que el componente se desmontó
- Sin lógica de backoff exponencial — 3 segundos fijos es suficiente para uso local

### Integración en componentes — MODIFICAR 3 archivos

**`frontend/components/TablaGuardia.vue`** y **`frontend/components/TablaActivosMedico.vue`** cargan sus propios datos, así que el composable va directo en el componente:

```js
import { useWebSocket } from '~/composables/useWebSocket'

// En <script setup>, después de definir cargarIngresos:
useWebSocket(cargarIngresos)
```

**`frontend/pages/recepcion/activos.vue`** — `TablaIngresosActivos` recibe datos vía prop desde la página, así que el composable va en la página:

```js
import { useWebSocket } from '~/composables/useWebSocket'

// En <script setup>, después de definir cargarIngresos:
useWebSocket(cargarIngresos)
```

El `onMounted` ya existente en cada archivo sigue cargando los datos iniciales. El WebSocket solo recarga cuando llega una notificación.

---

## Flujo completo

1. Médico abre `/medico/guardia` → `TablaGuardia` conecta WS → servidor acepta conexión
2. Recepción registra un ingreso nuevo → `POST /ingresos/` → servidor hace broadcast
3. `TablaGuardia` recibe mensaje → llama `cargarIngresos()` → tabla se actualiza sola
4. Médico cierra pestaña → WS se cierra → servidor detecta `WebSocketDisconnect` → elimina conexión

---

## Manejo de errores

- **Backend cae:** `ws.onclose` dispara en el frontend → reintenta cada 3 segundos hasta que vuelva
- **Cliente se desconecta sin avisar (crash, corte de red):** el `try/except` en `broadcast` descarta esa conexión y continúa con las demás
- **Error al hacer broadcast a un cliente:** no interrumpe el broadcast al resto
- **Sin clientes conectados:** `broadcast` itera sobre lista vacía, sin efecto

---

## Sin cambios de backend adicionales

Los tests existentes no necesitan modificarse — `ConnectionManager` no toca la lógica de negocio ni los schemas. El broadcast es un efecto secundario de los endpoints, no una responsabilidad del service layer.
