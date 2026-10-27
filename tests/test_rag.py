import pytest

from app.evaluation.retrieval import covers, evaluate, find_span
from app.rag.bm25 import BM25Index, tokenize
from app.rag.chunking import (
    chunk_corpus,
    chunk_structure,
    chunk_text,
    fixed_windows,
    markdown_blocks,
)
from app.rag.http import HttpError
from app.rag.index import build_index, default_collection, to_point
from app.rag.ollama import embed
from app.rag.qdrant import QdrantStore
from app.rag.retrieve import build_searcher, reciprocal_rank_fusion
from app.rag.search import search
from app.rag.translate import translate_to_english

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


# --- divisão por estrutura ---

DOC = """# Título A

Primeiro parágrafo curto.

## Seção B

Texto da seção B com bastante conteúdo para passar do mínimo de caracteres. """ + "x" * 220 + """

```python
# isto não é título

def f():
    return 1
```

Fim.
"""


def test_blocos_nao_cortam_codigo_nem_confundem_comentario_com_titulo():
    blocos = markdown_blocks(DOC)
    textos = [DOC[a:b] for a, b, _ in blocos]
    codigo = next(t for t in textos if t.startswith("```python"))
    assert "def f():" in codigo and codigo.rstrip().endswith("```")
    titulos = [DOC[a:b] for a, b, titulo in blocos if titulo]
    assert titulos == ["# Título A", "## Seção B"]


def test_estrutura_comeca_pedaco_novo_em_titulo_quando_o_atual_ja_e_grande():
    chunks = chunk_structure("a.md", DOC, size=2000, min_size=20)
    assert len(chunks) == 2
    assert chunks[0].text.startswith("# Título A")
    assert chunks[1].text.startswith("## Seção B")
    assert all(DOC[c.start : c.end] == c.text for c in chunks)


def test_estrutura_junta_secao_minuscula_com_a_seguinte():
    chunks = chunk_structure("a.md", DOC, size=2000, min_size=1000)
    assert len(chunks) == 1


def test_estrutura_respeita_o_tamanho_maximo_e_corta_bloco_gigante():
    texto = "# T\n\n" + "palavra " * 100
    chunks = chunk_structure("a.md", texto, size=300)
    assert all(len(c.text) <= 300 for c in chunks)
    assert "".join(texto[c.start : c.end] for c in chunks).replace(" ", "")  # sem erro de posição


def test_chunk_corpus_aceita_estrategia_e_rejeita_desconhecida(tmp_path):
    (tmp_path / "a.md").write_text(DOC, encoding="utf-8")
    assert chunk_corpus(tmp_path, 2000, strategy="structure")
    with pytest.raises(ValueError):
        chunk_corpus(tmp_path, 2000, strategy="outra")


def test_nome_da_colecao_por_estrategia():
    assert default_collection(1000, 0, "structure") == "docs-structure-1000"


# --- busca por palavras (BM25) e híbrida ---

TEXTOS = [
    "Use app.routes to list the route tree of the application",
    "Dependencies are declared with Depends and can have sub-dependencies",
    "The status_code parameter sets the HTTP status of the response",
]


def test_tokenize_separa_palavras_e_ignora_maiusculas():
    assert tokenize("Use app.routes, status_code!") == ["use", "app", "routes", "status_code"]


def test_bm25_acha_o_documento_com_o_termo_exato():
    indice = BM25Index(TEXTOS)
    assert indice.search("app.routes", 3)[0][0] == 0
    assert indice.search("status_code", 3)[0][0] == 2


def test_bm25_sem_termos_em_comum_devolve_vazio_e_respeita_o_limite():
    indice = BM25Index(TEXTOS)
    assert indice.search("zzz qqq", 3) == []
    assert len(indice.search("the", 2)) <= 2


def test_rrf_premia_quem_aparece_bem_nas_duas_listas():
    a = [{"id": 1, "payload": {}}, {"id": 2, "payload": {}}, {"id": 3, "payload": {}}]
    b = [{"id": 3, "payload": {}}, {"id": 2, "payload": {}}, {"id": 9, "payload": {}}]
    fundidos = reciprocal_rank_fusion([a, b])
    assert {p["id"] for p in fundidos[:2]} == {2, 3}
    assert {p["id"] for p in fundidos} == {1, 2, 3, 9}


def test_searcher_modos_dense_bm25_e_hybrid():
    chunks = [chunk_text(f"f{i}.md", texto, size=1000)[0] for i, texto in enumerate(TEXTOS)]
    falso = QdrantFalso()  # o Qdrant falso devolve sempre o ponto de id 1
    loja = QdrantStore("http://q", "c", falso)

    def embed_fn(textos):
        return [[0.1, 0.2] for _ in textos]

    denso = build_searcher("dense", embed_fn, loja, [], 3)
    assert denso("qualquer")[0]["id"] == 1

    lexico = build_searcher("bm25", embed_fn, loja, chunks, 3)
    achados = lexico("app.routes")
    assert achados[0]["payload"]["source_file"] == "f0.md"

    hibrido = build_searcher("hybrid", embed_fn, loja, chunks, 3)
    ids = [p["id"] for p in hibrido("app.routes")]
    assert set(ids[:2]) == {0, 1}  # 0 vem do BM25 e 1 vem da busca por sentido

    with pytest.raises(ValueError):
        build_searcher("outro", embed_fn, loja, chunks, 3)


# --- tradução da pergunta ---


def test_traducao_usa_o_modelo_e_fica_com_a_primeira_linha():
    chamadas = []

    def falso(method, url, payload=None):
        chamadas.append((method, url, payload))
        return {"response": '\n"How do I override a dependency?"\nNote: translated.\n'}

    texto = translate_to_english("Como sobrescrever?", url="http://o", model="qwen", request=falso)
    assert texto == "How do I override a dependency?"
    metodo, url, corpo = chamadas[0]
    assert (metodo, url) == ("POST", "http://o/api/generate")
    assert corpo["model"] == "qwen" and corpo["stream"] is False
    assert "Como sobrescrever?" in corpo["prompt"]


def test_traducao_vazia_devolve_a_pergunta_original():
    vazio = lambda *args, **kwargs: {"response": "  \n"}  # noqa: E731
    assert translate_to_english("Oi?", url="http://o", model="m", request=vazio) == "Oi?"


def test_bm25_usa_a_pergunta_traduzida_e_o_dense_usa_a_original():
    chunks = [chunk_text(f"f{i}.md", texto, size=1000)[0] for i, texto in enumerate(TEXTOS)]
    loja = QdrantStore("http://q", "c", QdrantFalso())
    recebidas = []

    def embed_fn(textos):
        recebidas.extend(textos)
        return [[0.1, 0.2] for _ in textos]

    busca = build_searcher(
        "bm25", embed_fn, loja, chunks, 1, lexical_query=lambda q: "app.routes"
    )
    assert busca("pergunta em português")[0]["payload"]["source_file"] == "f0.md"
    hibrida = build_searcher(
        "hybrid", embed_fn, loja, chunks, 3, lexical_query=lambda q: "app.routes"
    )
    hibrida("pergunta em português")
    assert recebidas == ["pergunta em português"]
