"""Confere o arquivo de perguntas de avaliação (`eval/questions.jsonl`).

Cada pergunta com resposta precisa apontar para um trecho que existe de verdade no
corpus. Cada pergunta sem resposta precisa trazer termos que não aparecem em lugar
nenhum do corpus. Assim, nenhuma fonte "inventada" passa despercebida.

Uso (a partir da pasta `src`):

    python -m app.evaluation.check_questions          # confere a estrutura e as fontes
    python -m app.evaluation.check_questions --final  # confere também os totais (40 + 10)
"""

from __future__ import annotations

import argparse
import json
import re
from collections import Counter
from pathlib import Path
from typing import Any

from ..ingest.prepare import DEFAULT_OUT

DEFAULT_QUESTIONS = Path(__file__).resolve().parents[3] / "eval" / "questions.jsonl"

SPLITS = ("dev", "test")
REQUIRED_FIELDS = ("id", "split", "question", "answerable")
FINAL_TOTALS = {"answerable": 40, "unanswerable": 10, "dev": 20, "test": 30}


def normalize(text: str) -> str:
    """Troca qualquer sequência de espaços e quebras de linha por um espaço só."""
    return re.sub(r"\s+", " ", text).strip()


class Corpus:
    """Acesso ao texto do corpus, com os espaços normalizados."""

    def __init__(self, root: Path) -> None:
        self.root = root.resolve()
        self._files: dict[str, str | None] = {}
        self._all_lower: str | None = None

    def text_of(self, relative: str) -> str | None:
        if relative not in self._files:
            path = (self.root / relative).resolve()
            if path.is_relative_to(self.root) and path.is_file():
                self._files[relative] = normalize(path.read_text(encoding="utf-8"))
            else:
                self._files[relative] = None
        return self._files[relative]

    def all_text_lower(self) -> str:
        if self._all_lower is None:
            files = sorted(self.root.rglob("*.md"))
            texts = (normalize(path.read_text(encoding="utf-8")) for path in files)
            self._all_lower = "\n".join(texts).lower()
        return self._all_lower


def load_questions(path: Path) -> tuple[list[dict[str, Any]], list[str]]:
    """Lê o arquivo, uma pergunta por linha. Devolve as perguntas e os erros de leitura."""
    items: list[dict[str, Any]] = []
    errors: list[str] = []
    for number, line in enumerate(path.read_text(encoding="utf-8").splitlines(), start=1):
        if not line.strip():
            continue
        try:
            item = json.loads(line)
        except json.JSONDecodeError as error:
            errors.append(f"linha {number}: JSON inválido ({error.msg})")
            continue
        if not isinstance(item, dict):
            errors.append(f"linha {number}: esperado um objeto JSON")
            continue
        items.append(item)
    return items, errors


def _is_text(value: Any) -> bool:
    return isinstance(value, str) and bool(value.strip())


def validate_item(item: dict[str, Any], corpus: Corpus) -> list[str]:
    """Devolve os problemas de uma pergunta (lista vazia quando está tudo certo)."""
    qid = item.get("id", "?")
    errors = [f"{qid}: falta o campo '{name}'" for name in REQUIRED_FIELDS if name not in item]
    if errors:
        return errors

    if item["split"] not in SPLITS:
        errors.append(f"{qid}: 'split' deve ser 'dev' ou 'test'")
    if not _is_text(item["question"]):
        errors.append(f"{qid}: a pergunta está vazia")
    if not isinstance(item["answerable"], bool):
        return [*errors, f"{qid}: 'answerable' deve ser true ou false"]

    if item["answerable"]:
        errors += _validate_answerable(item, corpus)
    else:
        errors += _validate_unanswerable(item, corpus)
    return errors


def _validate_answerable(item: dict[str, Any], corpus: Corpus) -> list[str]:
    qid = item["id"]
    if not _is_text(item.get("expected_answer")):
        return [f"{qid}: falta a resposta esperada ('expected_answer')"]
    source_file, span = item.get("source_file"), item.get("source_span")
    if not _is_text(source_file) or not _is_text(span):
        return [f"{qid}: faltam 'source_file' e 'source_span'"]
    text = corpus.text_of(source_file)
    if text is None:
        return [f"{qid}: o arquivo '{source_file}' não existe no corpus"]
    if normalize(span) not in text:
        return [f"{qid}: o trecho 'source_span' não foi encontrado em '{source_file}'"]
    return []


def _validate_unanswerable(item: dict[str, Any], corpus: Corpus) -> list[str]:
    qid = item["id"]
    terms = item.get("forbidden_terms")
    if not isinstance(terms, list) or not terms or not all(_is_text(t) for t in terms):
        return [f"{qid}: perguntas sem resposta precisam de 'forbidden_terms' (lista de termos)"]
    everything = corpus.all_text_lower()
    return [
        f"{qid}: o termo '{term}' aparece no corpus, então a pergunta pode ter resposta"
        for term in terms
        if term.lower() in everything
    ]


def validate(items: list[dict[str, Any]], corpus: Corpus) -> list[str]:
    errors: list[str] = []
    seen: set[str] = set()
    for item in items:
        qid = item.get("id")
        if qid in seen:
            errors.append(f"{qid}: id repetido")
        seen.add(qid)
        errors += validate_item(item, corpus)
    return errors


def count_items(items: list[dict[str, Any]]) -> Counter[str]:
    counts: Counter[str] = Counter()
    for item in items:
        counts["answerable" if item.get("answerable") is True else "unanswerable"] += 1
        counts[str(item.get("split"))] += 1
    return counts


def check_final_totals(counts: Counter[str]) -> list[str]:
    return [
        f"total de '{name}': esperado {expected}, encontrado {counts[name]}"
        for name, expected in FINAL_TOTALS.items()
        if counts[name] != expected
    ]


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Confere as perguntas de avaliação.")
    parser.add_argument("--questions", type=Path, default=DEFAULT_QUESTIONS)
    parser.add_argument("--corpus", type=Path, default=DEFAULT_OUT)
    parser.add_argument("--final", action="store_true", help="exige os totais finais (40 + 10)")
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)

    for label, path in (("--questions", args.questions), ("--corpus", args.corpus)):
        if not path.exists():
            print(f"Erro: o caminho indicado em {label} não existe: {path}")
            return 1

    items, errors = load_questions(args.questions)
    errors += validate(items, Corpus(args.corpus))
    counts = count_items(items)
    if args.final:
        errors += check_final_totals(counts)

    print(f"Perguntas lidas: {len(items)}")
    print(f"Com resposta: {counts['answerable']} | Sem resposta: {counts['unanswerable']}")
    print(f"Desenvolvimento (dev): {counts['dev']} | Teste final (test): {counts['test']}")
    if errors:
        print(f"\n{len(errors)} problema(s) encontrado(s):")
        for error in errors:
            print(f"- {error}")
        return 1
    print("\nTudo certo.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
