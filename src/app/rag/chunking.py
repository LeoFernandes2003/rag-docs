"""Divisão dos textos em pedaços (chunks).

Estratégia do baseline: janelas de tamanho fixo, em caracteres, sem respeitar
o conteúdo. É a mais simples; as outras (com sobreposição e por títulos) serão
comparadas com ela nos experimentos.
"""

from __future__ import annotations

import re
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


HEADING_RE = re.compile(r"^#{1,6}\s")
FENCE_RE = re.compile(r"^(`{3,}|~{3,})")


def markdown_blocks(text: str) -> list[tuple[int, int, bool]]:
    """Separa o texto em blocos (início, fim, começa_com_título).

    Os blocos são separados por linhas em branco ou por títulos. Um bloco de código
    (entre cercas ``` ou ~~~) nunca é cortado ao meio, mesmo que tenha linhas em branco.
    """
    blocks: list[tuple[int, int, bool]] = []
    start = end = None
    is_heading = False
    in_fence = False
    fence_char, fence_len = "", 0
    position = 0

    def close() -> None:
        nonlocal start, end, is_heading
        if start is not None:
            blocks.append((start, end, is_heading))
        start = end = None
        is_heading = False

    for line in text.splitlines(keepends=True):
        line_start = position
        position += len(line)
        line_end = line_start + len(line.rstrip("\r\n"))
        stripped = line.strip()
        fence = FENCE_RE.match(stripped)

        if in_fence:
            end = line_end
            if fence and fence.group(1)[0] == fence_char and len(fence.group(1)) >= fence_len:
                if stripped == fence.group(1):
                    in_fence = False
            continue
        if not stripped:
            close()
            continue
        if HEADING_RE.match(stripped):
            close()
            start, end, is_heading = line_start, line_end, True
            continue
        if start is None:
            start = line_start
        end = line_end
        if fence:
            in_fence, fence_char, fence_len = True, fence.group(1)[0], len(fence.group(1))
    close()
    return blocks


def chunk_structure(source_file: str, text: str, size: int, min_size: int = 200) -> list[Chunk]:
    """Agrupa blocos inteiros até `size` caracteres, começando um pedaço novo em cada título.

    Um título só abre pedaço novo se o pedaço atual já tiver `min_size` caracteres,
    para não gerar pedaços minúsculos. Um bloco maior que `size` é cortado em janelas fixas.
    """
    chunks: list[Chunk] = []

    def emit(first: int, last: int) -> None:
        piece = text[first:last]
        if piece.strip():
            chunks.append(Chunk(source_file, len(chunks), first, last, piece))

    current_start = current_end = None
    for start, end, heading in markdown_blocks(text):
        if end - start > size:
            if current_start is not None:
                emit(current_start, current_end)
                current_start = current_end = None
            for first, last in fixed_windows(end - start, size):
                emit(start + first, start + last)
            continue
        if current_start is None:
            current_start, current_end = start, end
            continue
        too_big = end - current_start > size
        new_section = heading and (current_end - current_start) >= min_size
        if too_big or new_section:
            emit(current_start, current_end)
            current_start, current_end = start, end
        else:
            current_end = end
    if current_start is not None:
        emit(current_start, current_end)
    return chunks


STRATEGIES = ("fixed", "structure")


def chunk_corpus(
    corpus: Path, size: int, overlap: int = 0, strategy: str = "fixed"
) -> list[Chunk]:
    """Divide todos os arquivos .md do corpus, em ordem alfabética."""
    if strategy not in STRATEGIES:
        raise ValueError(f"estratégia desconhecida: {strategy}")
    chunks: list[Chunk] = []
    for path in sorted(corpus.rglob("*.md")):
        name = path.relative_to(corpus).as_posix()
        text = path.read_text(encoding="utf-8")
        if strategy == "structure":
            chunks += chunk_structure(name, text, size)
        else:
            chunks += chunk_text(name, text, size, overlap)
    return chunks
