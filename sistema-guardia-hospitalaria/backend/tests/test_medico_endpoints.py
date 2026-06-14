MEDICO_DATA = {
    "nombre": "Carlos",
    "apellido": "López",
    "matricula": "MN12345",
    "especialidad": "Clínica Médica",
    "username": "drlopez",
    "password": "secreto123",
}

MEDICO_DATA_2 = {
    "nombre": "Ana",
    "apellido": "Martínez",
    "matricula": "MN67890",
    "especialidad": "Guardia",
    "username": "drmartinez",
    "password": "secreto123",
}


def test_crear_medico_retorna_201(client):
    response = client.post("/medicos/", json=MEDICO_DATA)
    assert response.status_code == 201


def test_crear_medico_retorna_datos(client):
    response = client.post("/medicos/", json=MEDICO_DATA)
    data = response.json()
    assert data["nombre"] == MEDICO_DATA["nombre"]
    assert data["apellido"] == MEDICO_DATA["apellido"]
    assert data["matricula"] == MEDICO_DATA["matricula"]
    assert data["especialidad"] == MEDICO_DATA["especialidad"]
    assert "id" in data


def test_crear_medico_sin_especialidad_retorna_422(client):
    data = {k: v for k, v in MEDICO_DATA.items() if k != "especialidad"}
    response = client.post("/medicos/", json=data)
    assert response.status_code == 422


def test_crear_medico_matricula_duplicada_retorna_409(client):
    client.post("/medicos/", json=MEDICO_DATA)
    response = client.post("/medicos/", json=MEDICO_DATA)
    assert response.status_code == 409


def test_listar_medicos_lista_vacia(client):
    response = client.get("/medicos/")
    assert response.status_code == 200
    assert response.json() == []


def test_listar_medicos_retorna_todos(client):
    client.post("/medicos/", json=MEDICO_DATA)
    client.post("/medicos/", json=MEDICO_DATA_2)
    response = client.get("/medicos/")
    assert response.status_code == 200
    assert len(response.json()) == 2


PACIENTE_DATA = {
    "dni": "55555555",
    "nombre": "Marta",
    "apellido": "Ruiz",
    "fecha_nacimiento": "1980-03-10",
}


def test_medicos_con_carga_lista_vacia(client):
    response = client.get("/medicos/con-carga")
    assert response.status_code == 200
    assert response.json() == []


def test_medicos_con_carga_sin_ingresos(client):
    client.post("/medicos/", json=MEDICO_DATA)
    response = client.get("/medicos/con-carga")
    data = response.json()
    assert len(data) == 1
    assert data[0]["pacientes_en_espera"] == 0


def test_medicos_con_carga_cuenta_en_espera(client):
    medico = client.post("/medicos/", json=MEDICO_DATA).json()
    paciente = client.post("/pacientes/", json=PACIENTE_DATA).json()
    ingreso = client.post(
        "/ingresos/", json={"paciente_id": paciente["id"], "prioridad": "ALTA"}
    ).json()
    client.patch(f"/ingresos/{ingreso['id']}/medico", json={"medico_id": medico["id"]})

    response = client.get("/medicos/con-carga")
    data = response.json()
    assert data[0]["pacientes_en_espera"] == 1


def test_medicos_con_carga_estado_personalizado(client):
    medico = client.post("/medicos/", json=MEDICO_DATA).json()
    paciente = client.post("/pacientes/", json=PACIENTE_DATA).json()
    ingreso = client.post(
        "/ingresos/", json={"paciente_id": paciente["id"], "prioridad": "ALTA"}
    ).json()
    client.patch(f"/ingresos/{ingreso['id']}/medico", json={"medico_id": medico["id"]})
    client.patch(f"/ingresos/{ingreso['id']}/estado", json={"estado": "EN_ATENCION"})

    en_espera = client.get("/medicos/con-carga?estado=EN_ESPERA").json()
    en_atencion = client.get("/medicos/con-carga?estado=EN_ATENCION").json()
    assert en_espera[0]["pacientes_en_espera"] == 0
    assert en_atencion[0]["pacientes_en_espera"] == 1
