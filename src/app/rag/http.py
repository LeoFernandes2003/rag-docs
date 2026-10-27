"""Chamadas HTTP simples (só biblioteca padrão) para o Ollama e o Qdrant."""

from __future__ import annotations

import json
import urllib.error
import urllib.request
from typing import Any


class HttpError(RuntimeError):
    """O servidor respondeu com um erro (por exemplo, 404 ou 500)."""

    def __init__(self, status: int, body: str) -> None:
        super().__init__(f"HTTP {status}: {body[:300]}")
        self.status = status
        self.body = body


def request_json(
    method: str, url: str, payload: dict[str, Any] | None = None, timeout: float = 600
) -> dict[str, Any]:
    """Envia JSON e devolve a resposta já convertida em dicionário."""
    data = None if payload is None else json.dumps(payload).encode("utf-8")
    request = urllib.request.Request(
        url, data=data, method=method, headers={"Content-Type": "application/json"}
    )
    try:
        with urllib.request.urlopen(request, timeout=timeout) as response:
            body = response.read().decode("utf-8")
    except urllib.error.HTTPError as error:
        raise HttpError(error.code, error.read().decode("utf-8", "replace")) from error
    except urllib.error.URLError as error:
        raise ConnectionError(
            f"Não consegui conectar a {url} ({error.reason}). "
            "O Docker, o Qdrant e o Ollama estão ligados?"
        ) from error
    return json.loads(body) if body else {}
