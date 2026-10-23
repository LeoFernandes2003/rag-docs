import json

from app.ingest.clean import clean_markdown, extract_title
from app.ingest.prepare import main

CODIGO = "from fastapi import FastAPI\n\napp = FastAPI()\n"


def criar_docs_src(base):
    pasta = base / "docs_src" / "first_steps"
    pasta.mkdir(parents=True)
    (pasta / "tutorial001_py310.py").write_text(CODIGO, encoding="utf-8")
    return base / "docs_src"


def test_include_vira_bloco_de_codigo(tmp_path):
    docs_src = criar_docs_src(tmp_path)
    texto = "Copie para `main.py`:\n\n{* ../../docs_src/first_steps/tutorial001_py310.py *}\n\nFim"
    limpo, relatorio = clean_markdown(texto, docs_src)
    assert "```python\nfrom fastapi import FastAPI" in limpo
    assert "{*" not in limpo
    assert relatorio.resolved == 1
    assert relatorio.missing == []


def test_include_com_opcoes_de_destaque(tmp_path):
    docs_src = criar_docs_src(tmp_path)
    texto = "{* ../../docs_src/first_steps/tutorial001_py310.py hl[3] *}"
    limpo, relatorio = clean_markdown(texto, docs_src)
    assert "app = FastAPI()" in limpo
    assert relatorio.resolved == 1


def test_include_de_arquivo_inexistente_e_registrado(tmp_path):
    docs_src = criar_docs_src(tmp_path)
    limpo, relatorio = clean_markdown("{* ../../docs_src/nao/existe.py *}", docs_src)
    assert "{*" not in limpo
    assert relatorio.resolved == 0
    assert relatorio.missing == ["nao/existe.py"]


def test_include_nao_le_arquivos_fora_de_docs_src(tmp_path):
    docs_src = criar_docs_src(tmp_path)
    (tmp_path / "segredo.txt").write_text("SEGREDO", encoding="utf-8")
    limpo, relatorio = clean_markdown("{* ../../docs_src/../segredo.txt *}", docs_src)
    assert "SEGREDO" not in limpo
    assert relatorio.resolved == 0
    assert len(relatorio.missing) == 1


def test_remove_ancora_do_titulo(tmp_path):
    limpo, _ = clean_markdown("# First Steps { #first-steps }\n", tmp_path)
    assert limpo == "# First Steps\n"


def test_remove_enfeites_html_do_terminal(tmp_path):
    texto = (
        '<div class="termy">\n\n```console\n'
        "$ <font color=\"#4E9A06\">uv run fastapi</font> dev\n\n"
        '  <span style="background-color:#009485"><font color="#D3D7CF"> FastAPI </font></span>'
        "  Starting development server\n"
        '<b>[</b><font color="#4E9A06">&apos;/home/user/code/app&apos;</font><b>]</b>\n'
        "```\n\n</div>\n"
    )
    limpo, _ = clean_markdown(texto, tmp_path)
    assert "<font" not in limpo
    assert "<span" not in limpo
    assert "<div" not in limpo
    assert "&apos;" not in limpo
    assert "$ uv run fastapi dev" in limpo
    assert "['/home/user/code/app']" in limpo


def test_dica_vira_rotulo_simples(tmp_path):
    texto = "/// tip\n\nUse o VS Code.\n\n///\n\n/// warning | Cuidado\n\nNão faça isso.\n\n///\n"
    limpo, _ = clean_markdown(texto, tmp_path)
    assert "**Tip**" in limpo
    assert "**Warning**: Cuidado" in limpo
    assert "Use o VS Code." in limpo
    assert "///" not in limpo


def test_abbr_mantem_a_explicacao(tmp_path):
    limpo, _ = clean_markdown('Usa <abbr title="Interface de Programação">API</abbr>.\n', tmp_path)
    assert limpo == "Usa API (Interface de Programação).\n"


def test_dfn_com_code_mantem_a_explicacao(tmp_path):
    texto = '* using a <dfn title="an HTTP GET method"><code>get</code> operation</dfn>\n'
    limpo, _ = clean_markdown(texto, tmp_path)
    assert limpo == "* using a `get` operation (an HTTP GET method)\n"


def test_linha_em_branco_depois_do_include_e_preservada(tmp_path):
    docs_src = criar_docs_src(tmp_path)
    texto = "{* ../../docs_src/first_steps/tutorial001_py310.py *}\n\nCopy that to a file.\n"
    limpo, _ = clean_markdown(texto, docs_src)
    assert "```\n\nCopy that to a file." in limpo


def test_html_dentro_de_bloco_de_codigo_e_preservado(tmp_path):
    texto = (
        "```html\n<form><button>Ok</button></form>\n<div class=\"x\">a</div>\n"
        '<a href="/">home</a> <img src="a.png" alt="logo">\n```\n'
    )
    limpo, _ = clean_markdown(texto, tmp_path)
    assert limpo == texto


def test_html_de_texto_vira_markdown(tmp_path):
    texto = (
        "Aperte <kbd>Ctrl+C</kbd> para <strong>sair</strong>. "
        'Veja <a href="https://x.dev" target="_blank">o site</a>.\n'
    )
    limpo, _ = clean_markdown(texto, tmp_path)
    assert limpo == "Aperte `Ctrl+C` para **sair**. Veja [o site](https://x.dev).\n"


def test_imagens_viram_rotulo_ou_somem(tmp_path):
    texto = (
        '<img src="a.png" alt="Swagger UI">\n\n'
        '<img src="b.png">\n\n'
        "![ReDoc](https://x.dev/redoc.png)\n"
    )
    limpo, _ = clean_markdown(texto, tmp_path)
    assert limpo == "[Image: Swagger UI]\n\n[Image: ReDoc]\n"


def test_dica_com_espacos_na_frente_e_removida(tmp_path):
    texto = "1. Passo\n\n    /// note\n\n    Texto da nota.\n\n    ///\n\n2. Outro\n"
    limpo, _ = clean_markdown(texto, tmp_path)
    assert "    **Note**" in limpo
    assert "    Texto da nota." in limpo
    assert "///" not in limpo


def test_urls_e_dicionarios_com_barras_e_chaves_nao_sao_alterados(tmp_path):
    texto = 'sqlite_url = f"sqlite:///{sqlite_file_name}"\nnovo = {**antigo, "k": 1}\n'
    limpo, _ = clean_markdown(texto, tmp_path)
    assert limpo == texto


def test_codigo_com_colchetes_e_sinais_nao_e_alterado(tmp_path):
    texto = "```python\nitems: list[int] = []\nif a < b and b > c:\n    pass\n```\n"
    limpo, _ = clean_markdown(texto, tmp_path)
    assert limpo == texto


def test_extract_title():
    assert extract_title("texto\n# Primeiros Passos\n", "x") == "Primeiros Passos"
    assert extract_title("sem titulo", "arquivo") == "arquivo"


def test_prepare_filtra_pastas_e_gera_manifest(tmp_path):
    docs = tmp_path / "docs"
    (docs / "tutorial").mkdir(parents=True)
    (docs / "reference").mkdir()
    (docs / "tutorial" / "primeiro.md").write_text("# Primeiro\n\nTexto.\n", encoding="utf-8")
    (docs / "reference" / "fastapi.md").write_text("::: fastapi.FastAPI\n", encoding="utf-8")
    (docs / "release-notes.md").write_text("# Release Notes\n", encoding="utf-8")
    docs_src = criar_docs_src(tmp_path)
    saida = tmp_path / "saida"

    codigo = main(["--docs", str(docs), "--docs-src", str(docs_src), "--out", str(saida)])

    assert codigo == 0
    assert (saida / "tutorial" / "primeiro.md").is_file()
    assert not (saida / "reference").exists()
    assert not (saida / "release-notes.md").exists()
    manifesto = json.loads((saida / "manifest.json").read_text(encoding="utf-8"))
    assert manifesto["total_files"] == 1
    assert manifesto["files"][0]["source"] == "tutorial/primeiro.md"
    assert manifesto["files"][0]["title"] == "Primeiro"


def test_prepare_avisa_quando_a_pasta_nao_existe(tmp_path, capsys):
    codigo = main(["--docs", str(tmp_path / "nada"), "--docs-src", str(tmp_path)])
    assert codigo == 1
    assert "não existe" in capsys.readouterr().out
