import pytest

from app.evaluation.retrieval import covers, evaluate, find_span
from app.rag.chunking import chunk_corpus, chunk_text, fixed_windows
from app.rag.http import HttpError
from app.rag.index import build_index, default_collection, to_point
from app.rag.ollama import embed
from app.rag.qdrant import QdrantStore
from app.rag.search import search

# --- pedaços ---


def test_janelas_sem_sobreposicao_cobrem_o_texto_todo():
    assert fixed_windows(10, 4) == [(0, 4), (4, 8), (8, 10)]


def test_janelas_com_sobreposicao():
    assert fixed_windows(10, 4, overlap=2) == [(0, 4), (2, 6), (4, 8), (6, 10)]


def test_janelas_texto_menor_que_o_pedaco_e_texto_vazio():
    assert fixed_windows(3, 10) == [(0, 3)]
    assert fixed_windows(0, 10) == []


def test_janelas_rejeitam_parametros_invalidos():
    with pytest.raises(ValueError):
        fixed_windows(10, 0)
    with pytest.raises(ValueError):
        fixed_windows(10, 4, overlap=4)


def test_chunk_text_guarda_posicoes_e_ignora_pedacos_em_branco():
    texto = "abcd" + "    " + "efgh"
    chunks = chunk_text("a.md", texto, size=4)
    assert [(c.index, c.start, c.end, c.text) for c in chunks] == [
        (0, 0, 4, "abcd"),
        (1, 8, 12, "efgh"),
    ]


def test_chunk_corpus_le_arquivos_em_ordem_com_caminho_relativo(tmp_path):
    (tmp_path / "tutorial").mkdir()
    (tmp_path / "tutorial" / "b.md").write_text("bbbb", encoding="utf-8")
    (tmp_path / "a.md").write_text("aaaa", encoding="utf-8")
    chunks = chunk_corpus(tmp_path, size=10)
    assert [c.source_file for c in chunks] == ["a.md", "tutorial/b.md"]


# --- clientes (com respostas falsas, sem rede) ---


def test_embed_envia_modelo_e_textos_e_devolve_vetores():
    chamadas = []

    def falso(method, url, payload=None):
        chamadas.append((method, url, payload))
        return {"embeddings": [[1.0, 0.0], [0.0, 1.0]]}

    vetores = embed(["um", "dois"], url="http://o", model="bge-m3", request=falso)
    assert vetores == [[1.0, 0.0], [0.0, 1.0]]
    corpo = {"model": "bge-m3", "input": ["um", "dois"]}
    assert chamadas == [("POST", "http://o/api/embed", corpo)]


def test_embed_detecta_quantidade_errada_de_vetores():
    curto = lambda *args, **kwargs: {"embeddings": [[1]]}  # noqa: E731
    with pytest.raises(ValueError):
        embed(["um", "dois"], url="http://o", model="m", request=curto)


class QdrantFalso:
    """Guarda as chamadas e responde como o Qdrant responderia."""

    def __init__(self, existe=True):
        self.existe = existe
        self.chamadas = []

    def __call__(self, method, url, payload=None):
        self.chamadas.append((method, url, payload))
        if method == "GET" and not self.existe:
            raise HttpError(404, "not found")
        if url.endswith("/points/count"):
            return {"result": {"count": 7}}
        if url.endswith("/points/query"):
            return {"result": {"points": [{"id": 1, "score": 0.9, "payload": {"x": 1}}]}}
        return {}


def test_qdrant_existe_trata_404_como_nao_existe():
    assert QdrantStore("http://q", "c", QdrantFalso(existe=True)).exists() is True
    assert QdrantStore("http://q", "c", QdrantFalso(existe=False)).exists() is False


def test_qdrant_outros_erros_sobem():
    def quebrado(*args, **kwargs):
        raise HttpError(500, "erro")

    with pytest.raises(HttpError):
        QdrantStore("http://q", "c", quebrado).exists()


def test_qdrant_cria_colecao_com_distancia_cosseno():
    falso = QdrantFalso()
    QdrantStore("http://q", "c", falso).create(1024)
    assert falso.chamadas[0] == (
        "PUT",
        "http://q/collections/c",
        {"vectors": {"size": 1024, "distance": "Cosine"}},
    )


def test_qdrant_busca_conta_e_envia_pontos():
    falso = QdrantFalso()
    loja = QdrantStore("http://q", "c", falso)
    assert loja.count() == 7
    assert loja.search([0.1, 0.2], 5)[0]["score"] == 0.9
    loja.upsert([{"id": 0}])
    metodos = [(m, u.split("/collections/c")[1]) for m, u, _ in falso.chamadas]
    assert ("POST", "/points/query") in metodos
    assert ("PUT", "/points?wait=true") in metodos
    consulta = next(p for m, u, p in falso.chamadas if u.endswith("/points/query"))
    assert consulta == {"query": [0.1, 0.2], "limit": 5, "with_payload": True}


# --- indexação e busca ---


def test_build_index_cria_colecao_e_envia_em_lotes():
    chunks = chunk_text("a.md", "abcdefghij", size=2)  # 5 pedaços
    falso = QdrantFalso(existe=False)
    loja = QdrantStore("http://q", "c", falso)
    andamento = []
    build_index(
        chunks,
        lambda textos: [[float(len(t)), 0.0] for t in textos],
        loja,
        batch_size=2,
        progress=lambda feito, total: andamento.append((feito, total)),
    )
    assert andamento == [(2, 5), (4, 5), (5, 5)]
    criacoes = [c for c in falso.chamadas if c[0] == "PUT" and c[1].endswith("/collections/c")]
    assert len(criacoes) == 1
    assert criacoes[0][2]["vectors"]["size"] == 2
    envios = [c[2]["points"] for c in falso.chamadas if "points?wait" in c[1]]
    assert [len(lote) for lote in envios] == [2, 2, 1]
    assert [p["id"] for lote in envios for p in lote] == [0, 1, 2, 3, 4]


def test_to_point_guarda_posicoes_e_texto():
    chunk = chunk_text("a.md", "abcd", size=4)[0]
    ponto = to_point(3, chunk, [0.5])
    assert ponto["id"] == 3
    assert ponto["payload"] == {
        "source_file": "a.md",
        "index": 0,
        "start": 0,
        "end": 4,
        "text": "abcd",
    }


def test_nome_padrao_da_colecao():
    assert default_collection(1000, 0) == "docs-fixed-1000-0"


def test_search_embute_a_pergunta_e_consulta_o_qdrant():
    falso = QdrantFalso()
    loja = QdrantStore("http://q", "c", falso)
    resultado = search("pergunta?", lambda textos: [[0.3, 0.4]] * len(textos), loja, 3)
    assert resultado[0]["id"] == 1
    consulta = next(p for m, u, p in falso.chamadas if u.endswith("/points/query"))
    assert consulta["query"] == [0.3, 0.4] and consulta["limit"] == 3


# --- medição da busca ---


def test_find_span_ignora_diferencas_de_espaco():
    assert find_span("um  texto\ncom quebra", "texto com") == (4, 13)
    assert find_span("abc", "xyz") is None
    assert find_span("abc", "   ") is None


def test_covers_exige_mesmo_arquivo_e_sobreposicao():
    pedaco = {"source_file": "a.md", "start": 10, "end": 20}
    assert covers(pedaco, "a.md", (15, 30))
    assert covers(pedaco, "a.md", (0, 11))
    assert not covers(pedaco, "a.md", (20, 30))
    assert not covers(pedaco, "b.md", (15, 30))


def test_evaluate_calcula_recall_e_lista_erros(tmp_path):
    (tmp_path / "a.md").write_text("0123456789 alvo do teste 0123456789", encoding="utf-8")
    perguntas = [
        {"id": "q1", "answerable": True, "question": "acerta", "source_file": "a.md",
         "source_span": "alvo do teste"},
        {"id": "q2", "answerable": True, "question": "erra", "source_file": "a.md",
         "source_span": "alvo do teste"},
        {"id": "q3", "answerable": False, "question": "sem resposta"},
    ]
    certo = [{"payload": {"source_file": "a.md", "start": 10, "end": 30}}]
    errado = [{"payload": {"source_file": "b.md", "start": 0, "end": 99}}]
    resultado = evaluate(perguntas, tmp_path, lambda q: certo if q == "acerta" else errado)
    assert resultado["questions"] == 2
    assert resultado["hits"] == 1
    assert resultado["recall"] == 0.5
    assert resultado["misses"][0]["id"] == "q2"
    assert resultado["misses"][0]["retrieved_files"] == ["b.md"]
