"""Busca: transforma a pergunta em embedding e devolve os pedaços mais parecidos.

Uso (a partir da pasta `src`):

    python -m app.rag.search "Como sobrescrever uma dependência em testes?"
    python -m app.rag.search "O que é app.routes?" --mode hybrid
"""

from __future__ import annotations

import argparse
from collections.abc import Callable
from pathlib import Path
from typing import Any

from ..ingest.prepare import DEFAULT_OUT
from .chunking import STRATEGIES, chunk_corpus
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
    parser.add_argument("--mode", choices=("dense", "bm25", "hybrid"), default="dense")
    parser.add_argument("--strategy", choices=STRATEGIES, default="fixed")
    parser.add_argument("--size", type=int, default=1000)
    parser.add_argument("--overlap", type=int, default=0)
    parser.add_argument("--corpus", type=Path, default=DEFAULT_OUT)
    parser.add_argument("--collection", help="coleção (padrão: a da estratégia escolhida)")
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    settings = get_settings()
    name = args.collection or default_collection(args.size, args.overlap, args.strategy)
    store = QdrantStore(settings.qdrant_url, name)

    def embed_fn(texts: list[str]) -> list[list[float]]:
        return embed(texts, url=settings.ollama_url, model=settings.embed_model)

    from .retrieve import build_searcher  # aqui dentro para evitar import circular

    chunks = []
    if args.mode != "dense":
        chunks = chunk_corpus(args.corpus, args.size, args.overlap, args.strategy)
    searcher = build_searcher(args.mode, embed_fn, store, chunks, args.top)

    try:
        results = searcher(args.question)
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
