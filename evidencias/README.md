# Índice de evidências

Este índice é o roteiro para conferir o trabalho: cada afirmação do artigo (`../docs/pesquisa-abnt.pdf`) aponta para a prova que a sustenta. Todas as provas saíram da execução real do projeto (scripts de `../eval/`, GitHub Actions e a própria aplicação); nenhum número foi editado à mão. A única parte manual é a conferência do conteúdo das respostas, em que o autor leu cada resposta e fez a marcação (antes, leu uma segunda opinião de IA, registrada em `../PROMPTS.md`); os arquivos estão em `../eval/results/`.

Situação em 25/11/2026. O único item pendente (execução do CI na tag `v1.0`, com link e captura) será acrescentado na criação da tag.

## 1. Evidências pedidas no enunciado

| # | Evidência | Onde está | Status |
| --- | --- | --- | --- |
| 1 | Execução gravada (3 a 5 min), subindo do zero com `docker compose up` | `video/execucao-do-zero.mp4` (4 min 39 s, gravado em 23/11/2026; o que foi editado está na seção 4) | pronto |
| 2 | Integração contínua verde na tag `v1.0`, com link e captura | Aba **Actions** do repositório (ruff e pytest com cobertura, Python 3.12). A `main` está verde: `capturas/ci-verde-main.png` (CI nº 49, commit `0d9218a`, 22/11/2026) e `capturas/ci-cobertura-main.png` (log do passo de testes: 99 testes e cobertura de 73%). A captura e o link da tag `v1.0` virão na entrega | parcial |
| 3 | Resultados da avaliação, com o comando que os regera | `../eval/results/` (JSON brutos, arquivos de conferência e `README.md` com as tabelas); comandos passo a passo em `../docs/avaliacao.md` | pronto |
| 4 | Logs de uma execução completa, com data e hora | `logs/execucao-2026-11-22.log` (6 perguntas da sessão de uso de 22/11/2026; descrição na seção 3) | pronto |
| 5 | Capturas de tela (opcional, pelo menos 5 situações, incluindo uma falha tratada) | `capturas/ui-1-...png` a `capturas/ui-6-...png` (6 situações de 22/11/2026, incluindo a falha tratada com o Ollama desligado; descrição na seção 3). As duas capturas de 31/10 (`ui-resposta-2026-10-31.png` e `ui-recusa-2026-10-31.png`) ficam como registro de uma versão anterior | pronto (refazer só se o código mudar antes da `v1.0`) |
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
| Testes automáticos: 99 testes e cobertura de 73% (1356 linhas, 364 sem teste) medidos no CI nº 49 | `capturas/ci-cobertura-main.png`, `../docs/testes-e-ci.md` e aba **Actions** |
| Licenças dos componentes e dos modelos (3.8) | `../README.md` e `../docs/dados-e-modelos.md` |

## 3. Sessão de uso de 22/11/2026 (log e capturas)

Seis perguntas feitas pela interface (http://localhost:8501), uma de cada vez, com o sistema no Docker e a API recém-recriada (`docker compose up -d --force-recreate api`), de modo que o log contém só estas perguntas. O log foi exportado com `docker compose logs -t api > evidencias/logs/execucao-2026-11-22.log`. Os horários do log vêm em UTC (3 horas à frente de Brasília); o relógio do Windows aparece nas capturas.

| # | Situação | Captura | Linhas do log (`logs/execucao-2026-11-22.log`) | Resultado |
| --- | --- | --- | --- | --- |
| 1 | Resposta com fonte (`q002` do teste) | `capturas/ui-1-resposta-opentelemetry.png` | linhas 5 a 8 | respondeu, similaridade 0,704, cita `advanced/opentelemetry.md` |
| 2 | Resposta com fonte (`q017` do teste) | `capturas/ui-2-resposta-httpexception.png` | linhas 9 a 12 | respondeu, similaridade 0,783, cita `tutorial/handling-errors.md` |
| 3 | Recusa de assunto fora da documentação (`q048` do teste) | `capturas/ui-3-recusa-scikit-learn.png` | linhas 13 a 16 | recusou (`modelo_recusou`), similaridade 0,516 |
| 4 | Recusa de assunto sem relação | `capturas/ui-4-recusa-fora-do-assunto.png` | linhas 17 a 20 | recusou (`modelo_recusou`), similaridade 0,406 |
| 5 | Falha tratada: Ollama desligado (`docker compose stop ollama`) | `capturas/ui-5-falha-ollama-desligado.png` | linhas 21 a 23 | a API respondeu 503 com mensagem clara; o sistema não caiu. Na interface, o indicador de carregamento continuou girando depois do erro (detalhe visual da interface naquele momento; corrigido depois, em 22/11/2026, no pull request "Corrige o indicador de carregamento quando a API falha") |
| 6 | Recuperação depois de religar o Ollama | `capturas/ui-6-recuperacao.png` | linhas 24 a 27 | respondeu, similaridade 0,619, cita `advanced/testing-dependencies.md` |

Cada pergunta gera no log, nesta ordem: `pergunta recebida`, `decisão` (respondeu ou modelo_recusou, nota de similaridade, trechos devolvidos e citados, a pergunta traduzida usada na busca por palavras e o tempo), `resposta` e o código HTTP. As respostas das situações 1, 2 e 3 repetem o resultado do teste final (mesma nota de similaridade, mesma fonte). Os tempos desta sessão (de 23 s a 53 s por resposta) variam com a carga do computador; o teste final teve média de 25 s.

## 4. Vídeo da execução do zero

O vídeo `video/execucao-do-zero.mp4` foi gravado em 23/11/2026, com a tela inteira, a partir de uma pasta criada do zip da `main`, depois de apagar os contêineres, a rede e os volumes do teste anterior, subindo tudo com `docker compose up --build`. Mostra: a pasta do projeto, `docker compose down`, `docker compose up --build`, a lista dos serviços no ar, uma pergunta com resposta e fonte, uma pergunta fora da documentação recusada, a falha tratada com o Ollama desligado (mensagem de erro, sem o indicador de carregamento preso), a recuperação depois de religar o Ollama, o log das perguntas e, no final, o pull request nº 21 e o CI verde no GitHub.

O vídeo foi editado depois da gravação (a gravação original tinha 7 min 2 s). Tudo o que foi alterado está declarado aqui:

- A gravação foi pausada durante a construção das imagens e o download dos modelos (cerca de 25 minutos); há uma legenda no ponto do corte.
- Foram cortados um comando digitado errado (`docker compose um`), trechos em que a janela do programa de gravação aparecia e um comando de logs que não chegou a rodar na primeira tentativa.
- Duas esperas da resposta foram aceleradas (6 vezes e 9 vezes), com legenda na tela.
- O endereço público do computador, que o Streamlit imprime na linha `External URL`, foi coberto com uma tarja preta (regra do enunciado: nenhum dado pessoal em vídeos). Conferi o arquivo final quadro a quadro com leitura de texto (OCR) e o endereço não aparece.

O sistema, os resultados e as respostas não foram alterados: só o tempo de espera e o que ficou fora da imagem.

## 5. Como reproduzir (conferência ao vivo)

Os comandos completos estão em `../docs/avaliacao.md`. Em resumo, com `docker compose up -d` rodando:

```bash
curl http://localhost:8000/health                       # a API está de pé
cd src
python -m app.evaluation.check_questions --final        # confere as 50 perguntas
python -m app.evaluation.retrieval --strategy structure --mode hybrid --translate --final   # Recall@5 do teste
```

A interface fica em http://localhost:8501. A geração das 30 respostas leva cerca de 12 minutos em CPU.

## 6. O que falta

1. Execução verde do CI na tag `v1.0`, com link e captura (evidência 2).
