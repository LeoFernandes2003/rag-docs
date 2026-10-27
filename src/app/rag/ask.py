"""Faz uma pergunta ao assistente e mostra a resposta com as fontes.

Uso (a partir da pasta `src`):

    python -m app.rag.ask "Como sobrescrever uma dependência em testes?"
    python -m app.rag.ask "Como integrar com a Stripe?"      # deve recusar
"""

from __future__ import annotations

import argparse
from pathlib import Path

from ..ingest.prepare import DEFAULT_OUT
from .chunking import STRATEGIES, chunk_corpus
from .config import get_settings
from .index import default_collection
from .ollama import embed, generate
from .pipeline import RagPipeline
from .qdrant import QdrantStore
from .translate import translate_to_english


def build_pipeline(
    corpus: Path, strategy: str, size: int, overlap: int, min_score: float, collection: str | None
) -> RagPipeline:
    settings = get_settings()
    name = collection or default_collection(size, overlap, strategy)
    return RagPipeline(
        embed_fn=lambda texts: embed(texts, url=settings.ollama_url, model=settings.embed_model),
        generate_fn=lambda prompt: generate(
            prompt, url=settings.ollama_url, model=settings.gen_model
        ),
        translate_fn=lambda question: translate_to_english(
            question, url=settings.ollama_url, model=settings.gen_model
        ),
        store=QdrantStore(settings.qdrant_url, name),
        chunks=chunk_corpus(corpus, size, overlap, strategy),
        min_score=min_score,
    )


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Pergunta ao assistente.")
    parser.add_argument("question", help="a pergunta, entre aspas")
    parser.add_argument("--corpus", type=Path, default=DEFAULT_OUT)
    parser.add_argument("--strategy", choices=STRATEGIES, default="structure")
    parser.add_argument("--size", type=int, default=1000)
    parser.add_argument("--overlap", type=int, default=0)
    parser.add_argument("--collection", help="coleção (padrão: a da estratégia escolhida)")
    parser.add_argument(
        "--min-score", type=float, default=0.0, help="abaixo desta nota de similaridade, recusa"
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    try:
        pipeline = build_pipeline(
            args.corpus, args.strategy, args.size, args.overlap, args.min_score, args.collection
        )
        answer = pipeline.ask(args.question)
    except ConnectionError as error:
        print(f"Erro: {error}")
        return 1

    print(f"Pergunta: {answer.question}")
    if answer.translated:
        print(f"(busca por palavras com: {answer.translated})")
    print(f"Nota de similaridade: {answer.top_score:.3f}\n")
    print(answer.answer)
    if answer.refused:
        print(f"\n[recusou: {answer.reason}]")
    elif answer.sources:
        print("\nFontes citadas:")
        for source in answer.sources:
            print(f"  [{source['n']}] {source['source_file']}")
    else:
        print("\n[atenção: a resposta não cita nenhuma fonte válida]")
    if not answer.refused:
        print("\nTrechos consultados:")
        for number, item in enumerate(answer.retrieved, start=1):
            print(f"  ({number}) {item['source_file']}")
    print(f"\nTempo: {answer.seconds:.1f} s")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
