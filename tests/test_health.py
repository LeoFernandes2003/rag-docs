from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_health_retorna_ok():
    resposta = client.get("/health")
    assert resposta.status_code == 200
    assert resposta.json() == {"status": "ok"}


def test_config_usa_variaveis_de_ambiente(monkeypatch):
    monkeypatch.setenv("GEN_MODEL", "modelo-de-teste")
    resposta = client.get("/config")
    assert resposta.status_code == 200
    assert resposta.json()["gen_model"] == "modelo-de-teste"
