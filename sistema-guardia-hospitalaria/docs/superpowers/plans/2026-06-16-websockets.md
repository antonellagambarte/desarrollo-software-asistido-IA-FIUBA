# WebSockets — Actualización automática de tablas

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Implementar WebSockets para que el backend notifique a todos los clientes cuando hay un cambio en ingresos, y las tablas del médico y de recepción se actualicen automáticamente.

**Architecture:** Un `ConnectionManager` singleton gestiona las conexiones WebSocket activas. Los endpoints `crear_ingreso`, `cambiar_estado` y `asignar_medico` hacen broadcast via `BackgroundTasks` después de responder. El frontend conecta con un composable `useWebSocket` que llama a `cargarIngresos` al recibir cualquier mensaje.

**Tech Stack:** FastAPI (WebSocket, BackgroundTasks), pytest + AsyncMock (tests), Vue 3 / Nuxt 3 (composable + WebSocket API nativa del browser).

---

## Archivos

| Archivo | Acción |
|---|---|
| `backend/ws/__init__.py` | CREAR (vacío) |
| `backend/ws/connection_manager.py` | CREAR |
| `backend/main.py` | MODIFICAR (agregar endpoint `/ws`) |
| `backend/routers/ingreso_guardia.py` | MODIFICAR (agregar broadcast a 3 endpoints) |
| `backend/tests/test_websocket.py` | CREAR |
| `frontend/composables/useWebSocket.js` | CREAR |
| `frontend/components/TablaGuardia.vue` | MODIFICAR (1 import + 1 línea) |
| `frontend/components/TablaActivosMedico.vue` | MODIFICAR (1 import + 1 línea) |
| `frontend/components/TablaIngresosActivos.vue` | MODIFICAR (1 import + 1 línea) |

---

## Task 1: Backend — ConnectionManager

**Archivos:**
- Crear: `backend/ws/__init__.py`
- Crear: `backend/ws/connection_manager.py`
- Crear: `backend/tests/test_websocket.py` (solo unit tests del manager en este task)

- [ ] **Step 1: Crear el directorio y el archivo vacío `__init__.py`**

```bash
mkdir -p backend/ws
touch backend/ws/__init__.py
```

- [ ] **Step 2: Escribir los unit tests del ConnectionManager (fallan porque el módulo no existe)**

Crear `backend/tests/test_websocket.py` con:

```python
import asyncio
from unittest.mock import AsyncMock, MagicMock
from ws.connection_manager import ConnectionManager

PACIENTE_DATA = {
    "dni": "22222222",
    "nombre": "Ana",
    "apellido": "Torres",
    "fecha_nacimiento": "1990-01-01",
}

MEDICO_DATA = {
    "nombre": "Carlos",
    "apellido": "Ruiz",
    "matricula": "MN88888",
    "especialidad": "Guardia",
    "username": "drruiz",
    "password": "clave123",
}


def test_connect_agrega_websocket():
    manager = ConnectionManager()
    mock_ws = MagicMock()
    mock_ws.accept = AsyncMock()
    asyncio.run(manager.connect(mock_ws))
    assert mock_ws in manager.active_connections


def test_disconnect_elimina_websocket():
    manager = ConnectionManager()
    mock_ws = MagicMock()
    manager.active_connections.append(mock_ws)
    manager.disconnect(mock_ws)
    assert mock_ws not in manager.active_connections


def test_disconnect_es_idempotente():
    manager = ConnectionManager()
    mock_ws = MagicMock()
    manager.disconnect(mock_ws)  # no debe lanzar error


def test_broadcast_envia_a_todas_las_conexiones():
    manager = ConnectionManager()
    ws1, ws2 = MagicMock(), MagicMock()
    ws1.send_json = AsyncMock()
    ws2.send_json = AsyncMock()
    manager.active_connections.extend([ws1, ws2])
    asyncio.run(manager.broadcast({"tipo": "actualizacion"}))
    ws1.send_json.assert_called_once_with({"tipo": "actualizacion"})
    ws2.send_json.assert_called_once_with({"tipo": "actualizacion"})


def test_broadcast_elimina_conexion_caida():
    manager = ConnectionManager()
    mock_ws = MagicMock()
    mock_ws.send_json = AsyncMock(side_effect=Exception("connection lost"))
    manager.active_connections.append(mock_ws)
    asyncio.run(manager.broadcast({"tipo": "actualizacion"}))
    assert mock_ws not in manager.active_connections


def test_broadcast_con_lista_vacia_no_falla():
    manager = ConnectionManager()
    asyncio.run(manager.broadcast({"tipo": "actualizacion"}))
```

- [ ] **Step 3: Verificar que los tests fallan**

```bash
cd backend
python -m pytest tests/test_websocket.py -v
```

Esperado: 6 tests en ERROR con `ModuleNotFoundError: No module named 'ws.connection_manager'`.

- [ ] **Step 4: Crear `backend/ws/connection_manager.py`**

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
        if websocket in self.active_connections:
            self.active_connections.remove(websocket)

    async def broadcast(self, message: dict):
        for connection in list(self.active_connections):
            try:
                await connection.send_json(message)
            except Exception:
                self.disconnect(connection)


manager = ConnectionManager()
```

- [ ] **Step 5: Verificar que los unit tests pasan**

```bash
cd backend
python -m pytest tests/test_websocket.py -v
```

Esperado: 6 tests en PASSED.

- [ ] **Step 6: Commit**

```bash
git add backend/ws/__init__.py backend/ws/connection_manager.py backend/tests/test_websocket.py
git commit -m "feat: ConnectionManager para WebSockets con unit tests"
```

---

## Task 2: Backend — Endpoint `/ws` y broadcast en routers

**Archivos:**
- Modificar: `backend/main.py`
- Modificar: `backend/routers/ingreso_guardia.py`
- Modificar: `backend/tests/test_websocket.py` (agregar integration tests)

- [ ] **Step 1: Agregar integration tests al final de `backend/tests/test_websocket.py`**

Agregar debajo de los unit tests existentes:

```python
import pytest


@pytest.fixture
def paciente_id(client):
    resp = client.post("/pacientes/", json=PACIENTE_DATA)
    return resp.json()["id"]


@pytest.fixture
def medico_id(client):
    resp = client.post("/medicos/", json=MEDICO_DATA)
    return resp.json()["id"]


@pytest.fixture
def ingreso_id(client, paciente_id):
    resp = client.post("/ingresos/", json={"paciente_id": paciente_id, "prioridad": "BAJA"})
    return resp.json()["id"]


def test_websocket_acepta_conexion(client):
    with client.websocket_connect("/ws") as ws:
        pass


def test_broadcast_al_crear_ingreso(client, paciente_id):
    with client.websocket_connect("/ws") as ws:
        client.post("/ingresos/", json={"paciente_id": paciente_id, "prioridad": "MEDIA"})
        data = ws.receive_json()
        assert data == {"tipo": "actualizacion"}


def test_broadcast_al_cambiar_estado(client, ingreso_id):
    with client.websocket_connect("/ws") as ws:
        client.patch(f"/ingresos/{ingreso_id}/estado", json={"estado": "EN_ATENCION"})
        data = ws.receive_json()
        assert data == {"tipo": "actualizacion"}


def test_broadcast_al_asignar_medico(client, ingreso_id, medico_id):
    with client.websocket_connect("/ws") as ws:
        client.patch(f"/ingresos/{ingreso_id}/medico", json={"medico_id": medico_id})
        data = ws.receive_json()
        assert data == {"tipo": "actualizacion"}


def test_sin_broadcast_al_actualizar_observaciones(client, ingreso_id):
    client.patch(f"/ingresos/{ingreso_id}/estado", json={"estado": "EN_ATENCION"})
    response = client.patch(
        f"/ingresos/{ingreso_id}/observaciones",
        json={"observaciones": "Sin novedad"},
    )
    assert response.status_code == 200
```

- [ ] **Step 2: Verificar que los integration tests fallan**

```bash
cd backend
python -m pytest tests/test_websocket.py::test_websocket_acepta_conexion -v
```

Esperado: FAILED con error 404 (endpoint `/ws` no existe todavía).

- [ ] **Step 3: Agregar el endpoint WebSocket en `backend/main.py`**

Reemplazar el contenido de `backend/main.py` con:

```python
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from database import Base, engine
import models  # noqa: F401 — registers all models so create_all includes all tables
from routers.paciente import router as paciente_router
from routers.medico import router as medico_router
from routers.ingreso_guardia import router as ingreso_router
from routers.auth import router as auth_router
from ws.connection_manager import manager

Base.metadata.create_all(bind=engine)

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:3001"],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(paciente_router)
app.include_router(medico_router)
app.include_router(ingreso_router)
app.include_router(auth_router)


@app.get("/")
def root():
    return {"status": "ok"}


@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await manager.connect(websocket)
    try:
        while True:
            await websocket.receive_text()
    except WebSocketDisconnect:
        manager.disconnect(websocket)
```

- [ ] **Step 4: Modificar `backend/routers/ingreso_guardia.py` para agregar broadcast**

Reemplazar el contenido completo con:

```python
from typing import List, Optional
from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException, status
from sqlalchemy.orm import Session
from dependencies import get_db
from models.ingreso_guardia import EstadoIngreso
from schemas.ingreso_guardia import (
    IngresoGuardiaCreate,
    IngresoGuardiaResponse,
    CambioEstadoRequest,
    AsignacionMedicoRequest,
    ActualizarObservacionesRequest,
    ActualizarObservacionesMedicoRequest,
)
from services import ingreso_guardia as ingreso_service
from ws.connection_manager import manager

router = APIRouter(prefix="/ingresos", tags=["ingresos"])

_ACTUALIZACION = {"tipo": "actualizacion"}


@router.post("/", response_model=IngresoGuardiaResponse, status_code=status.HTTP_201_CREATED)
def crear_ingreso(data: IngresoGuardiaCreate, background_tasks: BackgroundTasks, db: Session = Depends(get_db)):
    try:
        ingreso = ingreso_service.crear_ingreso(db, data)
        background_tasks.add_task(manager.broadcast, _ACTUALIZACION)
        return ingreso
    except LookupError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))


@router.get("/", response_model=List[IngresoGuardiaResponse])
def listar_ingresos(estado: Optional[EstadoIngreso] = None, db: Session = Depends(get_db)):
    return ingreso_service.obtener_ingresos(db, estado)


@router.patch("/{ingreso_id}/estado", response_model=IngresoGuardiaResponse)
def cambiar_estado(ingreso_id: int, data: CambioEstadoRequest, background_tasks: BackgroundTasks, db: Session = Depends(get_db)):
    try:
        ingreso = ingreso_service.cambiar_estado(db, ingreso_id, data.estado)
        background_tasks.add_task(manager.broadcast, _ACTUALIZACION)
        return ingreso
    except LookupError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.patch("/{ingreso_id}/medico", response_model=IngresoGuardiaResponse)
def asignar_medico(ingreso_id: int, data: AsignacionMedicoRequest, background_tasks: BackgroundTasks, db: Session = Depends(get_db)):
    try:
        ingreso = ingreso_service.asignar_medico(db, ingreso_id, data.medico_id)
        background_tasks.add_task(manager.broadcast, _ACTUALIZACION)
        return ingreso
    except LookupError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))


@router.patch("/{ingreso_id}/observaciones", response_model=IngresoGuardiaResponse)
def actualizar_observaciones(ingreso_id: int, data: ActualizarObservacionesRequest, db: Session = Depends(get_db)):
    try:
        return ingreso_service.actualizar_observaciones(db, ingreso_id, data.observaciones)
    except LookupError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.patch("/{ingreso_id}/observaciones-medico", response_model=IngresoGuardiaResponse)
def actualizar_observaciones_medico(ingreso_id: int, data: ActualizarObservacionesMedicoRequest, db: Session = Depends(get_db)):
    try:
        return ingreso_service.actualizar_observaciones_medico(db, ingreso_id, data.observaciones_medico)
    except LookupError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
```

- [ ] **Step 5: Verificar que todos los tests pasan**

```bash
cd backend
python -m pytest --tb=short -q
```

Esperado: todos los tests existentes + los 11 nuevos en PASSED.

- [ ] **Step 6: Commit**

```bash
git add backend/main.py backend/routers/ingreso_guardia.py backend/tests/test_websocket.py
git commit -m "feat: endpoint /ws y broadcast en crear_ingreso, cambiar_estado, asignar_medico"
```

---

## Task 3: Frontend — composable useWebSocket + integración en 3 componentes

**Archivos:**
- Crear: `frontend/composables/useWebSocket.js`
- Modificar: `frontend/components/TablaGuardia.vue`
- Modificar: `frontend/components/TablaActivosMedico.vue`
- Modificar: `frontend/components/TablaIngresosActivos.vue`

- [ ] **Step 1: Crear `frontend/composables/useWebSocket.js`**

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

- [ ] **Step 2: Integrar en `frontend/components/TablaGuardia.vue`**

En `<script setup>`, agregar el import junto a los otros imports existentes:

```js
import { useWebSocket } from '~/composables/useWebSocket'
```

Y agregar esta línea después de la definición de `cargarIngresos`:

```js
useWebSocket(cargarIngresos)
```

El import de `ref` y `onMounted` ya existe — no modificar.

- [ ] **Step 3: Integrar en `frontend/components/TablaActivosMedico.vue`**

En `<script setup>`, agregar el import:

```js
import { useWebSocket } from '~/composables/useWebSocket'
```

Y agregar después de la definición de `cargarIngresos`:

```js
useWebSocket(cargarIngresos)
```

- [ ] **Step 4: Integrar en `frontend/components/TablaIngresosActivos.vue`**

En `<script setup>`, agregar el import:

```js
import { useWebSocket } from '~/composables/useWebSocket'
```

Y agregar después de la definición de `cargarIngresos`:

```js
useWebSocket(cargarIngresos)
```

- [ ] **Step 5: Verificar que los tests del backend siguen pasando**

```bash
cd backend
python -m pytest --tb=short -q
```

Esperado: todos los tests en PASSED. (Los cambios de frontend no afectan los tests.)

- [ ] **Step 6: Commit**

```bash
git add frontend/composables/useWebSocket.js frontend/components/TablaGuardia.vue frontend/components/TablaActivosMedico.vue frontend/components/TablaIngresosActivos.vue
git commit -m "feat: composable useWebSocket y actualización automática en las tres tablas"
```
