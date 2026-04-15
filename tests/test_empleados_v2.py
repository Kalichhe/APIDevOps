# Tests de empleados para API v2 (payload con campos en raiz + jsonDirector.jsonDoctor)


def _mensaje_empleado(cedula: int, nombre: str, rol: str) -> dict:
    return {
        "cedula": cedula,
        "nombre": nombre,
        "rol": rol,
        "jsonDirector": {
            "nombre": "Director General",
            "jsonDoctor": {
                "documento": "CC",
                "nombres": "Juan",
                "apellidos": "Perez",
                "especialidad": "General",
                "durationCitaMinutos": 30,
            },
        },
    }


def _mensaje_update(**kwargs) -> dict:
    return kwargs


# Test para crear un empleado en v2


def test_crear_empleado_v2(client):
    response = client.post(
        "/api/v2/empleados/",
        json=_mensaje_empleado(123456789, "Juan Perez", "Operario"),
    )
    assert response.status_code == 201
    data = response.json()
    assert data["cedula"] == 123456789
    assert data["nombre"] == "Juan Perez"
    assert "data_json" not in data


# Test para crear empleado duplicado en v2


def test_crear_empleado_duplicado_v2(client):
    client.post(
        "/api/v2/empleados/",
        json=_mensaje_empleado(123456789, "Juan Perez", "Operario"),
    )
    response = client.post(
        "/api/v2/empleados/",
        json=_mensaje_empleado(123456789, "Juan Perez", "Operario"),
    )
    assert response.status_code == 409


# Test para obtener empleado en v2


def test_obtener_empleado_v2(client):
    client.post(
        "/api/v2/empleados/",
        json=_mensaje_empleado(123456789, "Juan Perez", "Operario"),
    )
    response = client.get("/api/v2/empleados/123456789")
    assert response.status_code == 200
    data = response.json()
    assert data["cedula"] == 123456789
    assert data["jsonDirector"]["nombre"] == "Director General"
    assert "data_json" not in data


# Test para listar empleados en v2


def test_listar_empleados_v2(client):
    client.post(
        "/api/v2/empleados/",
        json=_mensaje_empleado(123456789, "Juan Perez", "Operario"),
    )
    response = client.get("/api/v2/empleados/")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert data[0]["cedula"] == 123456789
    assert "data_json" not in data[0]


# Test para actualizar empleado con PATCH en v2


def test_actualizar_empleado_v2(client):
    client.post(
        "/api/v2/empleados/",
        json=_mensaje_empleado(123456789, "Juan Perez", "Operario"),
    )
    response = client.patch(
        "/api/v2/empleados/123456789",
        json=_mensaje_update(nombre="Juan Actualizado"),
    )
    assert response.status_code == 200
    data = response.json()
    assert data["nombre"] == "Juan Actualizado"
    assert data["rol"] == "Operario"
    assert "data_json" not in data


# Test para reemplazar empleado con PUT en v2


def test_reemplazar_empleado_v2(client):
    client.post(
        "/api/v2/empleados/",
        json=_mensaje_empleado(123456789, "Juan Perez", "Operario"),
    )
    response = client.put(
        "/api/v2/empleados/123456789",
        json={
            "nombre": "Juan Reemplazado",
            "rol": "Supervisor",
        },
    )
    assert response.status_code == 200
    data = response.json()
    assert data["nombre"] == "Juan Reemplazado"
    assert data["rol"] == "Supervisor"
    assert "data_json" not in data


# Test para PUT con campos faltantes (schema validation) en v2


def test_reemplazar_empleado_campos_faltantes_v2(client):
    client.post(
        "/api/v2/empleados/",
        json=_mensaje_empleado(123456789, "Juan Perez", "Operario"),
    )
    response = client.put(
        "/api/v2/empleados/123456789",
        json={"nombre": "Solo Nombre"},
    )
    assert response.status_code == 422
