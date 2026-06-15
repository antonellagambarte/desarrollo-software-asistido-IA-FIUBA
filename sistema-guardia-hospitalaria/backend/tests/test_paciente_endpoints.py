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


def test_buscar_pacientes_por_nombre(client):
    client.post("/pacientes/", json=PACIENTE_DATA)          # Juan Pérez
    client.post("/pacientes/", json=PACIENTE_SIN_TELEFONO)  # María García
    response = client.get("/pacientes/?q=juan")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert data[0]["nombre"] == "Juan"


def test_buscar_pacientes_por_apellido(client):
    client.post("/pacientes/", json=PACIENTE_DATA)
    client.post("/pacientes/", json=PACIENTE_SIN_TELEFONO)
    response = client.get("/pacientes/?q=garc")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert data[0]["apellido"] == "García"


def test_buscar_pacientes_por_dni_parcial(client):
    client.post("/pacientes/", json=PACIENTE_DATA)          # DNI 12345678
    client.post("/pacientes/", json=PACIENTE_SIN_TELEFONO)  # DNI 87654321
    response = client.get("/pacientes/?q=1234")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert data[0]["dni"] == "12345678"


def test_buscar_pacientes_sin_resultados(client):
    client.post("/pacientes/", json=PACIENTE_DATA)
    response = client.get("/pacientes/?q=xyz_no_existe")
    assert response.status_code == 200
    assert response.json() == []


def test_buscar_pacientes_q_vacio_retorna_lista_vacia(client):
    client.post("/pacientes/", json=PACIENTE_DATA)
    response = client.get("/pacientes/?q=")
    assert response.status_code == 200
    assert response.json() == []
