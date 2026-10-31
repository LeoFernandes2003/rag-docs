"""Preparação automática do ambiente (roda uma vez, antes da API, no `docker compose up`).

Passos, todos pulados quando já estão prontos:
1. espera o Ollama e o Qdrant responderem;
2. baixa os modelos que faltam no Ollama;
3. baixa e limpa a documentação do FastAPI (corpus);
4. cria o índice no Qdrant (embeddings de todos os pedaços).

Uso manual (a partir da pasta `src`): `python -m app.setup`
"""

from __future__ import annotations

import os
import time
from collections.abc import Callable
from pathlib import Path

from .ingest.fetch import DEFAULT_VERSION, fetch_corpus
from .ingest.prepare import DEFAULT_OUT
from .rag.chunking import chunk_corpus
from .rag.config import Settings, get_settings
from .rag.http import HttpError, request_json
from .rag.index import build_index, default_collection
from .rag.ollama import embed
from .rag.qdrant import QdrantStore

Request = Callable[..., dict]


def wait_for(url: str, request: Request = request_json, tries: int = 60, pause: float = 5) -> None:
    """Espera um serviço responder (útil porque os containers sobem em ordem diferente)."""
    for attempt in range(tries):
        try:
            request("GET", url, timeout=10)
            return
        except (ConnectionError, HttpError):
            if attempt == tries - 1:
                raise ConnectionError(f"O serviço em {url} não respondeu a tempo.") from None
            time.sleep(pause)


def missing_models(installed: list[str], wanted: list[str]) -> list[str]:
    """Modelos pedidos que ainda não estão instalados (aceita o sufixo ':latest')."""
    have = set(installed) | {name.removesuffix(":latest") for name in installed}
    return [model for model in wanted if model not in have]


def ensure_models(ollama_url: str, wanted: list[str], request: Request = request_json) -> None:
    tags = request("GET", f"{ollama_url}/api/tags")
    installed = [item["name"] for item in tags.get("models", [])]
    for model in missing_models(installed, wanted):
        print(f"Baixando o modelo {model} (pode demorar vários minutos)...")
        request("POST", f"{ollama_url}/api/pull", {"model": model, "stream": False}, timeout=3600)


def ensure_corpus(out: Path, fetch: Callable[..., int] = fetch_corpus) -> None:
    if (out / "manifest.json").exists():
        print("Corpus já existe, pulando.")
        return
    print(f"Baixando e preparando a documentação do FastAPI {DEFAULT_VERSION}...")
    if fetch(DEFAULT_VERSION, out) != 0:
        raise RuntimeError("Não consegui preparar o corpus.")


def ensure_index(settings: Settings, corpus: Path, strategy: str = "structure") -> None:
    name = default_collection(1000, 0, strategy)
    store = QdrantStore(settings.qdrant_url, name)
    if store.exists() and store.count() > 0:
        print(f"Índice '{name}' já existe ({store.count()} pedaços), pulando.")
        return
    chunks = chunk_corpus(corpus, 1000, 0, strategy)
    print(f"Criando o índice '{name}' com {len(chunks)} pedaços (alguns minutos)...")

    def embed_fn(texts: list[str]) -> list[list[float]]:
        return embed(texts, url=settings.ollama_url, model=settings.embed_model)

    def show(done: int, total: int) -> None:
        print(f"  {done}/{total} pedaços")

    build_index(chunks, embed_fn, store, 16, show)


def main() -> int:
    settings = get_settings()
    corpus = Path(os.getenv("CORPUS_DIR", str(DEFAULT_OUT)))
    strategy = os.getenv("CHUNK_STRATEGY", "structure")
    try:
        wait_for(f"{settings.qdrant_url}/collections")
        wait_for(f"{settings.ollama_url}/api/tags")
        ensure_models(settings.ollama_url, [settings.embed_model, settings.gen_model])
        ensure_corpus(corpus)
        ensure_index(settings, corpus, strategy)
    except (ConnectionError, HttpError, RuntimeError) as error:
        print(f"Erro na preparação: {error}")
        return 1
    print("Ambiente pronto.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
