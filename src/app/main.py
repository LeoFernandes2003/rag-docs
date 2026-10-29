"""API do assistente RAG para documentação técnica.

Endereços:
- `GET /health`: indica que o serviço está de pé.
- `GET /config`: mostra a configuração não secreta.
- `POST /ask`: recebe `{"question": "..."}` e devolve a resposta com as fontes citadas,
  ou a recusa quando a documentação não tem evidência suficiente.
"""

import os
from functools import lru_cache
from pathlib import Path
from typing import Annotated, Any

from fastapi import Depends, FastAPI, HTTPException
from pydantic import BaseModel, Field

from .rag.http import HttpError
from .rag.pipeline import RagPipeline

app = FastAPI(
    title="RAG de documentação técnica",
    description="Assistente que responde dúvidas sobre uma documentação, sempre citando a fonte.",
    version="0.2.0",
)


class AskRequest(BaseModel):
    question: str = Field(min_length=3, max_length=500, description="A pergunta do usuário.")


@lru_cache(maxsize=1)
def get_pipeline() -> RagPipeline:
    """Monta o assistente uma única vez (lê o corpus e liga aos serviços)."""
    from .ingest.prepare import DEFAULT_OUT
    from .rag.ask import build_pipeline

    corpus = Path(os.getenv("CORPUS_DIR", str(DEFAULT_OUT)))
    strategy = os.getenv("CHUNK_STRATEGY", "structure")
    return build_pipeline(corpus, strategy, 1000, 0, 0.0, None)


@app.get("/health")
def health() -> dict[str, str]:
    """Indica que o serviço está de pé."""
    return {"status": "ok"}


@app.get("/config")
def config() -> dict[str, str]:
    """Mostra a configuração não secreta, útil para conferir o ambiente."""
    return {
        "ollama_url": os.getenv("OLLAMA_URL", "http://localhost:11434"),
        "qdrant_url": os.getenv("QDRANT_URL", "http://localhost:6333"),
        "gen_model": os.getenv("GEN_MODEL", "qwen2.5:3b"),
        "embed_model": os.getenv("EMBED_MODEL", "bge-m3"),
    }


@app.post("/ask")
def ask(
    request: AskRequest, pipeline: Annotated[RagPipeline, Depends(get_pipeline)]
) -> dict[str, Any]:
    """Responde a pergunta com citações, ou recusa quando não há evidência."""
    try:
        return pipeline.ask(request.question).to_dict()
    except ConnectionError as error:
        raise HTTPException(status_code=503, detail=str(error)) from error
    except HttpError as error:
        raise HTTPException(
            status_code=503,
            detail="Um serviço respondeu com erro. O índice do Qdrant foi criado? "
            f"(código {error.status})",
        ) from error
