# 7. Testes e integração contínua

## O que é testado

Os testes ficam em `tests/` e rodam sem Ollama nem Qdrant (usam dados e serviços simulados), por isso são rápidos e rodam no CI.

| Arquivo | Cobre |
| --- | --- |
| `test_clean.py` | Limpeza do corpus (HTML, código, avisos, âncoras) |
| `test_rag.py` | Divisão em trechos, BM25, fusão RRF, busca |
| `test_pipeline.py` | Prompt, citações, recusa (variações), resposta vazia, nova tentativa, reranker, preparação automática, download do corpus |
| `test_evaluation.py` | Perguntas, Recall@k e métricas da avaliação |
| `test_health.py` | Endereços `/health`, `/config` e `/ask` da API |

## Como rodar

```bash
pip install -r requirements-dev.txt -r requirements-ui.txt
pytest -v --cov=src/app --cov-report=term-missing
ruff check .
```

## Integração contínua

O workflow `.github/workflows/ci.yml` roda em todo push na `main` e em todo pull request: instala as dependências (Python 3.12), roda `ruff check .` (estilo e erros comuns) e `pytest -v`. Os testes da API só rodam no CI, porque dependem do FastAPI instalado. O CI também mede a cobertura (veja abaixo).

## Regras de trabalho

- Código gerado por IA só entra na `main` por pull request com testes passando no CI.
- Cada pull request recebe um comentário de revisão declarando que foi feita por IA, porque o projeto é individual.
- Segredos: não há chaves; `.env` está no `.gitignore`.

## Cobertura

A cobertura é medida com `pytest-cov` e impressa no final do log de cada execução do CI (passo "Testes (pytest) com cobertura", linha `TOTAL`, com as linhas não cobertas de cada arquivo). Para ver no seu computador:

```bash
pytest --cov=src/app --cov-report=term-missing
```

Resultado medido no CI em 05/11/2026 (CI #32, `main`, Python 3.12): **97 testes passaram, cobertura total de 73%** (1341 linhas de código, 358 sem teste).

Onde a cobertura é alta: `chunking.py`, `bm25.py`, `pipeline.py`, `retrieve.py`, `translate.py`, `ollama.py` e `config.py` (100%), `qdrant.py` (97%) e `clean.py` (98%). Esses arquivos são a lógica central do RAG.

Onde é baixa, e por quê:

| Arquivo | Cobertura | Motivo |
| --- | --- | --- |
| `ui.py` (interface Streamlit) | 0% | Testada à mão, com as capturas de tela do manual; não há teste automático da interface. |
| `ask.py`, `search.py` (linhas de comando) | 34% e 33% | Código de terminal que chama Ollama e Qdrant reais. |
| `evaluation/retrieval.py`, `evaluation/generation.py` | 36% e 45% | Scripts de avaliação que dependem dos serviços reais; foram executados à mão e seus resultados estão em `eval/results/`. |
| `rag/index.py`, `setup.py`, `rag/http.py` | 45%, 59%, 52% | Indexação e preparação automática dependem de Qdrant e Ollama rodando. |

Esse número será copiado para `evidencias/` (captura da linha `TOTAL`) junto com a execução do CI da tag `v1.0`. Ele mostra o que os testes automáticos cobrem, não a qualidade das respostas; essa é medida em `docs/avaliacao.md`.
