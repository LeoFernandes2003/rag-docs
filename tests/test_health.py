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


def test_ask_devolve_a_resposta_do_assistente():
    from app.main import get_pipeline
    from app.rag.pipeline import Answer

    class AssistenteFalso:
        def ask(self, question):
            return Answer(question, "Use X [1].", False, "respondeu", 0.7, cited=[1])

    app.dependency_overrides[get_pipeline] = lambda: AssistenteFalso()
    try:
        resposta = client.post("/ask", json={"question": "Como fazer X?"})
    finally:
        app.dependency_overrides.clear()
    assert resposta.status_code == 200
    assert resposta.json()["answer"] == "Use X [1]."
    assert resposta.json()["refused"] is False


def test_ask_rejeita_pergunta_vazia():
    resposta = client.post("/ask", json={"question": ""})
    assert resposta.status_code == 422


def test_ask_devolve_503_quando_um_servico_esta_fora_do_ar():
    from app.main import get_pipeline

    class AssistenteQuebrado:
        def ask(self, question):
            raise ConnectionError("O Docker, o Qdrant e o Ollama estão ligados?")

    app.dependency_overrides[get_pipeline] = lambda: AssistenteQuebrado()
    try:
        resposta = client.post("/ask", json={"question": "Como fazer X?"})
    finally:
        app.dependency_overrides.clear()
    assert resposta.status_code == 503
