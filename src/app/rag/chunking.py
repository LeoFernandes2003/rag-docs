"""Divisão dos textos em pedaços (chunks).

Estratégia do baseline: janelas de tamanho fixo, em caracteres, sem respeitar
o conteúdo. É a mais simples; as outras (com sobreposição e por títulos) serão
comparadas com ela nos experimentos.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class Chunk:
    source_file: str  # caminho relativo dentro do corpus, como em eval/questions.jsonl
    index: int  # posição do pedaço dentro do arquivo
    start: int  # caractere inicial no arquivo
    end: int  # caractere final (exclusivo) no arquivo
    text: str


def fixed_windows(length: int, size: int, overlap: int = 0) -> list[tuple[int, int]]:
    """Calcula as janelas (início, fim) para um texto de `length` caracteres."""
    if size <= 0:
        raise ValueError("o tamanho do pedaço deve ser maior que zero")
    if not 0 <= overlap < size:
        raise ValueError("a sobreposição deve estar entre 0 e o tamanho do pedaço menos 1")
    step = size - overlap
    windows = []
    start = 0
    while start < length:
        end = min(start + size, length)
        windows.append((start, end))
        if end == length:
            break
        start += step
    return windows


def chunk_text(source_file: str, text: str, size: int, overlap: int = 0) -> list[Chunk]:
    """Divide um texto; ignora pedaços formados só por espaços em branco."""
    chunks = []
    for start, end in fixed_windows(len(text), size, overlap):
        piece = text[start:end]
        if piece.strip():
            chunks.append(Chunk(source_file, len(chunks), start, end, piece))
    return chunks


def chunk_corpus(corpus: Path, size: int, overlap: int = 0) -> list[Chunk]:
    """Divide todos os arquivos .md do corpus, em ordem alfabética."""
    chunks: list[Chunk] = []
    for path in sorted(corpus.rglob("*.md")):
        name = path.relative_to(corpus).as_posix()
        chunks += chunk_text(name, path.read_text(encoding="utf-8"), size, overlap)
    return chunks
