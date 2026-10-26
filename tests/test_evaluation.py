import json
from collections import Counter

from app.evaluation.check_questions import (
    Corpus,
    check_final_totals,
    count_items,
    load_questions,
    validate,
)
from app.evaluation.check_questions import (
    main as check_main,
)
from app.evaluation.sample_candidates import (
    collect_paragraphs,
    is_eligible,
    sample_candidates,
)
from app.evaluation.sample_candidates import (
    main as sample_main,
)

PARAGRAFO_BOM = (
    "FastAPI is a modern web framework for building APIs with Python. It uses standard "
    "type hints to validate data and to generate documentation automatically for you."
)
PARAGRAFO_BOM_2 = (
    "A path operation decorator tells FastAPI that the function below it handles requests "
    "sent to a given path using a given HTTP method, such as GET or POST in this case."
)


def criar_corpus(base):
    corpus = base / "corpus"
    (corpus / "tutorial").mkdir(parents=True)
    (corpus / "tutorial" / "a.md").write_text(
        f"# A\n\n{PARAGRAFO_BOM}\n\nCurto.\n\n```python\n{PARAGRAFO_BOM_2}\n```\n", encoding="utf-8"
    )
    (corpus / "tutorial" / "b.md").write_text(f"# B\n\n{PARAGRAFO_BOM_2}\n", encoding="utf-8")
    (corpus / "c.md").write_text("# C\n\nSó um texto curto.\n", encoding="utf-8")
    return corpus


def escrever_perguntas(base, itens):
    caminho = base / "questions.jsonl"
    caminho.write_text("\n".join(json.dumps(i) for i in itens) + "\n", encoding="utf-8")
    return caminho


def pergunta_ok(**mudancas):
    item = {
        "id": "q001",
        "split": "dev",
        "question": "O que o FastAPI valida?",
        "answerable": True,
        "expected_answer": "Dados, usando type hints.",
        "source_file": "tutorial/a.md",
        "source_span": "uses standard type hints to validate data",
    }
    item.update(mudancas)
    return item


# --- sorteio de passagens ---


def test_paragrafo_elegivel_e_filtros():
    assert is_eligible(PARAGRAFO_BOM)
    assert not is_eligible("Curto demais.")
    assert not is_eligible("# " + PARAGRAFO_BOM)
    assert not is_eligible("| " + PARAGRAFO_BOM)
    assert not is_eligible("* " + PARAGRAFO_BOM)
    assert not is_eligible("{" * 200 + ".")


def test_coleta_ignora_codigo_e_arquivos_sem_paragrafo_elegivel(tmp_path):
    paragrafos = collect_paragraphs(criar_corpus(tmp_path))
    assert set(paragrafos) == {"tutorial/a.md", "tutorial/b.md"}
    assert paragrafos["tutorial/a.md"] == [PARAGRAFO_BOM]


def test_sorteio_e_reproduzivel_e_usa_um_arquivo_por_vez(tmp_path):
    paragrafos = collect_paragraphs(criar_corpus(tmp_path))
    primeiro = sample_candidates(paragrafos, n=5, seed=42)
    segundo = sample_candidates(paragrafos, n=5, seed=42)
    assert primeiro == segundo
    assert len(primeiro) == 2
    assert len({c["source_file"] for c in primeiro}) == 2
    assert [c["id"] for c in primeiro] == ["C01", "C02"]


def test_sample_main_gera_markdown_e_json(tmp_path):
    corpus = criar_corpus(tmp_path)
    saida = tmp_path / "eval"
    codigo = sample_main(["--corpus", str(corpus), "--out-dir", str(saida), "--n", "2"])
    assert codigo == 0
    assert PARAGRAFO_BOM in (saida / "candidates.md").read_text(encoding="utf-8")
    dados = json.loads((saida / "candidates.json").read_text(encoding="utf-8"))
    assert len(dados) == 2


def test_sample_main_avisa_quando_o_corpus_nao_existe(tmp_path, capsys):
    assert sample_main(["--corpus", str(tmp_path / "nada")]) == 1
    assert "não existe" in capsys.readouterr().out


# --- conferência das perguntas ---


def test_pergunta_correta_passa(tmp_path):
    corpus = Corpus(criar_corpus(tmp_path))
    assert validate([pergunta_ok()], corpus) == []


def test_trecho_com_quebras_de_linha_diferentes_ainda_e_encontrado(tmp_path):
    corpus = Corpus(criar_corpus(tmp_path))
    item = pergunta_ok(source_span="uses standard\ntype   hints")
    assert validate([item], corpus) == []


def test_trecho_inexistente_e_arquivo_inexistente_dao_erro(tmp_path):
    corpus = Corpus(criar_corpus(tmp_path))
    erros = validate([pergunta_ok(source_span="texto que não existe")], corpus)
    assert any("não foi encontrado" in e for e in erros)
    erros = validate([pergunta_ok(source_file="tutorial/zzz.md")], corpus)
    assert any("não existe no corpus" in e for e in erros)


def test_source_file_nao_pode_sair_da_pasta_do_corpus(tmp_path):
    corpus = Corpus(criar_corpus(tmp_path))
    (tmp_path / "segredo.md").write_text("uses standard type hints to validate data", "utf-8")
    erros = validate([pergunta_ok(source_file="../segredo.md")], corpus)
    assert any("não existe no corpus" in e for e in erros)


def test_campos_obrigatorios_split_e_ids_repetidos(tmp_path):
    corpus = Corpus(criar_corpus(tmp_path))
    assert any("falta o campo" in e for e in validate([{"id": "q9"}], corpus))
    assert any("'split'" in e for e in validate([pergunta_ok(split="treino")], corpus))
    erros = validate([pergunta_ok(), pergunta_ok()], corpus)
    assert any("id repetido" in e for e in erros)


def test_pergunta_sem_resposta_exige_termos_ausentes_do_corpus(tmp_path):
    corpus = Corpus(criar_corpus(tmp_path))
    boa = {"id": "q041", "split": "test", "question": "Como usar Celery?", "answerable": False}
    assert any("forbidden_terms" in e for e in validate([boa], corpus))
    assert validate([{**boa, "forbidden_terms": ["celery"]}], corpus) == []
    erros = validate([{**boa, "forbidden_terms": ["FASTAPI"]}], corpus)
    assert any("aparece no corpus" in e for e in erros)


def test_totais_finais(tmp_path):
    itens = [pergunta_ok(id=f"q{i}") for i in range(3)]
    erros = check_final_totals(count_items(itens))
    assert len(erros) == 4
    perfeito = Counter(answerable=40, unanswerable=10, dev=20, test=30)
    assert check_final_totals(perfeito) == []


def test_load_questions_aponta_json_invalido(tmp_path):
    caminho = tmp_path / "q.jsonl"
    caminho.write_text('{"id": "q1"}\n{quebrado\n\n[1, 2]\n', encoding="utf-8")
    itens, erros = load_questions(caminho)
    assert len(itens) == 1
    assert len(erros) == 2


def test_check_main_de_ponta_a_ponta(tmp_path, capsys):
    corpus = criar_corpus(tmp_path)
    caminho = escrever_perguntas(tmp_path, [pergunta_ok()])
    assert check_main(["--questions", str(caminho), "--corpus", str(corpus)]) == 0
    assert "Tudo certo." in capsys.readouterr().out
    assert check_main(["--questions", str(caminho), "--corpus", str(corpus), "--final"]) == 1
    assert "esperado 40" in capsys.readouterr().out
