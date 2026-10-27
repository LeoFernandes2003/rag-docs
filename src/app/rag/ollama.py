"""Cliente do Ollama para gerar embeddings (as "etiquetas de sentido" dos textos)."""

from __future__ import annotations

from collections.abc import Callable
from typing import Any

from .http import request_json

Request = Callable[..., dict[str, Any]]


def embed(
    texts: list[str], *, url: str, model: str, request: Request = request_json
) -> list[list[float]]:
    """Devolve um vetor de números para cada texto."""
    result = request("POST", f"{url}/api/embed", {"model": model, "input": texts})
    vectors = result["embeddings"]
    if len(vectors) != len(texts):
        raise ValueError(f"pedi {len(texts)} embeddings e recebi {len(vectors)}")
    return vectors
