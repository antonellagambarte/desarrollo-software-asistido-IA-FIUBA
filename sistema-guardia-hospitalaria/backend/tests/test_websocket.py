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
