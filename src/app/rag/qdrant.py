"""Cliente mínimo do Qdrant (API REST)."""

from __future__ import annotations

from collections.abc import Callable
from typing import Any

from .http import HttpError, request_json

Request = Callable[..., dict[str, Any]]


class QdrantStore:
    def __init__(self, url: str, collection: str, request: Request = request_json) -> None:
        self.base = f"{url}/collections/{collection}"
        self._request = request

    def exists(self) -> bool:
        try:
            self._request("GET", self.base)
        except HttpError as error:
            if error.status == 404:
                return False
            raise
        return True

    def create(self, vector_size: int) -> None:
        body = {"vectors": {"size": vector_size, "distance": "Cosine"}}
        self._request("PUT", self.base, body)

    def delete(self) -> None:
        self._request("DELETE", self.base)

    def upsert(self, points: list[dict[str, Any]]) -> None:
        self._request("PUT", f"{self.base}/points?wait=true", {"points": points})

    def count(self) -> int:
        result = self._request("POST", f"{self.base}/points/count", {"exact": True})
        return int(result["result"]["count"])

    def search(self, vector: list[float], limit: int) -> list[dict[str, Any]]:
        body = {"query": vector, "limit": limit, "with_payload": True}
        result = self._request("POST", f"{self.base}/points/query", body)
        return result["result"]["points"]
