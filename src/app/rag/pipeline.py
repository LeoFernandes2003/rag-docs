"""Pipeline completo: busca híbrida com tradução, resposta com citações e recusa.

Fluxo de uma pergunta:
1. busca os melhores pedaços (híbrida: sentido + palavras, com a pergunta traduzida);
2. se a evidência for fraca (nota de similaridade baixa), recusa sem chamar o modelo;
3. senão, pede ao modelo que responda só com os pedaços, citando-os como [1], [2]...;
4. se o modelo disser que não encontrou, ou se citar algo que não existe, isso é registrado.
"""

from __future__ import annotations

import re
import time
from collections.abc import Callable
from dataclasses import asdict, dataclass, field
from typing import Any

from .chunking import Chunk
from .qdrant import QdrantStore
from .retrieve import EmbedFn, build_searcher

REFUSAL_TEXT = "NÃO ENCONTREI NA DOCUMENTAÇÃO."

PROMPT = """Você é um assistente que responde dúvidas sobre a documentação do FastAPI.
Regras:
1. Responda em português, usando SOMENTE as informações dos trechos abaixo.
2. TODA frase da resposta termina com o número do trecho que a sustenta, assim: [1] ou [2].
3. Não invente nada que não esteja nos trechos.
4. Se os trechos não trazem informação suficiente, responda exatamente: {refusal}

Trechos:
{passages}

Exemplo de formato: "Use o parâmetro X para fazer Y [2]."

Pergunta: {question}
Resposta (cada frase termina com [número]):"""

RETRY_NOTE = (
    "\n\nLEMBRETE: sua resposta anterior não citou nenhum trecho. "
    "Responda de novo e termine cada frase com [1], [2]..."
)


@dataclass
class Answer:
    question: str
    answer: str
    refused: bool
    reason: str  # "respondeu", "evidencia_fraca" ou "modelo_recusou"
    top_score: float
    cited: list[int] = field(default_factory=list)
    sources: list[dict[str, Any]] = field(default_factory=list)  # só os citados
    retrieved: list[dict[str, Any]] = field(default_factory=list)  # todos os devolvidos
    translated: str = ""
    seconds: float = 0.0

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


def build_prompt(question: str, payloads: list[dict[str, Any]]) -> str:
    passages = "\n\n".join(
        f"[{number}] (arquivo: {payload['source_file']})\n{payload['text'].strip()}"
        for number, payload in enumerate(payloads, start=1)
    )
    return PROMPT.format(refusal=REFUSAL_TEXT, passages=passages, question=question)


def is_refusal(text: str) -> bool:
    return "não encontrei na documentação" in " ".join(text.lower().split())


def cited_numbers(text: str, total: int) -> list[int]:
    """Números de trechos citados (como [2]) que realmente existem, sem repetição."""
    found = [int(number) for number in re.findall(r"\[(\d+)\]", text)]
    return sorted({number for number in found if 1 <= number <= total})


class RagPipeline:
    def __init__(
        self,
        *,
        embed_fn: EmbedFn,
        generate_fn: Callable[[str], str],
        translate_fn: Callable[[str], str],
        store: QdrantStore,
        chunks: list[Chunk],
        top_k: int = 5,
        min_score: float = 0.0,
    ) -> None:
        self.embed_fn = embed_fn
        self.generate_fn = generate_fn
        self.store = store
        self.min_score = min_score
        self._translations: dict[str, str] = {}

        def lexical_query(question: str) -> str:
            if question not in self._translations:
                self._translations[question] = translate_fn(question)
            return self._translations[question]

        self._search = build_searcher(
            "hybrid", embed_fn, store, chunks, top_k, lexical_query=lexical_query
        )

    def top_score(self, question: str) -> float:
        """Maior nota de similaridade (por sentido) entre a pergunta e algum pedaço."""
        points = self.store.search(self.embed_fn([question])[0], 1)
        return float(points[0]["score"]) if points else 0.0

    def ask(self, question: str) -> Answer:
        started = time.time()
        points = self._search(question)
        payloads = [point["payload"] for point in points]
        score = self.top_score(question)
        retrieved = [{"source_file": p["source_file"], "start": p["start"]} for p in payloads]
        translated = self._translations.get(question, "")

        def result(text: str, refused: bool, reason: str, numbers: list[int]) -> Answer:
            return Answer(
                question=question,
                answer=text,
                refused=refused,
                reason=reason,
                top_score=score,
                cited=numbers,
                sources=[
                    {"n": n, "source_file": payloads[n - 1]["source_file"],
                     "start": payloads[n - 1]["start"], "end": payloads[n - 1]["end"]}
                    for n in numbers
                ],
                retrieved=retrieved,
                translated=translated,
                seconds=time.time() - started,
            )

        if score < self.min_score:
            return result(REFUSAL_TEXT, True, "evidencia_fraca", [])
        prompt = build_prompt(question, payloads)
        text = self.generate_fn(prompt)
        if not is_refusal(text) and not cited_numbers(text, len(payloads)):
            text = self.generate_fn(prompt + RETRY_NOTE)  # uma segunda chance
        if is_refusal(text):
            return result(REFUSAL_TEXT, True, "modelo_recusou", [])
        return result(text, False, "respondeu", cited_numbers(text, len(payloads)))
