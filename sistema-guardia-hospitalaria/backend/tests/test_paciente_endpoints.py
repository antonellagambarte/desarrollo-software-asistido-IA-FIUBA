PACIENTE_DATA = {
    "dni": "12345678",
    "nombre": "Juan",
    "apellido": "Pérez",
    "fecha_nacimiento": "1990-05-15",
    "telefono": "1122334455",
}

PACIENTE_SIN_TELEFONO = {
    "dni": "87654321",
    "nombre": "María",
    "apellido": "García",
    "fecha_nacimiento": "1985-03-22",
}


def test_crear_paciente_retorna_201(client):
    response = client.post("/pacientes/", json=PACIENTE_DATA)
    assert response.status_code == 201


def test_crear_paciente_retorna_datos(client):
    response = client.post("/pacientes/", json=PACIENTE_DATA)
    data = response.json()
    assert data["dni"] == PACIENTE_DATA["dni"]
    assert data["nombre"] == PACIENTE_DATA["nombre"]
    assert data["apellido"] == PACIENTE_DATA["apellido"]
    assert "id" in data
    assert "edad" in data


def test_crear_paciente_sin_telefono(client):
    response = client.post("/pacientes/", json=PACIENTE_SIN_TELEFONO)
    assert response.status_code == 201
    assert response.json()["telefono"] is None


def test_crear_paciente_dni_duplicado_retorna_409(client):
    client.post("/pacientes/", json=PACIENTE_DATA)
    response = client.post("/pacientes/", json=PACIENTE_DATA)
    assert response.status_code == 409


def test_listar_pacientes_lista_vacia(client):
    response = client.get("/pacientes/")
    assert response.status_code == 200
    assert response.json() == []


def test_listar_pacientes_retorna_todos(client):
    client.post("/pacientes/", json=PACIENTE_DATA)
    client.post("/pacientes/", json=PACIENTE_SIN_TELEFONO)
    response = client.get("/pacientes/")
    assert response.status_code == 200
    assert len(response.json()) == 2


def test_obtener_paciente_por_dni(client):
    client.post("/pacientes/", json=PACIENTE_DATA)
    response = client.get(f"/pacientes/{PACIENTE_DATA['dni']}")
    assert response.status_code == 200
    assert response.json()["dni"] == PACIENTE_DATA["dni"]


def test_obtener_paciente_por_dni_no_encontrado(client):
    response = client.get("/pacientes/00000000")
    assert response.status_code == 404
