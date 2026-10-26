"""Sorteia passagens do corpus para servir de base às perguntas de avaliação.

Sortear as passagens, em vez de escolhê-las a dedo, evita que as perguntas fiquem
só nos assuntos mais fáceis. O sorteio usa uma semente fixa, então qualquer pessoa
que rodar o script com o mesmo corpus obtém as mesmas passagens.

Uso (a partir da pasta `src`):

    python -m app.evaluation.sample_candidates

Gera `eval/candidates.md` (para ler) e `eval/candidates.json` (para os scripts).
"""

from __future__ import annotations

import argparse
import json
import random
import re
from pathlib import Path

from ..ingest.clean import split_segments
from ..ingest.prepare import DEFAULT_OUT

DEFAULT_EVAL_DIR = Path(__file__).resolve().parents[3] / "eval"

MIN_CHARS = 150
MAX_CHARS = 700
IGNORED_STARTS = ("#", "|", ">", "![", "[Image", "```", "~~~", "* ", "- ")


def is_eligible(block: str) -> bool:
    """Diz se um parágrafo serve como base de pergunta: texto corrido, de tamanho médio."""
    if not MIN_CHARS <= len(block) <= MAX_CHARS:
        return False
    if "\n" in block:
        return False
    if block.startswith(IGNORED_STARTS) or re.match(r"\d+\.\s", block):
        return False
    prose_chars = sum(ch.isalpha() or ch == " " for ch in block)
    if prose_chars / len(block) < 0.8:
        return False
    if block.count("](") > 1:
        return False
    return any(mark in block for mark in ".!?")


def collect_paragraphs(corpus: Path) -> dict[str, list[str]]:
    """Lista, por arquivo, os parágrafos elegíveis (fora de blocos de código)."""
    result: dict[str, list[str]] = {}
    for path in sorted(corpus.rglob("*.md")):
        blocks = []
        for kind, segment in split_segments(path.read_text(encoding="utf-8")):
            if kind != "text":
                continue
            for block in re.split(r"\n\s*\n", segment):
                block = block.strip()
                if is_eligible(block):
                    blocks.append(block)
        if blocks:
            result[path.relative_to(corpus).as_posix()] = blocks
    return result


def sample_candidates(paragraphs: dict[str, list[str]], n: int, seed: int) -> list[dict[str, str]]:
    """Sorteia `n` arquivos diferentes e, em cada um, um parágrafo."""
    rng = random.Random(seed)
    files = rng.sample(sorted(paragraphs), min(n, len(paragraphs)))
    return [
        {"id": f"C{index:02d}", "source_file": name, "passage": rng.choice(paragraphs[name])}
        for index, name in enumerate(files, start=1)
    ]


def render_markdown(candidates: list[dict[str, str]], seed: int) -> str:
    lines = [
        "# Passagens sorteadas para as perguntas de avaliação",
        "",
        f"Sorteio com semente {seed}: um parágrafo de cada arquivo sorteado do corpus.",
        "",
    ]
    for candidate in candidates:
        lines += [
            f"## {candidate['id']} · `{candidate['source_file']}`",
            "",
            "````text",
            candidate["passage"],
            "````",
            "",
        ]
    return "\n".join(lines)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Sorteia passagens do corpus.")
    parser.add_argument("--corpus", type=Path, default=DEFAULT_OUT, help="pasta do corpus limpo")
    parser.add_argument("--out-dir", type=Path, default=DEFAULT_EVAL_DIR, help="pasta de saída")
    parser.add_argument("--n", type=int, default=60, help="quantas passagens sortear")
    parser.add_argument("--seed", type=int, default=42, help="semente do sorteio")
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)

    if not args.corpus.is_dir():
        print(f"Erro: a pasta do corpus não existe: {args.corpus}")
        print("Rode antes: python -m app.ingest.prepare ...")
        return 1

    paragraphs = collect_paragraphs(args.corpus)
    candidates = sample_candidates(paragraphs, args.n, args.seed)

    args.out_dir.mkdir(parents=True, exist_ok=True)
    (args.out_dir / "candidates.md").write_text(
        render_markdown(candidates, args.seed), encoding="utf-8"
    )
    (args.out_dir / "candidates.json").write_text(
        json.dumps(candidates, ensure_ascii=False, indent=2), encoding="utf-8"
    )

    print(f"Arquivos com parágrafos elegíveis: {len(paragraphs)}")
    print(f"Passagens sorteadas: {len(candidates)}")
    print(f"Saída em: {args.out_dir}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
