"""Escolha da estratégia de busca: por sentido (dense), por palavras (bm25) ou híbrida."""

from __future__ import annotations

from collections.abc import Callable
from typing import Any

from .bm25 import BM25Index
from .chunking import Chunk
from .index import chunk_payload
from .qdrant import QdrantStore

MODES = ("dense", "bm25", "hybrid")
RRF_K = 60

Point = dict[str, Any]
EmbedFn = Callable[[list[str]], list[list[float]]]


def reciprocal_rank_fusion(rankings: list[list[Point]], k: int = RRF_K) -> list[Point]:
    """Combina várias listas ordenadas: cada pedaço soma 1/(k + posição) em cada lista."""
    scores: dict[Any, float] = {}
    first_seen: dict[Any, Point] = {}
    for ranking in rankings:
        for position, point in enumerate(ranking, start=1):
            scores[point["id"]] = scores.get(point["id"], 0.0) + 1.0 / (k + position)
            first_seen.setdefault(point["id"], point)
    order = sorted(scores, key=lambda point_id: (-scores[point_id], point_id))
    return [{**first_seen[point_id], "score": scores[point_id]} for point_id in order]


def build_searcher(
    mode: str,
    embed_fn: EmbedFn,
    store: QdrantStore,
    chunks: list[Chunk],
    top_k: int,
    pool: int = 20,
    lexical_query: Callable[[str], str] = lambda question: question,
) -> Callable[[str], list[Point]]:
    """Devolve uma função pergunta -> pedaços. No modo hybrid, cada busca traz `pool` candidatos.

    `lexical_query` transforma a pergunta antes da busca por palavras (por exemplo, traduz).

    O id de cada pedaço no Qdrant é a sua posição na lista `chunks`; por isso `chunks` precisa
    ser gerado com a mesma estratégia e tamanho da coleção.
    """
    if mode not in MODES:
        raise ValueError(f"modo desconhecido: {mode}")

    def dense(question: str, limit: int) -> list[Point]:
        return store.search(embed_fn([question])[0], limit)

    if mode == "dense":
        return lambda question: dense(question, top_k)

    bm25 = BM25Index([chunk.text for chunk in chunks])

    def lexical(question: str, limit: int) -> list[Point]:
        return [
            {"id": doc_id, "score": score, "payload": chunk_payload(chunks[doc_id])}
            for doc_id, score in bm25.search(lexical_query(question), limit)
        ]

    if mode == "bm25":
        return lambda question: lexical(question, top_k)

    def hybrid(question: str) -> list[Point]:
        fused = reciprocal_rank_fusion([dense(question, pool), lexical(question, pool)])
        return fused[:top_k]

    return hybrid
