"""Configuração lida das variáveis de ambiente (com valores padrão para uso local)."""

from __future__ import annotations

import os
from dataclasses import dataclass


@dataclass(frozen=True)
class Settings:
    ollama_url: str
    qdrant_url: str
    embed_model: str
    gen_model: str


def get_settings() -> Settings:
    return Settings(
        ollama_url=os.getenv("OLLAMA_URL", "http://localhost:11434").rstrip("/"),
        qdrant_url=os.getenv("QDRANT_URL", "http://localhost:6333").rstrip("/"),
        embed_model=os.getenv("EMBED_MODEL", "bge-m3"),
        gen_model=os.getenv("GEN_MODEL", "qwen2.5:3b"),
    )
