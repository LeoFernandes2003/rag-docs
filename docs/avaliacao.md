# 6. Guia de avaliação

Como reproduzir os experimentos. Os comandos rodam a partir da pasta `src`, com Qdrant e Ollama ligados e o corpus baixado (basta ter rodado `docker compose up` uma vez, ou `python -m app.setup`).

## Regras do protocolo

1. As 50 perguntas foram escritas antes de ajustar o sistema.
2. Ajustes usam só as perguntas `dev` (16 com resposta e 4 sem).
3. O conjunto `test` (24 com resposta e 6 sem) é medido **uma única vez**, no fim, com `--final`.
4. O baseline é a busca densa com trechos de tamanho fixo.
5. A conferência manual da qualidade das respostas é feita pelo autor, nunca pela IA.

## Passo 0. Conferir as perguntas

```bash
python -m app.evaluation.check_questions --final
```

Confirma que cada trecho-fonte existe no corpus, que os termos proibidos não existem e que os totais batem.

## Passo 1. Recuperação (Recall@5)

Indexar cada divisão do texto (uma vez):

```bash
python -m app.rag.index --strategy fixed --size 1000 --recreate
python -m app.rag.index --strategy structure --size 1000 --recreate
```

Medir cada combinação (exemplos):

```bash
python -m app.evaluation.retrieval --strategy fixed --mode dense        # baseline
python -m app.evaluation.retrieval --strategy structure --mode hybrid --translate
python -m app.evaluation.retrieval --strategy structure --mode hybrid --translate --rerank
```

`--mode` aceita `dense`, `bm25` e `hybrid`. Cada execução imprime o Recall@5 e grava o JSON com os erros em `eval/results/`. A tabela comparativa está em `eval/results/README.md`.

## Passo 2. Geração, citação e recusa

```bash
python -m app.evaluation.generation --label v5
```

Mede, nas perguntas de desenvolvimento: citação válida, fonte certa, recusa indevida, recusa correta e alucinação (resposta a uma pergunta sem resposta). Grava `generation-...-dev-v5.json` e um arquivo `...-conferencia.md`.

## Passo 3. Conferência manual

Abra o arquivo `...-conferencia.md`, leia cada resposta e marque `[x]` nas corretas (a marcação é do autor). Depois:

```bash
python -m app.evaluation.generation --conferencia caminho/do/arquivo-conferencia.md
```

Mostra a taxa de acerto conferida.

## Passo 4. Avaliação final (uma vez)

```bash
python -m app.evaluation.retrieval --strategy structure --mode hybrid --translate --final
python -m app.evaluation.generation --final --label v5
```

Os números do conjunto de teste são os oficiais.

## Métricas

| Métrica | Como é calculada |
| --- | --- |
| Recall@5 | A busca acerta quando um dos 5 trechos devolvidos cobre o trecho-fonte da pergunta, no arquivo certo |
| Citação válida | A resposta cita ao menos um trecho que existe |
| Fonte certa | Entre os trechos citados está o arquivo-fonte esperado |
| Recusa indevida | Recusou uma pergunta que tinha resposta |
| Recusa correta | Recusou uma pergunta sem resposta |
| Alucinação | Respondeu uma pergunta sem resposta |

## Resultados já medidos (desenvolvimento)

Estão em `eval/results/README.md`. A comparação de recuperação tem 10 combinações; a de geração compara as versões v2 a v5 do prompt (v5: recusa indevida 0/16, recusa correta 4/4, fonte certa 14/16, citação válida 1,000).
