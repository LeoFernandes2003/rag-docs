# Índice de evidências

Este índice é o roteiro para conferir o trabalho: cada afirmação do artigo (`../docs/pesquisa-abnt.pdf`) aponta para a prova que a sustenta. Todas as provas saíram da execução real do projeto (scripts de `../eval/`, GitHub Actions e a própria aplicação); nenhum número foi editado à mão. A única parte manual é a conferência do conteúdo das respostas, em que o autor leu cada resposta e fez a marcação (antes, leu uma segunda opinião de IA, registrada em `../PROMPTS.md`); os arquivos estão em `../eval/results/`.

Situação em 20/11/2026 (Marco 4). Os itens marcados como pendentes serão feitos antes da entrega final, com o sistema na tag `v1.0`.

## 1. Evidências pedidas no enunciado

| # | Evidência | Onde está | Status |
| --- | --- | --- | --- |
| 1 | Execução gravada (3 a 5 min), subindo do zero com `docker compose up` | | pendente (será gravada na versão `v1.0`) |
| 2 | Integração contínua verde na tag `v1.0`, com link e captura | Aba **Actions** do repositório (ruff e pytest com cobertura, Python 3.12). Hoje a `main` está verde; a captura e o link da tag `v1.0` virão na entrega | parcial |
| 3 | Resultados da avaliação, com o comando que os regera | `../eval/results/` (JSON brutos, arquivos de conferência e `README.md` com as tabelas); comandos passo a passo em `../docs/avaliacao.md` | pronto |
| 4 | Logs de uma execução completa, com data e hora | | pendente |
| 5 | Capturas de tela (opcional, pelo menos 5 situações, incluindo uma falha tratada) | `capturas/ui-resposta-2026-10-31.png` e `capturas/ui-recusa-2026-10-31.png` (uma resposta com fontes e uma recusa de pergunta sem resposta) | parcial (2 de 5; falta uma falha tratada, como a mensagem de erro com o Ollama desligado; refazer na `v1.0`) |
| 6 | Casos de falha (mínimo 3) com análise da causa | `analise-de-falhas.md` (5 casos do teste final) e a seção "Casos de falha para a análise" de `../eval/results/README.md` | pronto |
| 7 | Histórico do Git | Aba **Pull requests** (todos os PRs, com CI e comentário de revisão) e aba **Commits**. Trabalho individual: não há commits de outros integrantes. A revisão de cada PR foi feita por IA (Claude), declarada no comentário de cada um | pronto |
| 8 | Este índice | `evidencias/README.md` | pronto |

## 2. Afirmações do artigo e suas provas

| Afirmação (seção do artigo) | Prova |
| --- | --- |
| Corpus: documentação do FastAPI 0.162.0; 121 arquivos, 452 exemplos de código inseridos, 1 não encontrado (3.2) | `../docs/corpus.md` |
| Arquitetura e componentes: Qdrant, Ollama, `bge-m3`, `qwen2.5:3b`, API e interface (3.1) | `../docs/arquitetura.md`, `../docker-compose.yml` |
| Divisão por estrutura gera 1626 trechos de até 1000 caracteres (3.3) | `../docs/decisoes.md` (ADR 1); o comando `python -m app.rag.index --strategy structure --size 1000 --recreate` mostra o total de pedaços |
| 50 perguntas escritas antes de ajustar o sistema: 20 de desenvolvimento (16 com resposta, 4 sem) e 30 de teste (24 com resposta, 6 sem) (3.6) | `../eval/questions.jsonl`; `python -m app.evaluation.check_questions --final` confere trechos-fonte e totais |
| Definição das métricas: Recall@5, citação válida, fonte certa, recusas (3.7) | `../docs/avaliacao.md` (seção Métricas) e código em `../src/app/evaluation/` |
| Recall@5 das dez combinações no desenvolvimento, incluindo o baseline (4.1, Tabela 1 e Figura 2) | `../eval/results/README.md` e os dez arquivos `retrieval-*-dev-top5.json` |
| Reranker testado e não adotado: 0,875 contra 0,938, cerca de 45 s a mais por pergunta (4.2, Tabela 2) | `../eval/results/README.md` (seção Reranking), `retrieval-docs-structure-1000-hybrid-traducao-rerank10-dev-top5.json`, `../docs/decisoes.md` (ADR 5) |
| Versões v2 a v5 do prompt e seus efeitos (4.3, Tabela 3 e Figura 3) | `../eval/results/README.md`, arquivos `generation-*-dev-v*.json` e `*-conferencia.md`, `../PROMPTS.md` |
| Resultado no teste final, medido uma vez em 10/11/2026 (4.4, Tabela 4) | `../eval/results/README.md` (seção Teste final), `generation-docs-structure-1000-test-v5.json`, `generation-docs-structure-1000-test-v5-conferencia.md`, `retrieval-docs-structure-1000-hybrid-traducao-test-top5.json` |
| Baseline no teste, medido em 16/11/2026: 0,875 contra 0,833, sistema não trocado (4.4, Tabela 5) | `retrieval-docs-fixed-1000-0-dense-test-top5.json`, `../eval/results/README.md` (seção Baseline), `../docs/decisoes.md` (ADR 6) |
| Exemplos de respostas q002, q017 e q048 (4.5, Quadro 3) | Campo `answers` de `generation-docs-structure-1000-test-v5.json` (perguntas q002, q017 e q048) |
| Análise das falhas q004, q012, q030, q037 e q040 (4.6, Quadro 4) | `analise-de-falhas.md` |
| Tempo de resposta em CPU: média de 25 s, máximo de 38 s (4.7) | Campo `seconds` de cada resposta em `generation-docs-structure-1000-test-v5.json` |
| Limitações dos resultados (4.9) | `../docs/seguranca-e-limitacoes.md` e `../eval/results/README.md` |
| Uso de IA no desenvolvimento | `../PROMPTS.md` |
| Testes automáticos: 97 testes, cobertura de 73% (CI nº 32) | `../docs/testes-e-ci.md` e aba **Actions** |
| Licenças dos componentes e dos modelos (3.8) | `../README.md` e `../docs/dados-e-modelos.md` |

## 3. Como reproduzir (conferência ao vivo)

Os comandos completos estão em `../docs/avaliacao.md`. Em resumo, com `docker compose up -d` rodando:

```bash
curl http://localhost:8000/health                       # a API está de pé
cd src
python -m app.evaluation.check_questions --final        # confere as 50 perguntas
python -m app.evaluation.retrieval --strategy structure --mode hybrid --translate --final   # Recall@5 do teste
```

A interface fica em http://localhost:8501. A geração das 30 respostas leva cerca de 12 minutos em CPU.

## 4. O que falta

1. Vídeo de 3 a 5 minutos (evidência 1).
2. Execução verde do CI na tag `v1.0`, com link e captura (evidência 2).
3. Logs com data e hora de uma execução completa (evidência 4).
4. Mais três capturas de tela de situações diferentes e refazer as duas atuais na `v1.0` (evidência 5).
