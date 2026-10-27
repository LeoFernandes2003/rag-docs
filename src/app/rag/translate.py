"""Tradução da pergunta para inglês, usando o modelo de texto do Ollama.

A documentação está em inglês e as perguntas em português. A busca por palavras (BM25)
só funciona se a pergunta usar as mesmas palavras do texto, então traduzimos antes.
"""

from __future__ import annotations

from collections.abc import Callable
from typing import Any

from .http import request_json

Request = Callable[..., dict[str, Any]]

PROMPT = (
    "Translate the following question about the FastAPI web framework from Portuguese "
    "to English. Keep code terms (like `status_code`, `Form` or `app.routes`) exactly as "
    "written. Reply with the translated question only, in one line.\n\n"
    "Question: {question}"
)


def translate_to_english(
    question: str, *, url: str, model: str, request: Request = request_json
) -> str:
    result = request(
        "POST",
        f"{url}/api/generate",
        {
            "model": model,
            "prompt": PROMPT.format(question=question),
            "stream": False,
            "options": {"temperature": 0},
        },
    )
    lines = [line.strip().strip('"') for line in result["response"].splitlines() if line.strip()]
    return lines[0] if lines else question
