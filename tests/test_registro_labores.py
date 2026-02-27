# Datos reutilizables
EMPLEADO = {"cedula": 123456789, "nombre": "Juan Perez", "rol": "Operario"}
LABOR = {"codigo_labor": "P01", "nombre": "Poda", "unidad_medida": "Hectarea", "precio": 50000.0}
REGISTRO = {"id": 1, "empleado_cedula": 123456789, "codigo_labor": "P01", "fecha": "2024-01-15", "cantidad": 2.5}

# Test para crear empleado y labor
def crear_empleado_y_labor(client):
    client.post("/api/v1/empleados/", json=EMPLEADO)
    client.post("/api/v1/labores/", json=LABOR)

# Test para crear un registro de labor
def test_crear_registro_labor(client):
    crear_empleado_y_labor(client)
    response = client.post("/api/v1/registrolabores/", json=REGISTRO)
    assert response.status_code == 201
    assert response.json()["empleado_cedula"] == 123456789
    assert response.json()["codigo_labor"] == "P01"

# Test para crear un registro de empleado no existente
def test_crear_registro_empleado_no_existe(client):
    client.post("/api/v1/labores/", json=LABOR)
    response = client.post("/api/v1/registrolabores/", json={
        "id": 1, "empleado_cedula": 999999999, "codigo_labor": "P01", "fecha": "2024-01-15", "cantidad": 2.5
    })
    assert response.status_code == 404

# Test para crear un registro de labor no existente
def test_crear_registro_labor_no_existe(client):
    client.post("/api/v1/empleados/", json=EMPLEADO)
    response = client.post("/api/v1/registrolabores/", json={
        "id": 1, "empleado_cedula": 123456789, "codigo_labor": "X99", "fecha": "2024-01-15", "cantidad": 2.5
    })
    assert response.status_code == 404

# Test para listar los registros
def test_listar_registros(client):
    crear_empleado_y_labor(client)
    client.post("/api/v1/registrolabores/", json=REGISTRO)
    response = client.get("/api/v1/registrolabores/")
    assert response.status_code == 200
    assert len(response.json()) == 1

# Test para obtener registros por empleados
def test_obtener_registros_por_empleado(client):
    crear_empleado_y_labor(client)
    client.post("/api/v1/registrolabores/", json=REGISTRO)
    response = client.get("/api/v1/registrolabores/empleado/123456789")
    assert response.status_code == 200
    assert len(response.json()) == 1

# Test para obtener registros de empleados sin registros
def test_obtener_registros_empleado_sin_registros(client):
    client.post("/api/v1/empleados/", json=EMPLEADO)
    response = client.get("/api/v1/registrolabores/empleado/123456789")
    assert response.status_code == 404

# Test para actualizar registro
def test_actualizar_registro(client):
    crear_empleado_y_labor(client)
    crear = client.post("/api/v1/registrolabores/", json=REGISTRO)
    registro_id = crear.json()["id"]
    response = client.patch(f"/api/v1/registrolabores/{registro_id}", json={"cantidad": 5.0})
    assert response.status_code == 200
    assert response.json()["cantidad"] == 5.0

# Test para actualizar registro no existente
def test_actualizar_registro_no_existe(client):
    response = client.patch("/api/v1/registrolabores/999", json={"cantidad": 5.0})
    assert response.status_code == 404

# Test para eliminar un registro
def test_eliminar_registro(client):
    crear_empleado_y_labor(client)
    crear = client.post("/api/v1/registrolabores/", json=REGISTRO)
    registro_id = crear.json()["id"]
    response = client.delete(f"/api/v1/registrolabores/{registro_id}")
    assert response.status_code == 204

# Test para eliminar un registro no existente
def test_eliminar_registro_no_existe(client):
    response = client.delete("/api/v1/registrolabores/999")
    assert response.status_code == 404

# Test para no eliminar un empleado con registros asociados
def test_no_eliminar_empleado_con_registros(client):
    crear_empleado_y_labor(client)
    client.post("/api/v1/registrolabores/", json=REGISTRO)
    response = client.delete("/api/v1/empleados/123456789")
    assert response.status_code == 409

# Test para no eliminar una labor con registros asociados
def test_no_eliminar_labor_con_registros(client):
    crear_empleado_y_labor(client)
    client.post("/api/v1/registrolabores/", json=REGISTRO)
    response = client.delete("/api/v1/labores/P01")
    assert response.status_code == 409