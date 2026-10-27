"""Mede a qualidade da busca (Recall@k) com as perguntas de `eval/questions.jsonl`.

Uma pergunta com resposta é considerada acertada quando algum dos `k` pedaços
devolvidos pela busca cobre o trecho-fonte (`source_span`) do mesmo arquivo.

Regra do protocolo: as perguntas de teste final (`test`) NÃO podem ser usadas
para ajustar o sistema. Por isso o padrão é medir só as de desenvolvimento
(`dev`); o conjunto `test` exige a opção `--final`, usada uma única vez, no fim.

Uso (a partir da pasta `src`):

    python -m app.evaluation.retrieval                          # dev, baseline
    python -m app.evaluation.retrieval --strategy structure --mode hybrid
    python -m app.evaluation.retrieval --final                  # test (só no fim!)
"""

from __future__ import annotations

import argparse
import json
import re
from collections.abc import Callable
from pathlib import Path
from typing import Any

from ..ingest.prepare import DEFAULT_OUT
from ..rag.chunking import STRATEGIES, chunk_corpus
from ..rag.config import get_settings
from ..rag.index import default_collection
from ..rag.ollama import embed
from ..rag.qdrant import QdrantStore
from ..rag.retrieve import MODES, build_searcher
from ..rag.translate import translate_to_english
from .check_questions import DEFAULT_QUESTIONS, load_questions

RESULTS_DIR = DEFAULT_QUESTIONS.parent / "results"


def find_span(text: str, span: str) -> tuple[int, int] | None:
    """Acha o trecho no texto ignorando diferenças de espaços e quebras de linha."""
    words = span.split()
    if not words:
        return None
    match = re.search(r"\s+".join(re.escape(word) for word in words), text)
    return (match.start(), match.end()) if match else None


def covers(payload: dict[str, Any], source_file: str, span_range: tuple[int, int]) -> bool:
    """Diz se um pedaço devolvido pela busca se sobrepõe ao trecho-fonte."""
    if payload["source_file"] != source_file:
        return False
    return payload["start"] < span_range[1] and span_range[0] < payload["end"]


def evaluate(
    questions: list[dict[str, Any]],
    corpus: Path,
    search_fn: Callable[[str], list[dict[str, Any]]],
) -> dict[str, Any]:
    """Calcula o Recall@k das perguntas com resposta. `search_fn` devolve os pedaços."""
    hits = 0
    misses = []
    answerable = [q for q in questions if q.get("answerable") is True]
    for item in answerable:
        text = (corpus / item["source_file"]).read_text(encoding="utf-8")
        span_range = find_span(text, item["source_span"])
        if span_range is None:
            raise ValueError(
                f"{item['id']}: o trecho-fonte não foi achado em {item['source_file']}"
            )
        retrieved = [point["payload"] for point in search_fn(item["question"])]
        if any(covers(p, item["source_file"], span_range) for p in retrieved):
            hits += 1
        else:
            misses.append(
                {
                    "id": item["id"],
                    "question": item["question"],
                    "source_file": item["source_file"],
                    "retrieved_files": [p["source_file"] for p in retrieved],
                }
            )
    total = len(answerable)
    return {
        "questions": total,
        "hits": hits,
        "recall": hits / total if total else 0.0,
        "misses": misses,
    }


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Mede o Recall@k da busca.")
    parser.add_argument("--questions", type=Path, default=DEFAULT_QUESTIONS)
    parser.add_argument("--corpus", type=Path, default=DEFAULT_OUT)
    parser.add_argument("--mode", choices=MODES, default="dense", help="tipo de busca")
    parser.add_argument(
        "--translate",
        action="store_true",
        help="traduz a pergunta para inglês antes da busca por palavras (bm25/hybrid)",
    )
    parser.add_argument("--strategy", choices=STRATEGIES, default="fixed")
    parser.add_argument("--size", type=int, default=1000)
    parser.add_argument("--overlap", type=int, default=0)
    parser.add_argument("--collection", help="coleção (padrão: a da estratégia escolhida)")
    parser.add_argument("--top", type=int, default=5, help="k do Recall@k")
    parser.add_argument(
        "--final",
        action="store_true",
        help="mede o conjunto de teste final (use só uma vez, no fim dos experimentos)",
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    split = "test" if args.final else "dev"
    settings = get_settings()
    name = args.collection or default_collection(args.size, args.overlap, args.strategy)
    store = QdrantStore(settings.qdrant_url, name)

    items, errors = load_questions(args.questions)
    if errors:
        print("Problemas no arquivo de perguntas:", *errors, sep="\n- ")
        return 1
    questions = [q for q in items if q.get("split") == split]

    def embed_fn(texts: list[str]) -> list[list[float]]:
        return embed(texts, url=settings.ollama_url, model=settings.embed_model)

    chunks = []
    if args.mode != "dense":
        chunks = chunk_corpus(args.corpus, args.size, args.overlap, args.strategy)
    translations: dict[str, str] = {}
    if args.translate and args.mode != "dense":
        try:
            for item in questions:
                if item.get("answerable") is True:
                    translations[item["question"]] = translate_to_english(
                        item["question"], url=settings.ollama_url, model=settings.gen_model
                    )
        except ConnectionError as error:
            print(f"Erro: {error}")
            return 1
        print("Traduções usadas na busca por palavras:")
        for original, english in translations.items():
            print(f"  {original}\n    -> {english}")
        print()
    searcher = build_searcher(
        args.mode,
        embed_fn,
        store,
        chunks,
        args.top,
        lexical_query=lambda question: translations.get(question, question),
    )

    try:
        result = evaluate(questions, args.corpus, searcher)
    except ConnectionError as error:
        print(f"Erro: {error}")
        return 1

    label = f"{args.mode}-traducao" if translations else args.mode
    print(f"Coleção: {name} | busca: {label} | conjunto: {split} | Recall@{args.top}")
    print(f"Perguntas com resposta: {result['questions']}")
    print(f"Acertos: {result['hits']}")
    print(f"Recall@{args.top}: {result['recall']:.3f}")
    for miss in result["misses"]:
        print(f"\nErrou {miss['id']}: {miss['question']}")
        print(f"  deveria achar: {miss['source_file']}")
        print(f"  achou: {', '.join(miss['retrieved_files'])}")

    RESULTS_DIR.mkdir(parents=True, exist_ok=True)
    result["translations"] = translations
    out = RESULTS_DIR / f"retrieval-{name}-{label}-{split}-top{args.top}.json"
    out.write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"\nResultado salvo em: {out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
