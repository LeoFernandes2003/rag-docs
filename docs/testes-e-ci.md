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
pytest -v
ruff check .
```

## Integração contínua

O workflow `.github/workflows/ci.yml` roda em todo push na `main` e em todo pull request: instala as dependências (Python 3.12), roda `ruff check .` (estilo e erros comuns) e `pytest -v`. Os testes da API só rodam no CI, porque dependem do FastAPI instalado.

## Regras de trabalho

- Código gerado por IA só entra na `main` por pull request com testes passando no CI.
- Cada pull request recebe um comentário de revisão declarando que foi feita por IA, porque o projeto é individual.
- Segredos: não há chaves; `.env` está no `.gitignore`.

## Cobertura

A cobertura percentual ainda não foi medida. Será medida e registrada antes da entrega final.
