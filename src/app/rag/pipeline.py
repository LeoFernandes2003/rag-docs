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
2. Primeiro escreva a resposta com frases completas, sem copiar código dos trechos.
3. Depois, em uma nova linha, escreva "Fontes:" seguido dos números dos trechos que você
   usou, cada um entre colchetes.
4. Não invente nada que não esteja nos trechos.
5. Se os trechos não trazem informação suficiente, responda exatamente: {refusal}

Trechos:
{passages}

Pergunta: {question}
Resposta:"""

RETRY_NOTE = (
    "\n\nLEMBRETE: sua resposta anterior não foi aproveitável (sem texto ou sem fontes). "
    "Responda de novo com frases completas e termine com a linha Fontes: e os números dos "
    "trechos usados, entre colchetes."
)

MIN_ANSWER_CHARS = 20


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
    raw: str = ""  # texto bruto do modelo, para analisar falhas

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


def build_prompt(question: str, payloads: list[dict[str, Any]]) -> str:
    passages = "\n\n".join(
        f"[{number}] (arquivo: {payload['source_file']})\n{payload['text'].strip()}"
        for number, payload in enumerate(payloads, start=1)
    )
    return PROMPT.format(refusal=REFUSAL_TEXT, passages=passages, question=question)


def is_refusal(text: str) -> bool:
    """Reconhece a recusa mesmo com pequenas variações do modelo (encontrei/encontrou...)."""
    normalized = " ".join(text.lower().split())
    return re.search(r"n[ãa]o encontr\w*\s+na\s+documenta", normalized) is not None


def is_empty_answer(text: str) -> bool:
    """Resposta sem conteúdo útil: vazia ou só com marcas de citação, como "[1]"."""
    body = re.sub(r"(?im)^\s*fontes?:.*$", "", text)
    return len(re.sub(r"\[\d+\]|\s", "", body)) < MIN_ANSWER_CHARS


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
        retrieved = [
            {"source_file": p["source_file"], "start": p["start"], "end": p["end"]}
            for p in payloads
        ]
        translated = self._translations.get(question, "")

        raw_text = ""

        def result(text: str, refused: bool, reason: str, numbers: list[int]) -> Answer:
            return Answer(
                question=question,
                answer=text,
                refused=refused,
                reason=reason,
                top_score=score,
                cited=numbers,
                sources=[
                    {
                        "n": n,
                        "source_file": payloads[n - 1]["source_file"],
                        "start": payloads[n - 1]["start"],
                        "end": payloads[n - 1]["end"],
                        "text": payloads[n - 1]["text"].strip(),
                    }
                    for n in numbers
                ],
                retrieved=retrieved,
                translated=translated,
                seconds=time.time() - started,
                raw=raw_text,
            )

        if score < self.min_score:
            return result(REFUSAL_TEXT, True, "evidencia_fraca", [])
        prompt = build_prompt(question, payloads)
        text = raw_text = self.generate_fn(prompt)
        if not is_refusal(text) and (
            is_empty_answer(text) or not cited_numbers(text, len(payloads))
        ):
            text = self.generate_fn(prompt + RETRY_NOTE)  # uma segunda chance
            raw_text = f"{raw_text}\n--- segunda tentativa ---\n{text}"
        if is_refusal(text):
            return result(REFUSAL_TEXT, True, "modelo_recusou", [])
        if is_empty_answer(text):
            return result(REFUSAL_TEXT, True, "resposta_vazia", [])
        return result(text, False, "respondeu", cited_numbers(text, len(payloads)))
