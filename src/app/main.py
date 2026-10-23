"""API do assistente RAG para documentação técnica.

No Marco 1 existe apenas o endpoint de saúde. A ingestão, a busca e a
geração de respostas entram a partir do Marco 2.
"""

import os

from fastapi import FastAPI

app = FastAPI(
    title="RAG de documentação técnica",
    description="Assistente que responde dúvidas sobre uma documentação, sempre citando a fonte.",
    version="0.1.0",
)


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
