"""Baixa a documentação do FastAPI (uma versão fixa) e prepara o corpus.

É o que permite reproduzir o projeto do zero: nenhum arquivo da documentação fica no Git,
o corpus é gerado a partir do código-fonte oficial (licença MIT) da versão escolhida.

Uso (a partir da pasta `src`):

    python -m app.ingest.fetch                      # baixa a versão padrão e gera o corpus
    python -m app.ingest.fetch --version 0.162.0 --out ../data/raw/corpus
"""

from __future__ import annotations

import argparse
import tarfile
import tempfile
import urllib.request
from collections.abc import Callable
from pathlib import Path

from . import prepare

DEFAULT_VERSION = "0.162.0"
URL = "https://github.com/fastapi/fastapi/archive/refs/tags/{version}.tar.gz"

Download = Callable[[str, Path], None]


def download_file(url: str, destination: Path) -> None:
    """Baixa um arquivo da internet para o disco."""
    try:
        with urllib.request.urlopen(url, timeout=120) as response:  # noqa: S310
            destination.write_bytes(response.read())
    except OSError as error:
        raise ConnectionError(f"Não consegui baixar {url}: {error}") from error


def fetch_corpus(
    version: str = DEFAULT_VERSION,
    out: Path = prepare.DEFAULT_OUT,
    download: Download = download_file,
) -> int:
    """Baixa o código-fonte da versão, extrai e gera o corpus em `out`."""
    with tempfile.TemporaryDirectory() as temp:
        folder = Path(temp)
        archive = folder / "fastapi.tar.gz"
        download(URL.format(version=version), archive)
        with tarfile.open(archive) as tar:
            tar.extractall(folder / "src", filter="data")
        roots = [p for p in (folder / "src").iterdir() if p.is_dir()]
        if len(roots) != 1:
            raise ValueError("O arquivo baixado não tem a estrutura esperada.")
        docs = roots[0] / "docs" / "en" / "docs"
        docs_src = roots[0] / "docs_src"
        return prepare.main(["--docs", str(docs), "--docs-src", str(docs_src), "--out", str(out)])


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Baixa e prepara o corpus do FastAPI.")
    parser.add_argument("--version", default=DEFAULT_VERSION)
    parser.add_argument("--out", type=Path, default=prepare.DEFAULT_OUT)
    args = parser.parse_args(argv)
    try:
        return fetch_corpus(args.version, args.out)
    except (ConnectionError, ValueError) as error:
        print(f"Erro: {error}")
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
