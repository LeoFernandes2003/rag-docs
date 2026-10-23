"""Limpeza dos arquivos Markdown da documentação do FastAPI.

Os textos originais são escritos para virar um site e trazem "sujeira" que
atrapalha a busca:

- exemplos de código que ficam em outra pasta (`docs_src`) e aparecem no texto
  apenas como uma indicação, por exemplo ``{* ../../docs_src/x/y.py *}``;
- enfeites de HTML (`<font>`, `<span>`, `<img>`, ...) no texto e nos blocos de terminal;
- marcadores do site, como ``{ #first-steps }`` nos títulos e ``/// tip`` nas dicas.

Regra importante: exemplos de código (blocos com três crases) não são alterados,
porque muitos deles são HTML de verdade, como `<form>` e `<button>`. A única
exceção são os blocos `console`, onde ficam os enfeites de cor do terminal.

Este módulo usa só a biblioteca padrão do Python.
"""

from __future__ import annotations

import html
import re
from dataclasses import dataclass, field
from pathlib import Path

# Linha que contém só a indicação de um arquivo de código, com opções opcionais
# (por exemplo `hl[3]`, que destaca linhas e não nos interessa).
INCLUDE_RE = re.compile(r"^\{\*[ \t]+(\S+)(?:[ \t]+(.*?))?[ \t]+\*\}[ \t]*$", re.MULTILINE)

# Início e fim de um bloco de código: ``` ou ~~~, com o nome da linguagem no início.
FENCE_RE = re.compile(r"^\s*(`{3,}|~{3,})\s*([\w.+-]*)")

# Enfeites de cor e de layout que aparecem nos blocos de terminal e nas páginas.
DECORATIVE_TAG_RE = re.compile(r"</?(?:font|span|u|b|div|br)\b[^>]*>", re.IGNORECASE)

# HTML que tem equivalente simples em Markdown (só fora dos blocos de código).
HTML_COMMENT_RE = re.compile(r"<!--.*?-->", re.DOTALL)
CODE_TAG_RE = re.compile(r"<code>(.*?)</code>", re.DOTALL)
KBD_TAG_RE = re.compile(r"<kbd>(.*?)</kbd>", re.DOTALL)
STRONG_TAG_RE = re.compile(r"<strong>(.*?)</strong>", re.DOTALL)
ABBR_RE = re.compile(r'<(?:abbr|dfn) title="([^"]*)">(.*?)</(?:abbr|dfn)>', re.DOTALL)
LINK_TAG_RE = re.compile(r'<a\s[^>]*?href="([^"]*)"[^>]*>(.*?)</a>', re.DOTALL)
IMG_TAG_RE = re.compile(r"<img\b[^>]*>", re.DOTALL)
IMG_ALT_RE = re.compile(r'\balt="([^"]*)"')
MD_IMAGE_RE = re.compile(r"!\[([^\]]*)\]\([^)]*\)")

# Título com marcador de âncora: "# First Steps { #first-steps }".
HEADING_ANCHOR_RE = re.compile(r"^(#{1,6}\s.*?)\s*\{\s*#[\w.-]+\s*\}\s*$")

# Blocos do site: "/// tip" abre e "///" fecha, às vezes com espaços na frente
# (dentro de listas). Com 4 barras são as abas.
ADMONITION_OPEN_RE = re.compile(r"^(\s*)/{3,}\s*([\w-]+)(?:\s*\|\s*(.*?))?\s*$")
ADMONITION_CLOSE_RE = re.compile(r"^\s*/{3,}\s*$")

LANGUAGES = {
    ".py": "python",
    ".js": "javascript",
    ".ts": "typescript",
    ".html": "html",
    ".json": "json",
    ".yml": "yaml",
    ".yaml": "yaml",
    ".toml": "toml",
    ".sh": "bash",
    ".md": "markdown",
}


@dataclass
class CleanReport:
    """Resumo do que aconteceu na limpeza de um arquivo."""

    resolved: int = 0
    missing: list[str] = field(default_factory=list)


def split_segments(text: str) -> list[tuple[str, str]]:
    """Separa o texto em pedaços: "text" (fora de código), "console" e "code".

    Os pedaços de código incluem as linhas com as três crases. Juntando todos com
    quebra de linha, volta-se exatamente ao texto original.
    """
    segments: list[tuple[str, str]] = []
    buffer: list[str] = []
    kind = "text"
    marker = ""

    for line in text.split("\n"):
        fence = FENCE_RE.match(line)
        if kind == "text":
            if fence:
                if buffer:
                    segments.append(("text", "\n".join(buffer)))
                language = fence.group(2).lower()
                kind = "console" if language == "console" else "code"
                marker = fence.group(1)[0]
                buffer = [line]
            else:
                buffer.append(line)
        else:
            buffer.append(line)
            if fence and fence.group(1)[0] == marker and not fence.group(2):
                segments.append((kind, "\n".join(buffer)))
                buffer = []
                kind = "text"

    if buffer:
        segments.append((kind, "\n".join(buffer)))
    return segments


def strip_decorative(text: str) -> str:
    """Remove enfeites de cor e layout (`<font>`, `<span>`, ...) e entidades como `&apos;`."""
    lines = []
    for line in text.split("\n"):
        if DECORATIVE_TAG_RE.search(line):
            # Só nas linhas que tinham enfeites: &apos; vira ', &amp; vira &, etc.
            line = html.unescape(DECORATIVE_TAG_RE.sub("", line))
        lines.append(line)
    return "\n".join(lines)


def _image_label(alt: str) -> str:
    alt = alt.strip()
    return f"[Image: {alt}]" if alt else ""


def strip_html_text(text: str) -> str:
    """Converte HTML de texto em Markdown simples. Use só fora dos blocos de código."""
    text = HTML_COMMENT_RE.sub("", text)
    text = CODE_TAG_RE.sub(lambda m: f"`{m.group(1)}`", text)
    text = KBD_TAG_RE.sub(lambda m: f"`{m.group(1)}`", text)
    text = ABBR_RE.sub(lambda m: f"{m.group(2)} ({m.group(1)})", text)
    text = STRONG_TAG_RE.sub(lambda m: f"**{m.group(1)}**", text)
    text = LINK_TAG_RE.sub(lambda m: f"[{m.group(2)}]({m.group(1)})", text)
    text = IMG_TAG_RE.sub(
        lambda m: _image_label(
            alt.group(1) if (alt := IMG_ALT_RE.search(m.group(0))) else ""
        ),
        text,
    )
    text = MD_IMAGE_RE.sub(lambda m: _image_label(m.group(1)), text)
    return strip_decorative(text)


def _admonition_label(kind: str, title: str | None) -> str:
    if kind == "tab":
        return f"**{title}**" if title else ""
    label = f"**{kind.capitalize()}**"
    return f"{label}: {title}" if title else label


def strip_site_markup(text: str) -> str:
    """Remove âncoras de títulos e troca os blocos `/// tip` por um rótulo simples."""
    lines = []
    for line in text.split("\n"):
        anchor = HEADING_ANCHOR_RE.match(line)
        if anchor:
            line = anchor.group(1)
        elif ADMONITION_CLOSE_RE.match(line):
            continue
        else:
            opened = ADMONITION_OPEN_RE.match(line)
            if opened:
                label = _admonition_label(opened.group(2), opened.group(3))
                line = f"{opened.group(1)}{label}" if label else ""
        lines.append(line)
    return "\n".join(lines)


def resolve_includes(text: str, docs_src: Path, report: CleanReport) -> str:
    """Troca cada `{* ...docs_src/arquivo.py *}` pelo código real, em um bloco de código."""
    docs_src_root = docs_src.resolve()

    def replace(match: re.Match[str]) -> str:
        raw_path = match.group(1)
        marker = "docs_src/"
        position = raw_path.find(marker)
        if position == -1:
            report.missing.append(raw_path)
            return ""
        relative = raw_path[position + len(marker) :]
        file = (docs_src / relative).resolve()
        # Segurança: nunca ler nada fora da pasta docs_src.
        if not file.is_relative_to(docs_src_root) or not file.is_file():
            report.missing.append(relative)
            return ""
        code = file.read_text(encoding="utf-8").rstrip("\n")
        language = LANGUAGES.get(file.suffix, "text")
        report.resolved += 1
        return f"```{language}\n{code}\n```"

    return INCLUDE_RE.sub(replace, text)


def clean_markdown(text: str, docs_src: Path) -> tuple[str, CleanReport]:
    """Aplica todas as etapas de limpeza e devolve o texto limpo e o relatório."""
    report = CleanReport()
    text = text.replace("\r\n", "\n")

    # A limpeza vem antes de trazer o código real, para não mexer nele.
    parts = []
    for kind, segment in split_segments(text):
        if kind == "text":
            segment = strip_site_markup(strip_html_text(segment))
        elif kind == "console":
            segment = strip_decorative(segment)
        parts.append(segment)
    text = "\n".join(parts)

    text = resolve_includes(text, docs_src, report)
    text = re.sub(r"\n{3,}", "\n\n", text).strip() + "\n"
    return text, report


def extract_title(text: str, fallback: str) -> str:
    """Devolve o primeiro título (`# ...`) do texto, ou o nome do arquivo."""
    for line in text.split("\n"):
        if line.startswith("# "):
            return line[2:].strip()
    return fallback
