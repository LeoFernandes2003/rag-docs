"""Indexação: divide o corpus em pedaços, cria o embedding de cada um e guarda no Qdrant.

Uso (a partir da pasta `src`):

    python -m app.rag.index                  # baseline: pedaços de 1000 caracteres
    python -m app.rag.index --recreate       # apaga a coleção e refaz do zero
    python -m app.rag.index --strategy structure   # divide respeitando títulos e código

É preciso estar com o Ollama aberto (modelo bge-m3) e o Qdrant ligado no Docker.
"""

from __future__ import annotations

import argparse
import time
from collections.abc import Callable
from pathlib import Path

from ..ingest.prepare import DEFAULT_OUT
from .chunking import STRATEGIES, Chunk, chunk_corpus
from .config import get_settings
from .ollama import embed
from .qdrant import QdrantStore


def default_collection(size: int, overlap: int, strategy: str = "fixed") -> str:
    if strategy == "structure":
        return f"docs-structure-{size}"
    return f"docs-fixed-{size}-{overlap}"


def chunk_payload(chunk: Chunk) -> dict:
    return {
        "source_file": chunk.source_file,
        "index": chunk.index,
        "start": chunk.start,
        "end": chunk.end,
        "text": chunk.text,
    }


def to_point(point_id: int, chunk: Chunk, vector: list[float]) -> dict:
    return {"id": point_id, "vector": vector, "payload": chunk_payload(chunk)}


def build_index(
    chunks: list[Chunk],
    embed_fn: Callable[[list[str]], list[list[float]]],
    store: QdrantStore,
    batch_size: int,
    progress: Callable[[int, int], None] = lambda done, total: None,
) -> None:
    """Envia os pedaços ao Qdrant em lotes. O id de cada ponto é sua posição na lista."""
    for first in range(0, len(chunks), batch_size):
        batch = chunks[first : first + batch_size]
        vectors = embed_fn([chunk.text for chunk in batch])
        if first == 0 and not store.exists():
            store.create(len(vectors[0]))
        pairs = enumerate(zip(batch, vectors, strict=True))
        store.upsert([to_point(first + i, chunk, vec) for i, (chunk, vec) in pairs])
        progress(first + len(batch), len(chunks))


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Indexa o corpus no Qdrant.")
    parser.add_argument("--corpus", type=Path, default=DEFAULT_OUT, help="pasta do corpus limpo")
    parser.add_argument("--size", type=int, default=1000, help="tamanho do pedaço, em caracteres")
    parser.add_argument("--overlap", type=int, default=0, help="sobreposição (só estratégia fixed)")
    parser.add_argument(
        "--strategy", choices=STRATEGIES, default="fixed", help="como dividir os textos"
    )
    parser.add_argument(
        "--collection",
        help="nome da coleção (padrão: docs-<estratégia>-<tamanho>)",
    )
    parser.add_argument("--batch", type=int, default=16, help="pedaços por lote")
    parser.add_argument("--recreate", action="store_true", help="apaga a coleção antes de indexar")
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    if not args.corpus.is_dir():
        print(f"Erro: a pasta do corpus não existe: {args.corpus}")
        return 1

    settings = get_settings()
    name = args.collection or default_collection(args.size, args.overlap, args.strategy)
    store = QdrantStore(settings.qdrant_url, name)
    chunks = chunk_corpus(args.corpus, args.size, args.overlap, args.strategy)
    print(f"Pedaços a indexar: {len(chunks)} (estratégia {args.strategy}, tamanho {args.size})")
    print(f"Coleção: {name}")

    started = time.time()

    def show(done: int, total: int) -> None:
        elapsed = time.time() - started
        left = elapsed / done * (total - done)
        print(f"  {done}/{total} pedaços | {elapsed / 60:.1f} min | faltam ~{left / 60:.1f} min")

    def embed_fn(texts: list[str]) -> list[list[float]]:
        return embed(texts, url=settings.ollama_url, model=settings.embed_model)

    try:
        if args.recreate and store.exists():
            store.delete()
        build_index(chunks, embed_fn, store, args.batch, show)
        total = store.count()
    except ConnectionError as error:
        print(f"Erro: {error}")
        return 1

    print(f"\nPronto. A coleção '{name}' tem {total} pedaços.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
