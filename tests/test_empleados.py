# Test para crear un empleado
def test_crear_empleado(client):
    response = client.post(
        "/api/v1/empleados/",
        json={"cedula": 123456789, "nombre": "Juan Perez", "rol": "Operario"},
    )
    assert response.status_code == 201
    assert response.json()["cedula"] == 123456789
    assert response.json()["nombre"] == "Juan Perez"

# Test para crear un empleado ya existente
def test_crear_empleado_duplicado(client):
    client.post(
        "/api/v1/empleados/",
        json={"cedula": 123456789, "nombre": "Juan Perez", "rol": "Operario"},
    )
    response = client.post(
        "/api/v1/empleados/",
        json={"cedula": 123456789, "nombre": "Juan Perez", "rol": "Operario"},
    )
    assert response.status_code == 409

# Test para listar empleados
def test_listar_empleados(client):
    client.post(
        "/api/v1/empleados/",
        json={"cedula": 111111111, "nombre": "Ana Lopez", "rol": "Supervisor"},
    )
    response = client.get("/api/v1/empleados/")
    assert response.status_code == 200
    assert len(response.json()) == 1

# Test para obtener un empleado
def test_obtener_empleado(client):
    client.post(
        "/api/v1/empleados/",
        json={"cedula": 123456789, "nombre": "Juan Perez", "rol": "Operario"},
    )
    response = client.get("/api/v1/empleados/123456789")
    assert response.status_code == 200
    assert response.json()["cedula"] == 123456789

# Test para obtener un emplado no existente
def test_obtener_empleado_no_existe(client):
    response = client.get("/api/v1/empleados/999999999")
    assert response.status_code == 404

# Test para actualizar un empleado
def test_actualizar_empleado(client):
    client.post(
        "/api/v1/empleados/",
        json={"cedula": 123456789, "nombre": "Juan Perez", "rol": "Operario"},
    )
    response = client.patch(
        "/api/v1/empleados/123456789", json={"nombre": "Juan Actualizado"}
    )
    assert response.status_code == 200
    assert response.json()["nombre"] == "Juan Actualizado"

# Test para actualizar un empleado no existente
def test_actualizar_empleado_no_existe(client):
    response = client.patch("/api/v1/empleados/999999999", json={"nombre": "No existe"})
    assert response.status_code == 404

# Test para eliminar un empleado
def test_eliminar_empleado(client):
    client.post(
        "/api/v1/empleados/",
        json={"cedula": 123456789, "nombre": "Juan Perez", "rol": "Operario"},
    )
    response = client.delete("/api/v1/empleados/123456789")
    assert response.status_code == 204

# Test para eliminar un empleado no existente
def test_eliminar_empleado_no_existe(client):
    response = client.delete("/api/v1/empleados/999999999")
    assert response.status_code == 404
