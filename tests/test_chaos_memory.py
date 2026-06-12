from app import main as main_module


def teardown_function():
    main_module._chaos_memory_store.clear()


def test_chaos_acumular_memoria_libera_y_responde_429(client, monkeypatch):
    main_module._chaos_memory_store.append("residuo")
    monkeypatch.setattr(main_module, "_CHAOS_MEMORY_LIMIT_MB", 0)

    response = client.get("/chaos/acumular-memoria?mb=1")

    assert response.status_code == 429
    assert (
        response.json()["detail"]["error"]
        == "Límite alcanzado — memoria liberada automáticamente"
    )
    assert main_module._chaos_memory_store == []


def test_chaos_liberar_memoria_vacia_el_buffer(client):
    main_module._chaos_memory_store.extend(["a", "b"])

    response = client.delete("/chaos/liberar-memoria")

    assert response.status_code == 200
    assert response.json()["liberado_MB"] >= 0
    assert main_module._chaos_memory_store == []
