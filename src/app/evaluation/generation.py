"""Mede a qualidade das respostas: citação, fonte correta, recusas e alucinações.

Para cada pergunta do conjunto escolhido (padrão: `dev`), roda o assistente completo e mede:

- **citação válida**: das perguntas com resposta que o sistema respondeu, quantas citam
  pelo menos um trecho que existe;
- **fonte correta**: das perguntas com resposta, quantas foram respondidas citando um trecho
  que cobre o trecho-fonte esperado (a resposta se apoia na evidência certa);
- **recusa correta**: das perguntas sem resposta, quantas o sistema recusou;
- **recusa indevida**: das perguntas com resposta, quantas o sistema recusou;
- **alucinações**: perguntas sem resposta que ele respondeu (e, entre elas, as que usam termos
  proibidos) e respostas sem nenhuma citação válida.

A qualidade do texto da resposta não é medida automaticamente: o script grava um arquivo
`.md` para o aluno marcar, à mão, se cada resposta bate com a esperada.

Uso (a partir da pasta `src`):

    python -m app.evaluation.generation                 # dev
    python -m app.evaluation.generation --final         # test (só uma vez, no fim!)
"""

from __future__ import annotations

import argparse
import json
import re
from pathlib import Path
from typing import Any

from ..ingest.prepare import DEFAULT_OUT
from ..rag.chunking import STRATEGIES
from ..rag.index import default_collection
from .check_questions import DEFAULT_QUESTIONS, load_questions
from .retrieval import RESULTS_DIR, covers, find_span


def rate(count: int, total: int) -> float | None:
    return count / total if total else None


def score_answers(
    questions: list[dict[str, Any]],
    answers: dict[str, dict[str, Any]],
    corpus: Path,
) -> dict[str, Any]:
    """Calcula as métricas a partir das respostas já geradas (`answers[id]`)."""
    answerable = [q for q in questions if q["answerable"]]
    unanswerable = [q for q in questions if not q["answerable"]]

    answered = valid_citation = right_source = wrongful_refusals = 0
    cases: list[dict[str, Any]] = []
    for item in answerable:
        answer = answers[item["id"]]
        text = (corpus / item["source_file"]).read_text(encoding="utf-8")
        span_range = find_span(text, item["source_span"])
        if span_range is None:
            raise ValueError(f"{item['id']}: trecho-fonte não achado em {item['source_file']}")
        cited = [answer["retrieved"][n - 1] for n in answer["cited"]]
        hit = any(covers(c, item["source_file"], span_range) for c in cited)
        if answer["refused"]:
            wrongful_refusals += 1
            problem = "recusa indevida"
        else:
            answered += 1
            valid_citation += bool(cited)
            right_source += hit
            problem = "" if hit else ("sem citação" if not cited else "fonte errada")
        if problem:
            cases.append({"id": item["id"], "question": item["question"], "problem": problem})

    correct_refusals = answered_unanswerable = forbidden_used = 0
    for item in unanswerable:
        answer = answers[item["id"]]
        if answer["refused"]:
            correct_refusals += 1
            continue
        answered_unanswerable += 1
        lowered = answer["answer"].lower()
        used = [t for t in item.get("forbidden_terms", []) if t.lower() in lowered]
        forbidden_used += bool(used)
        cases.append(
            {
                "id": item["id"],
                "question": item["question"],
                "problem": "alucinação: respondeu pergunta sem resposta",
                "forbidden_terms_in_answer": used,
            }
        )

    return {
        "answerable": len(answerable),
        "unanswerable": len(unanswerable),
        "answered": answered,
        "valid_citation_rate": rate(valid_citation, answered),
        "right_source_rate": rate(right_source, len(answerable)),
        "wrongful_refusal_rate": rate(wrongful_refusals, len(answerable)),
        "correct_refusal_rate": rate(correct_refusals, len(unanswerable)),
        "unanswerable_answered": answered_unanswerable,
        "unanswerable_with_forbidden_terms": forbidden_used,
        "problem_cases": cases,
    }


def review_markdown(questions: list[dict[str, Any]], answers: dict[str, dict[str, Any]]) -> str:
    """Roteiro para o aluno conferir à mão se cada resposta bate com a esperada."""
    lines = ["# Conferência manual das respostas", ""]
    lines += ["Marque `[x]` se a resposta está correta.", ""]
    for item in questions:
        answer = answers[item["id"]]
        lines.append(f"## {item['id']}: {item['question']}")
        if item["answerable"]:
            lines.append(f"- Esperado: {item['expected_answer']}")
        else:
            lines.append("- Esperado: recusar (a documentação não tem a resposta)")
        lines.append(f"- Sistema ({answer['reason']}): {' '.join(answer['answer'].split())}")
        lines.append("- [ ] correta")
        lines.append("")
    return "\n".join(lines)


def score_review(markdown: str) -> dict[str, Any]:
    """Conta as marcações `[x]` do arquivo de conferência manual preenchido pelo aluno."""
    answerable = [0, 0]  # certas, total
    unanswerable = [0, 0]
    for section in markdown.split("\n## ")[1:]:
        counts = unanswerable if "Esperado: recusar" in section else answerable
        counts[1] += 1
        counts[0] += re.search(r"-\s*\[\s*x\s*\]", section, re.IGNORECASE) is not None
    return {
        "answerable_correct": answerable[0],
        "answerable_total": answerable[1],
        "answerable_rate": rate(*answerable),
        "unanswerable_correct": unanswerable[0],
        "unanswerable_total": unanswerable[1],
        "unanswerable_rate": rate(*unanswerable),
    }


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Mede citações, recusas e alucinações.")
    parser.add_argument("--questions", type=Path, default=DEFAULT_QUESTIONS)
    parser.add_argument("--corpus", type=Path, default=DEFAULT_OUT)
    parser.add_argument("--strategy", choices=STRATEGIES, default="structure")
    parser.add_argument("--size", type=int, default=1000)
    parser.add_argument("--overlap", type=int, default=0)
    parser.add_argument("--collection")
    parser.add_argument("--final", action="store_true", help="usa o conjunto test (uma vez!)")
    parser.add_argument("--label", default="", help="sufixo nos arquivos (ex.: v4)")
    parser.add_argument(
        "--conferencia",
        type=Path,
        help="só calcula a taxa de acerto do arquivo de conferência manual já preenchido",
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    from ..rag.ask import build_pipeline  # aqui dentro: só a linha de comando precisa do Ollama

    args = build_parser().parse_args(argv)
    if args.conferencia:
        review = score_review(args.conferencia.read_text(encoding="utf-8"))
        print("Acerto conferido à mão:")
        for label, key in (("com resposta", "answerable"), ("sem resposta", "unanswerable")):
            print(f"  perguntas {label}: {review[key + '_correct']}/{review[key + '_total']}")
        return 0
    split = "test" if args.final else "dev"
    items, errors = load_questions(args.questions)
    if errors:
        print("Problemas no arquivo de perguntas:", *errors, sep="\n- ")
        return 1
    questions = [q for q in items if q.get("split") == split]
    name = args.collection or default_collection(args.size, args.overlap, args.strategy)

    try:
        pipeline = build_pipeline(args.corpus, args.strategy, args.size, args.overlap, 0.0, name)
        answers: dict[str, dict[str, Any]] = {}
        for number, item in enumerate(questions, start=1):
            answer = pipeline.ask(item["question"])
            answers[item["id"]] = answer.to_dict()
            print(f"  {number}/{len(questions)} {item['id']} | {answer.reason}")
    except ConnectionError as error:
        print(f"Erro: {error}")
        return 1

    result = score_answers(questions, answers, args.corpus)
    result["answers"] = answers
    RESULTS_DIR.mkdir(parents=True, exist_ok=True)
    suffix = f"-{args.label}" if args.label else ""
    out = RESULTS_DIR / f"generation-{name}-{split}{suffix}.json"
    out.write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8")
    review = RESULTS_DIR / f"generation-{name}-{split}{suffix}-conferencia.md"
    review.write_text(review_markdown(questions, answers), encoding="utf-8")

    def show(label: str, value: float | None) -> str:
        return f"{label}: {'n/a' if value is None else f'{value:.3f}'}"

    print(f"\nColeção: {name} | conjunto: {split}")
    print(f"Com resposta: {result['answerable']} | sem resposta: {result['unanswerable']}")
    print(show("Citação válida (entre as respondidas)", result["valid_citation_rate"]))
    print(show("Fonte correta (entre as com resposta)", result["right_source_rate"]))
    print(show("Recusa indevida", result["wrongful_refusal_rate"]))
    print(show("Recusa correta", result["correct_refusal_rate"]))
    print(f"Perguntas sem resposta que o sistema respondeu: {result['unanswerable_answered']}")
    for case in result["problem_cases"]:
        print(f"  - {case['id']}: {case['problem']} | {case['question']}")
    print(f"\nResultado salvo em: {out}")
    print(f"Para conferir à mão: {review}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
