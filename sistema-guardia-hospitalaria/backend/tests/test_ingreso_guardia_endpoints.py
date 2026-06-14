import pytest

PACIENTE_DATA = {
    "dni": "11111111",
    "nombre": "Laura",
    "apellido": "Gómez",
    "fecha_nacimiento": "1995-08-20",
}

MEDICO_DATA = {
    "nombre": "Roberto",
    "apellido": "Silva",
    "matricula": "MN99999",
    "especialidad": "Guardia",
    "username": "drsilva",
    "password": "secreto123",
}


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
    resp = client.post("/ingresos/", json={"paciente_id": paciente_id, "prioridad": "ALTA"})
    return resp.json()["id"]


# --- POST /ingresos/ ---

def test_crear_ingreso_retorna_201(client, paciente_id):
    response = client.post("/ingresos/", json={"paciente_id": paciente_id, "prioridad": "MEDIA"})
    assert response.status_code == 201


def test_crear_ingreso_estado_inicial_en_espera(client, paciente_id):
    response = client.post("/ingresos/", json={"paciente_id": paciente_id, "prioridad": "BAJA"})
    assert response.json()["estado"] == "EN_ESPERA"


def test_crear_ingreso_con_observaciones(client, paciente_id):
    response = client.post(
        "/ingresos/",
        json={"paciente_id": paciente_id, "prioridad": "ALTA", "observaciones": "Dolor agudo"},
    )
    assert response.status_code == 201
    assert response.json()["observaciones"] == "Dolor agudo"


def test_crear_ingreso_incluye_datos_del_paciente(client, paciente_id):
    response = client.post("/ingresos/", json={"paciente_id": paciente_id, "prioridad": "MEDIA"})
    data = response.json()
    assert data["paciente"]["dni"] == PACIENTE_DATA["dni"]


def test_crear_ingreso_paciente_inexistente_retorna_404(client):
    response = client.post("/ingresos/", json={"paciente_id": 9999, "prioridad": "BAJA"})
    assert response.status_code == 404


# --- GET /ingresos/ ---

def test_listar_ingresos_vacio(client):
    response = client.get("/ingresos/")
    assert response.status_code == 200
    assert response.json() == []


def test_listar_ingresos_sin_filtro(client, paciente_id):
    client.post("/ingresos/", json={"paciente_id": paciente_id, "prioridad": "BAJA"})
    client.post("/ingresos/", json={"paciente_id": paciente_id, "prioridad": "ALTA"})
    response = client.get("/ingresos/")
    assert len(response.json()) == 2


def test_listar_ingresos_filtro_estado(client, ingreso_id):
    client.patch(f"/ingresos/{ingreso_id}/estado", json={"estado": "EN_ATENCION"})
    en_espera = client.get("/ingresos/?estado=EN_ESPERA").json()
    en_atencion = client.get("/ingresos/?estado=EN_ATENCION").json()
    assert len(en_espera) == 0
    assert len(en_atencion) == 1


# --- PATCH /ingresos/{id}/estado ---

def test_cambiar_estado_en_espera_a_en_atencion(client, ingreso_id):
    response = client.patch(f"/ingresos/{ingreso_id}/estado", json={"estado": "EN_ATENCION"})
    assert response.status_code == 200
    assert response.json()["estado"] == "EN_ATENCION"


def test_cambiar_estado_en_atencion_a_alta(client, ingreso_id):
    client.patch(f"/ingresos/{ingreso_id}/estado", json={"estado": "EN_ATENCION"})
    response = client.patch(f"/ingresos/{ingreso_id}/estado", json={"estado": "ALTA"})
    assert response.status_code == 200
    assert response.json()["estado"] == "ALTA"


def test_cambiar_estado_transicion_invalida_retorna_400(client, ingreso_id):
    response = client.patch(f"/ingresos/{ingreso_id}/estado", json={"estado": "ALTA"})
    assert response.status_code == 400


def test_cambiar_estado_desde_alta_retorna_400(client, ingreso_id):
    client.patch(f"/ingresos/{ingreso_id}/estado", json={"estado": "EN_ATENCION"})
    client.patch(f"/ingresos/{ingreso_id}/estado", json={"estado": "ALTA"})
    response = client.patch(f"/ingresos/{ingreso_id}/estado", json={"estado": "EN_ESPERA"})
    assert response.status_code == 400


def test_cambiar_estado_ingreso_inexistente_retorna_404(client):
    response = client.patch("/ingresos/9999/estado", json={"estado": "EN_ATENCION"})
    assert response.status_code == 404


# --- PATCH /ingresos/{id}/medico ---

def test_asignar_medico(client, ingreso_id, medico_id):
    response = client.patch(f"/ingresos/{ingreso_id}/medico", json={"medico_id": medico_id})
    assert response.status_code == 200
    data = response.json()
    assert data["medico_id"] == medico_id
    assert data["medico"]["matricula"] == MEDICO_DATA["matricula"]


def test_asignar_medico_ingreso_inexistente_retorna_404(client, medico_id):
    response = client.patch("/ingresos/9999/medico", json={"medico_id": medico_id})
    assert response.status_code == 404


def test_asignar_medico_inexistente_retorna_404(client, ingreso_id):
    response = client.patch(f"/ingresos/{ingreso_id}/medico", json={"medico_id": 9999})
    assert response.status_code == 404
