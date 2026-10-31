"""Reranking: reordena os candidatos da busca com uma nota de relevância dada pelo modelo.

A busca (densa, por palavras ou híbrida) traz mais candidatos do que precisamos (por exemplo
10). Para cada candidato, o modelo de texto lê a pergunta e o trecho e dá uma nota de 0 a 9
para "este trecho responde à pergunta?". Os candidatos são reordenados pela nota (empates
mantêm a ordem original da busca) e só os melhores seguem para a resposta.

Limitação conhecida: o Ollama não tem um modelo de reranking dedicado; usar o modelo de
respostas como juiz é mais lento (uma chamada por candidato) do que um cross-encoder.
"""

from __future__ import annotations

import re
from collections.abc import Callable
from typing import Any

Point = dict[str, Any]

RELEVANCE_PROMPT = """Pergunta do usuário: {question}

Trecho da documentação:
{passage}

O trecho acima contém a informação necessária para responder à pergunta?
Responda apenas com um número de 0 (nada a ver) a 9 (responde diretamente).
Nota:"""

MAX_PASSAGE_CHARS = 1200


def build_relevance_prompt(question: str, passage: str) -> str:
    return RELEVANCE_PROMPT.format(question=question, passage=passage.strip()[:MAX_PASSAGE_CHARS])


def parse_score(text: str) -> int:
    """Primeiro dígito da resposta do modelo; 0 se ele não escreveu nenhum."""
    match = re.search(r"\d", text)
    return int(match.group()) if match else 0


def rerank(
    question: str,
    points: list[Point],
    generate_fn: Callable[[str], str],
    top_k: int,
) -> list[Point]:
    """Reordena `points` pela nota de relevância e devolve os `top_k` melhores."""
    scored = [
        (parse_score(generate_fn(build_relevance_prompt(question, p["payload"]["text"]))), i)
        for i, p in enumerate(points)
    ]
    scored.sort(key=lambda item: (-item[0], item[1]))
    return [points[i] for _, i in scored[:top_k]]


def with_reranker(
    searcher: Callable[[str], list[Point]],
    generate_fn: Callable[[str], str],
    top_k: int,
) -> Callable[[str], list[Point]]:
    """Envolve uma busca: busca candidatos, reordena e devolve só os `top_k` melhores."""
    return lambda question: rerank(question, searcher(question), generate_fn, top_k)
