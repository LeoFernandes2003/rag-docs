# Resultados da busca (conjunto de desenvolvimento)

Medido em 27/10/2026 com `python -m app.evaluation.retrieval`, nas **16 perguntas com resposta
do conjunto `dev`** (as de `test` ainda não foram usadas). A métrica é o Recall@5: a busca
acerta quando um dos 5 pedaços devolvidos cobre o trecho-fonte da pergunta, no arquivo certo.
Corpus: FastAPI 0.162.0. Embeddings: `bge-m3`. Tradução: `qwen2.5:3b`. Pedaços de até 1000
caracteres. Cada arquivo `retrieval-*.json` desta pasta guarda os erros de uma execução.

| Divisão do texto | Sentido (dense) | Palavras (BM25) | Híbrida | Palavras + tradução | Híbrida + tradução |
|---|---|---|---|---|---|
| Tamanho fixo (baseline) | 0,812 (13/16) | 0,500 (8/16) | 0,688 (11/16) | 1,000 (16/16) | 0,875 (14/16) |
| Por estrutura | 0,812 (13/16) | 0,312 (5/16) | 0,812 (13/16) | 0,938 (15/16) | 0,938 (15/16) |

## O que os resultados indicam

- A busca por palavras sem tradução vai mal porque as perguntas estão em português e a
  documentação em inglês. Traduzir a pergunta para inglês com o `qwen2.5:3b` antes dessa busca
  resolve a maior parte do problema.
- A busca híbrida (fusão RRF) piora quando uma das listas é ruidosa (sem tradução) e melhora
  quando as duas falam o mesmo idioma.
- A divisão por estrutura (títulos, parágrafos e blocos de código inteiros) não superou a de
  tamanho fixo na busca por sentido (empate em 0,812).

## Limitações (devem constar no trabalho)

- Só 16 perguntas: cada uma vale 6,25 pontos percentuais. Diferenças de uma pergunta estão no ruído.
- Dez configurações foram comparadas no mesmo conjunto; o melhor valor entre elas é otimista.
  O valor oficial virá do conjunto `test`, medido uma só vez no fim (`--final`).
- As perguntas foram escritas a partir de parágrafos do próprio corpus, então reaproveitam
  palavras da documentação. Isso favorece a busca por palavras mais do que perguntas de usuários reais.
- A tradução pelo modelo pequeno às vezes muda o sentido (q026: "resposta temporária" virou
  "response status") e às vezes acrescenta palavras que não estavam na pergunta (q011, q023).
- A métrica exige o pedaço exato com o trecho-fonte; encontrar só o arquivo certo conta como erro.

## Casos de falha para a análise

- **q026** ("Que informações o FastAPI extrai da resposta temporária?"): falha em quase todas as
  configurações. Pergunta vaga fora de contexto e tradução errada.
- **q001** ("O que o FastAPI gera automaticamente com as descrições de toda a sua API?"): vários
  arquivos falam de OpenAPI; falha com busca só por sentido.
- **q033** ("O que mostra, no editor, os benefícios do FastAPI?"): o tema aparece repetido em
  `about`, `features` e `index`; falha na divisão fixa mesmo com tradução.
