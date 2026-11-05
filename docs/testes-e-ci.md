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

O valor da execução do CI na tag `v1.0` será copiado para `evidencias/` como parte da evidência de integração contínua. Partes que dependem de Ollama e Qdrant reais (como `ollama.py` e `qdrant.py`) são cobertas só por testes com serviços simulados, então a cobertura delas é menor.
