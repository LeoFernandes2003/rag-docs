from app.rag.chunking import Chunk
from app.rag.ollama import generate
from app.rag.pipeline import (
    REFUSAL_TEXT,
    RagPipeline,
    build_prompt,
    cited_numbers,
    is_empty_answer,
    is_refusal,
)

CHUNKS = [
    Chunk("a.md", 0, 0, 30, "Use dependency_overrides in tests."),
    Chunk("b.md", 0, 0, 25, "Cookies are sent by the client."),
]


class LojaFalsa:
    def __init__(self, score: float) -> None:
        self.score = score

    def search(self, vector, limit):
        return [
            {
                "id": position,
                "score": self.score,
                "payload": {
                    "source_file": c.source_file,
                    "start": c.start,
                    "end": c.end,
                    "text": c.text,
                },
            }
            for position, c in enumerate(CHUNKS[:limit])
        ]


def make_pipeline(score: float, reply: str, min_score: float = 0.0) -> RagPipeline:
    return RagPipeline(
        embed_fn=lambda texts: [[0.0] for _ in texts],
        generate_fn=lambda prompt: reply,
        translate_fn=lambda question: "dependency overrides tests",
        store=LojaFalsa(score),
        chunks=CHUNKS,
        min_score=min_score,
    )


def test_is_refusal_ignores_case_and_spaces():
    assert is_refusal("Não   encontrei na documentação.")
    assert not is_refusal("Use dependency_overrides [1].")


def test_cited_numbers_keeps_only_valid_unique():
    assert cited_numbers("Veja [2], [1] e [2]; também [9] e [0].", 3) == [1, 2]
    assert cited_numbers("sem citações", 3) == []


def test_build_prompt_numbers_passages_and_has_question():
    prompt = build_prompt("Como?", [{"source_file": "a.md", "text": "texto A"}])
    assert "[1] (arquivo: a.md)" in prompt
    assert "texto A" in prompt
    assert "Pergunta: Como?" in prompt
    assert REFUSAL_TEXT in prompt


def test_answer_with_citation():
    answer = make_pipeline(0.7, "Use dependency_overrides [1].").ask("Como testar?")
    assert not answer.refused
    assert answer.reason == "respondeu"
    assert answer.cited == [1]
    assert answer.sources[0]["source_file"] == "a.md"
    assert answer.translated == "dependency overrides tests"


def test_weak_evidence_refuses_without_calling_model():
    chamadas = []
    pipeline = make_pipeline(0.2, "x", min_score=0.5)
    pipeline.generate_fn = lambda prompt: chamadas.append(prompt) or "x"
    answer = pipeline.ask("Stripe?")
    assert answer.refused
    assert answer.reason == "evidencia_fraca"
    assert chamadas == []


def test_model_refusal_is_recorded():
    answer = make_pipeline(0.7, "não encontrei na documentação.").ask("Stripe?")
    assert answer.refused
    assert answer.reason == "modelo_recusou"
    assert answer.answer == REFUSAL_TEXT


def test_generate_sends_prompt_and_strips():
    enviado = {}

    def falso(method, url, payload=None):
        enviado.update(url=url, payload=payload)
        return {"response": "  oi  "}

    assert generate("p", url="http://o", model="m", request=falso) == "oi"
    assert enviado["url"] == "http://o/api/generate"
    assert enviado["payload"]["options"]["temperature"] == 0


def test_retries_once_when_first_answer_has_no_citation():
    respostas = iter(["Use dependency_overrides.", "Use dependency_overrides [1]."])
    chamadas = []

    def modelo(prompt):
        chamadas.append(prompt)
        return next(respostas)

    pipeline = make_pipeline(0.7, "")
    pipeline.generate_fn = modelo
    answer = pipeline.ask("Como testar?")
    assert len(chamadas) == 2
    assert "LEMBRETE" in chamadas[1]
    assert answer.cited == [1]


def test_score_answers_counts_citations_refusals_and_hallucinations(tmp_path):
    from app.evaluation.generation import score_answers

    (tmp_path / "a.md").write_text("Use dependency_overrides in tests.", encoding="utf-8")
    questions = [
        {"id": "q1", "answerable": True, "question": "a?", "source_file": "a.md",
         "source_span": "dependency_overrides", "expected_answer": "x"},
        {"id": "q2", "answerable": True, "question": "b?", "source_file": "a.md",
         "source_span": "dependency_overrides", "expected_answer": "x"},
        {"id": "q3", "answerable": False, "question": "c?", "forbidden_terms": ["stripe"]},
        {"id": "q4", "answerable": False, "question": "d?", "forbidden_terms": ["kafka"]},
    ]
    chunk = {"source_file": "a.md", "start": 0, "end": 30}
    answers = {
        "q1": {"refused": False, "answer": "ok [1]", "cited": [1], "retrieved": [chunk]},
        "q2": {"refused": True, "answer": "", "cited": [], "retrieved": [chunk]},
        "q3": {"refused": False, "answer": "Use Stripe [1]", "cited": [1], "retrieved": [chunk]},
        "q4": {"refused": True, "answer": "", "cited": [], "retrieved": [chunk]},
    }
    result = score_answers(questions, answers, tmp_path)
    assert result["valid_citation_rate"] == 1.0
    assert result["right_source_rate"] == 0.5
    assert result["wrongful_refusal_rate"] == 0.5
    assert result["correct_refusal_rate"] == 0.5
    assert result["unanswerable_answered"] == 1
    assert result["unanswerable_with_forbidden_terms"] == 1
    assert {c["id"] for c in result["problem_cases"]} == {"q2", "q3"}


def test_is_refusal_accepts_small_spelling_variations():
    assert is_refusal("NÃO ENCONTROU NA DOCUMENTAÇÃO [1]")
    assert is_refusal("NÃO ENCONTROI NA DOCUMENTAÇÃO. [1]")
    assert not is_refusal("Encontrei na documentação que X [1].")


def test_is_empty_answer_detects_only_citation_marks():
    assert is_empty_answer("[1]")
    assert is_empty_answer("  [2] [3] ")
    assert not is_empty_answer("O response model filtra os campos retornados [1].")


def test_empty_answer_is_retried_then_refused_as_empty():
    pipeline = make_pipeline(0.7, "[1]")
    answer = pipeline.ask("Como testar?")
    assert answer.refused
    assert answer.reason == "resposta_vazia"


def test_refusal_variation_counts_as_refusal():
    answer = make_pipeline(0.7, "NÃO ENCONTROU NA DOCUMENTAÇÃO [1]").ask("Kafka?")
    assert answer.refused
    assert answer.reason == "modelo_recusou"


def test_score_review_counts_marked_answers():
    from app.evaluation.generation import score_review

    markdown = (
        "# t\n\n## q1: a?\n- Esperado: x\n- [x] correta\n\n"
        "## q2: b?\n- Esperado: y\n- [ ] correta\n\n"
        "## q3: c?\n- Esperado: recusar (a documentação não tem a resposta)\n- [x] correta\n"
    )
    result = score_review(markdown)
    assert (result["answerable_correct"], result["answerable_total"]) == (1, 2)
    assert (result["unanswerable_correct"], result["unanswerable_total"]) == (1, 1)


def test_fontes_line_does_not_count_as_answer_text():
    assert is_empty_answer("Fontes: [1] [2]")
    assert not is_empty_answer("Use dependency_overrides para trocar a dependência.\nFontes: [1]")


def test_answer_with_fontes_line_cites_and_keeps_raw():
    texto = "Use dependency_overrides para trocar a dependência.\nFontes: [1]"
    answer = make_pipeline(0.7, texto).ask("Como testar?")
    assert not answer.refused
    assert answer.cited == [1]
    assert answer.raw == texto


def test_score_review_accepts_spaces_inside_brackets():
    from app.evaluation.generation import score_review

    markdown = (
        "# t\n\n## q1: a?\n- Esperado: x\n- [ x] correta\n\n"
        "## q2: b?\n- Esperado: y\n- [x ] correta\n\n"
        "## q3: c?\n- Esperado: z\n- [ ] correta\n"
    )
    result = score_review(markdown)
    assert (result["answerable_correct"], result["answerable_total"]) == (2, 3)


def test_missing_models_accepts_latest_suffix():
    from app.setup import missing_models

    installed = ["bge-m3:latest", "qwen2.5:3b"]
    assert missing_models(installed, ["bge-m3", "qwen2.5:3b"]) == []
    assert missing_models(installed, ["llama3"]) == ["llama3"]


def test_ensure_models_pulls_only_missing_ones():
    from app.setup import ensure_models

    chamadas = []

    def falso(method, url, payload=None, timeout=0):
        chamadas.append((method, url, payload))
        if url.endswith("/api/tags"):
            return {"models": [{"name": "bge-m3:latest"}]}
        return {"status": "success"}

    ensure_models("http://o", ["bge-m3", "qwen2.5:3b"], falso)
    assert [c[1] for c in chamadas] == ["http://o/api/tags", "http://o/api/pull"]
    assert chamadas[1][2]["model"] == "qwen2.5:3b"


def test_ensure_corpus_skips_when_manifest_exists(tmp_path):
    from app.setup import ensure_corpus

    (tmp_path / "manifest.json").write_text("{}", encoding="utf-8")
    chamadas = []
    ensure_corpus(tmp_path, lambda *args: chamadas.append(args) or 0)
    assert chamadas == []


def test_ensure_corpus_fetches_when_missing(tmp_path):
    import pytest

    from app.setup import ensure_corpus

    chamadas = []
    ensure_corpus(tmp_path / "novo", lambda *args: chamadas.append(args) or 0)
    assert len(chamadas) == 1
    with pytest.raises(RuntimeError):
        ensure_corpus(tmp_path / "outro", lambda *args: 1)


def test_wait_for_retries_then_gives_up():
    import pytest

    from app.setup import wait_for

    tentativas = []

    def sempre_fora(method, url, payload=None, timeout=0):
        tentativas.append(url)
        raise ConnectionError("fora")

    with pytest.raises(ConnectionError):
        wait_for("http://x", sempre_fora, tries=3, pause=0)
    assert len(tentativas) == 3


def test_fetch_corpus_extracts_and_prepares(tmp_path):
    import io
    import tarfile

    from app.ingest.fetch import fetch_corpus

    def falso_download(url, destination):
        assert url.endswith("/0.1.0.tar.gz")
        with tarfile.open(destination, "w:gz") as tar:
            for nome, conteudo in (
                ("fastapi-0.1.0/docs/en/docs/index.md", "# Início\n\nTexto.\n"),
                ("fastapi-0.1.0/docs_src/exemplo.py", "print(1)\n"),
            ):
                dados = conteudo.encode()
                info = tarfile.TarInfo(nome)
                info.size = len(dados)
                tar.addfile(info, io.BytesIO(dados))

    saida = tmp_path / "corpus"
    assert fetch_corpus("0.1.0", saida, falso_download) == 0
    assert (saida / "index.md").exists()
    assert (saida / "manifest.json").exists()
