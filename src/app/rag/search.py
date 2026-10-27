"""Busca: transforma a pergunta em embedding e devolve os pedaços mais parecidos.

Uso (a partir da pasta `src`):

    python -m app.rag.search "Como sobrescrever uma dependência em testes?"
"""

from __future__ import annotations

import argparse
from collections.abc import Callable
from typing import Any

from .config import get_settings
from .index import default_collection
from .ollama import embed
from .qdrant import QdrantStore


def search(
    question: str,
    embed_fn: Callable[[list[str]], list[list[float]]],
    store: QdrantStore,
    top_k: int = 5,
) -> list[dict[str, Any]]:
    """Devolve os `top_k` pedaços mais parecidos com a pergunta (maior nota primeiro)."""
    vector = embed_fn([question])[0]
    return store.search(vector, top_k)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Busca pedaços da documentação.")
    parser.add_argument("question", help="a pergunta, entre aspas")
    parser.add_argument("--top", type=int, default=5, help="quantos pedaços mostrar")
    parser.add_argument("--collection", help="coleção (padrão: baseline de 1000 caracteres)")
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    settings = get_settings()
    store = QdrantStore(settings.qdrant_url, args.collection or default_collection(1000, 0))

    def embed_fn(texts: list[str]) -> list[list[float]]:
        return embed(texts, url=settings.ollama_url, model=settings.embed_model)

    try:
        results = search(args.question, embed_fn, store, args.top)
    except ConnectionError as error:
        print(f"Erro: {error}")
        return 1

    print(f"Pergunta: {args.question}\n")
    for rank, point in enumerate(results, start=1):
        payload = point["payload"]
        snippet = " ".join(payload["text"].split())[:300]
        print(f"[{rank}] nota {point['score']:.3f} | {payload['source_file']}")
        print(f"    {snippet}...\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
