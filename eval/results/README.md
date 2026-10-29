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

# Resultados da resposta com citação e recusa (conjunto de desenvolvimento)

Medido em 29/10/2026 com `python -m app.evaluation.generation` nas 20 perguntas `dev` (16 com
resposta e 4 sem). Busca: divisão por estrutura + híbrida + tradução. Modelo de respostas:
`qwen2.5:3b`. Cada versão do prompt guardou seus arquivos `generation-*-dev-<versão>.json`
(a v1 e a v2 só têm o arquivo de conferência `v2`; a v1 foi verificada à mão em 2 perguntas).

| Versão do prompt | Recusa indevida | Recusa correta | Fonte correta | Problema observado |
|---|---|---|---|---|
| v2 (com exemplo de formato) | 1/16 | 3/4 | 13/16 | O modelo copiou o exemplo ("Use o parâmetro X para fazer Y") em 3 respostas; recusas com grafia diferente ("NÃO ENCONTROU") não eram reconhecidas |
| v3 (frases curtas, suas palavras) | 6/16 | 4/4 | 8/16 | Modelo "medroso": recusou perguntas que antes respondia |
| v4 (citação no fim de cada frase) | 7/16 | 4/4 | 7/16 | 7 respostas só com "[1]", sem texto |
| **v5 (linha separada "Fontes:")** | **0/16** | **4/4** | **14/16** | Escolhida |

Conferência manual da v5 (feita pelo aluno, lendo cada resposta ao lado da esperada):
**15 de 16** respostas com resposta corretas e **4 de 4** recusas corretas.

## Limitações

- Só 4 perguntas sem resposta: cada uma vale 25 pontos percentuais.
- O prompt foi ajustado olhando estas mesmas 20 perguntas; o valor oficial virá do conjunto
  `test`, medido uma vez (`--final`).
- A métrica "fonte correta" é rígida: q018 e q026 estavam corretas no texto, mas o trecho citado
  não era o exato trecho-fonte (a mesma informação aparece em outro pedaço).
- A única resposta errada na conferência (q033) lista benefícios gerais do FastAPI em vez do que
  o editor mostra.
- O modelo pequeno às vezes escreve frases desajeitadas (q023 embaralha nomes de exemplo) e a
  q028 é longa e cita um nome antigo (`schema_extra`).

## Casos de falha para a análise

- **q033:** pergunta sobre benefícios no editor; o assistente respondeu com uma lista geral
  (a documentação repete o tema em vários arquivos).
- **q026:** a resposta está certa, mas o pedaço certo só entra na busca por sorte; a pergunta
  é vaga fora de contexto.
- **v2, q001/q011/q033:** alucinação por cópia do exemplo do prompt, corrigida removendo o
  exemplo (v3 em diante).
