from app.rag.chunking import Chunk
from app.rag.ollama import generate
from app.rag.pipeline import (
    REFUSAL_TEXT,
    RagPipeline,
    build_prompt,
    cited_numbers,
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
