# Tests de empleados para API v2 (payload tipo mensaje/jsonDirector/jsonEmpleado)


def _mensaje_empleado(cedula: int, nombre: str, rol: str) -> dict:
    return {
        "jsonDirector": {
            "jsonEmpleado": {
                "cedula": cedula,
                "nombre": nombre,
                "rol": rol,
            }
        }
    }


def _mensaje_update(**kwargs) -> dict:
    return {"jsonDirector": {"jsonEmpleado": kwargs}}


# Test para crear un empleado en v2


def test_crear_empleado_v2(client):
    response = client.post(
        "/api/v2/empleados/",
        json=_mensaje_empleado(123456789, "Juan Perez", "Operario"),
    )
    assert response.status_code == 201
    data = response.json()
    assert data["jsonDirector"]["jsonEmpleado"]["cedula"] == 123456789
    assert data["jsonDirector"]["jsonEmpleado"]["nombre"] == "Juan Perez"


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
    assert data["jsonDirector"]["jsonEmpleado"]["nombre"] == "Juan Actualizado"
    assert data["jsonDirector"]["jsonEmpleado"]["rol"] == "Operario"


# Test para reemplazar empleado con PUT en v2


def test_reemplazar_empleado_v2(client):
    client.post(
        "/api/v2/empleados/",
        json=_mensaje_empleado(123456789, "Juan Perez", "Operario"),
    )
    response = client.put(
        "/api/v2/empleados/123456789",
        json={
            "jsonDirector": {
                "jsonEmpleado": {
                    "nombre": "Juan Reemplazado",
                    "rol": "Supervisor",
                }
            }
        },
    )
    assert response.status_code == 200
    data = response.json()
    assert data["jsonDirector"]["jsonEmpleado"]["nombre"] == "Juan Reemplazado"
    assert data["jsonDirector"]["jsonEmpleado"]["rol"] == "Supervisor"


# Test para PUT con campos faltantes (schema validation) en v2


def test_reemplazar_empleado_campos_faltantes_v2(client):
    client.post(
        "/api/v2/empleados/",
        json=_mensaje_empleado(123456789, "Juan Perez", "Operario"),
    )
    response = client.put(
        "/api/v2/empleados/123456789",
        json={"jsonDirector": {"jsonEmpleado": {"nombre": "Solo Nombre"}}},
    )
    assert response.status_code == 422
