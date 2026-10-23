"""Prepara o corpus: seleciona os arquivos da documentação, limpa e salva.

Uso (a partir da pasta `src`):

    python -m app.ingest.prepare --docs CAMINHO/docs/en/docs --docs-src CAMINHO/docs_src

O resultado vai para `data/raw/corpus`, na raiz do repositório (ou outra pasta,
com `--out`), junto com um `manifest.json` que lista cada arquivo incluído.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from .clean import clean_markdown, extract_title

# Pasta padrão de saída: `data/raw/corpus`, na raiz do repositório.
DEFAULT_OUT = Path(__file__).resolve().parents[3] / "data" / "raw" / "corpus"

# Pastas que não são texto da documentação (estilo, scripts, imagens) ou que são
# geradas a partir do código e têm quase nenhum texto (reference, resources).
EXCLUDED_DIRS = {"css", "js", "img", "reference", "resources"}

# Arquivos soltos que não ajudam a responder dúvidas técnicas: histórico de
# versões (grande e repetitivo), avisos do site e páginas sobre a comunidade.
EXCLUDED_FILES = {
    "_llm-test.md",
    "translation-banner.md",
    "release-notes.md",
    "newsletter.md",
    "management.md",
    "fastapi-people.md",
    "external-links.md",
    "help-fastapi.md",
    "translations.md",
    "contributing.md",
}


def iter_corpus_files(docs_root: Path):
    """Lista, em ordem fixa, os arquivos `.md` que entram no corpus."""
    for path in sorted(docs_root.rglob("*.md")):
        relative = path.relative_to(docs_root)
        if relative.parts[0] in EXCLUDED_DIRS:
            continue
        if len(relative.parts) == 1 and relative.name in EXCLUDED_FILES:
            continue
        yield path


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Limpa a documentação do FastAPI.")
    parser.add_argument("--docs", required=True, type=Path, help="pasta docs/en/docs")
    parser.add_argument("--docs-src", required=True, type=Path, help="pasta docs_src")
    parser.add_argument("--out", type=Path, default=DEFAULT_OUT, help="pasta de saída")
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)

    for label, folder in (("--docs", args.docs), ("--docs-src", args.docs_src)):
        if not folder.is_dir():
            print(f"Erro: a pasta indicada em {label} não existe: {folder}")
            return 1

    entries = []
    total_chars = 0
    total_resolved = 0
    total_missing = 0

    for path in iter_corpus_files(args.docs):
        relative = path.relative_to(args.docs)
        text, report = clean_markdown(path.read_text(encoding="utf-8"), args.docs_src)

        destination = args.out / relative
        destination.parent.mkdir(parents=True, exist_ok=True)
        destination.write_text(text, encoding="utf-8")

        total_chars += len(text)
        total_resolved += report.resolved
        total_missing += len(report.missing)
        entries.append(
            {
                "source": relative.as_posix(),
                "title": extract_title(text, relative.stem),
                "chars": len(text),
                "includes_resolved": report.resolved,
                "includes_missing": report.missing,
            }
        )

    manifest = {
        "total_files": len(entries),
        "total_chars": total_chars,
        "includes_resolved": total_resolved,
        "includes_missing": total_missing,
        "files": entries,
    }
    args.out.mkdir(parents=True, exist_ok=True)
    (args.out / "manifest.json").write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8"
    )

    print(f"Arquivos no corpus: {len(entries)}")
    print(f"Caracteres no total: {total_chars}")
    print(f"Exemplos de código inseridos: {total_resolved}")
    print(f"Exemplos de código não encontrados: {total_missing}")
    print(f"Saída em: {args.out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
