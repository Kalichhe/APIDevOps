# Test para crear una labor
def test_crear_labor(client):
    response = client.post("/api/v1/labores/", json={
        "codigo_labor": "P01",
        "nombre": "Poda",
        "unidad_medida": "Hectarea",
        "precio": 50000.0
    })
    assert response.status_code == 201
    assert response.json()["codigo_labor"] == "P01"
    assert response.json()["nombre"] == "Poda"

# Test para crear una labor ya existente
def test_crear_labor_duplicada(client):
    client.post("/api/v1/labores/", json={
        "codigo_labor": "P01",
        "nombre": "Poda",
        "unidad_medida": "Hectarea",
        "precio": 50000.0
    })
    response = client.post("/api/v1/labores/", json={
        "codigo_labor": "P01",
        "nombre": "Poda",
        "unidad_medida": "Hectarea",
        "precio": 50000.0
    })
    assert response.status_code == 409

# Test para listar las labores
def test_listar_labores(client):
    client.post("/api/v1/labores/", json={
        "codigo_labor": "P01",
        "nombre": "Poda",
        "unidad_medida": "Hectarea",
        "precio": 50000.0
    })
    response = client.get("/api/v1/labores/")
    assert response.status_code == 200
    assert len(response.json()) == 1

# Test para obtener una labor
def test_obtener_labor(client):
    client.post("/api/v1/labores/", json={
        "codigo_labor": "P01",
        "nombre": "Poda",
        "unidad_medida": "Hectarea",
        "precio": 50000.0
    })
    response = client.get("/api/v1/labores/P01")
    assert response.status_code == 200
    assert response.json()["codigo_labor"] == "P01"

# Test para obtener una labor no existente
def test_obtener_labor_no_existe(client):
    response = client.get("/api/v1/labores/X99")
    assert response.status_code == 404

# Test para actualizar una labor
def test_actualizar_labor(client):
    client.post("/api/v1/labores/", json={
        "codigo_labor": "P01",
        "nombre": "Poda",
        "unidad_medida": "Hectarea",
        "precio": 50000.0
    })
    response = client.patch("/api/v1/labores/P01", json={
        "precio": 75000.0
    })
    assert response.status_code == 200
    assert response.json()["precio"] == 75000.0

# Test para actualizar una labor no existente
def test_actualizar_labor_no_existe(client):
    response = client.patch("/api/v1/labores/X99", json={
        "nombre": "No existe"
    })
    assert response.status_code == 404

# Test para eliminar una labor
def test_eliminar_labor(client):
    client.post("/api/v1/labores/", json={
        "codigo_labor": "P01",
        "nombre": "Poda",
        "unidad_medida": "Hectarea",
        "precio": 50000.0
    })
    response = client.delete("/api/v1/labores/P01")
    assert response.status_code == 204

# Test para eliminar una labor no existente
def test_eliminar_labor_no_existe(client):
    response = client.delete("/api/v1/labores/X99")
    assert response.status_code == 404