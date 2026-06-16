import asyncio
import pytest
import ws.connection_manager
from unittest.mock import AsyncMock, MagicMock, patch
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
    with patch.object(ws.connection_manager.manager, "broadcast", new_callable=AsyncMock) as mock_broadcast:
        response = client.patch(
            f"/ingresos/{ingreso_id}/observaciones",
            json={"observaciones": "Sin novedad"},
        )
        assert response.status_code == 200
        mock_broadcast.assert_not_called()


def test_sin_broadcast_al_actualizar_observaciones_medico(client, ingreso_id):
    client.patch(f"/ingresos/{ingreso_id}/estado", json={"estado": "EN_ATENCION"})
    with patch.object(ws.connection_manager.manager, "broadcast", new_callable=AsyncMock) as mock_broadcast:
        response = client.patch(
            f"/ingresos/{ingreso_id}/observaciones-medico",
            json={"observaciones_medico": "Paciente estable"},
        )
        assert response.status_code == 200
        mock_broadcast.assert_not_called()
