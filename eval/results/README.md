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

# Reranking (conjunto de desenvolvimento)

Medido em 31/10/2026 com `python -m app.evaluation.retrieval --strategy structure --mode hybrid
--translate --rerank`. A busca híbrida traz 10 candidatos; o `qwen2.5:3b` dá a cada um uma nota
de 0 a 9 ("este trecho responde à pergunta?"); os 5 melhores seguem. Empates mantêm a ordem
original da busca.

| Configuração | Recall@5 (dev, 16 perguntas) | Custo por pergunta |
|---|---|---|
| Híbrida + tradução (sem reranker) | 0,938 (15/16) | uma busca |
| Híbrida + tradução + reranker (10 candidatos) | 0,875 (14/16) | uma busca + 10 chamadas ao modelo (cerca de 45 s a mais neste computador) |

**Resultado negativo.** O reranker não melhorou: perdeu a q021 (o arquivo certo, `request-forms.md`,
continuou entre os 5, mas o modelo preferiu outros pedaços do mesmo arquivo ao pedaço que
contém a resposta) e manteve o erro da q026 (a tradução errada da pergunta nasce antes do
reranker; ele não consegue consertar). A diferença de uma pergunta está dentro do ruído
(16 perguntas), mas o custo de tempo é alto demais para uma interface interativa. Decisão:
**não usar o reranker no sistema final**; o resultado fica registrado como comparação.

Limitações: o Ollama não tem modelo de reranking dedicado, então o modelo de respostas foi usado
como juiz (nota de um modelo de 3 bilhões de parâmetros, sem calibração); um reranker
cross-encoder próprio (por exemplo `bge-reranker-v2-m3`) não foi testado.

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

# Resultados do teste final (conjunto de teste)

Medido em 10/11/2026, **uma única vez**, com o sistema congelado, no sistema do Docker (`docker compose up`, imagem do Ollama fixada por digest), com os comandos:

```bash
cd src
set OLLAMA_URL=http://localhost:11435        # Ollama do Docker (no Linux/macOS: export OLLAMA_URL=...)
python -m app.evaluation.retrieval --strategy structure --mode hybrid --translate --final
python -m app.evaluation.generation --final --label v5
python -m app.evaluation.generation --conferencia ../eval/results/generation-docs-structure-1000-test-v5-conferencia.md
```

Antes do teste, um ensaio no conjunto de desenvolvimento com o mesmo ambiente reproduziu o Recall@5 de 0,938 (15 de 16, erro só na q026), o que indica que o Ollama do Docker se comporta como o usado nas medições anteriores.

| Medida (30 perguntas de teste: 24 com resposta, 6 sem) | Teste | Desenvolvimento (v5) |
|---|---|---|
| Recall@5 da busca (estrutura + híbrida + tradução) | **0,833** (20/24) | 0,938 (15/16) |
| Citação válida (entre as respondidas) | **1,000** | 1,000 |
| Fonte correta (trecho citado cobre a frase-fonte) | **0,792** (19/24) | 0,875 (14/16) |
| Recusa indevida | **0/24** | 0/16 |
| Recusa correta | **6/6** | 4/4 |
| Perguntas sem resposta que o sistema respondeu | **0** | 0 |
| Conferência manual do autor, com resposta | **22/24** | 15/16 |
| Conferência manual do autor, sem resposta | **6/6** | 4/4 |

Erros da busca: q004, q012, q037 e q040. Erros de "fonte correta": q004, q012, q030, q037 e q040. Respostas erradas na conferência do autor: q004 e q012.

Tempo neste computador (CPU, sem GPU): recuperação das 24 perguntas em cerca de 2 minutos; geração das 30 respostas em 12,4 minutos (média de 25 s por pergunta, máximo de 38 s).

## O que os resultados indicam

- Os resultados do teste são um pouco piores que os do desenvolvimento na busca (0,833 contra 0,938) e na fonte (0,792 contra 0,875), como esperado: as configurações foram escolhidas olhando o desenvolvimento.
- O ponto forte se manteve: nenhuma pergunta sem resposta foi respondida (6/6) e nenhuma pergunta com resposta foi recusada (0/24).
- A métrica de fonte é mais rígida que o conteúdo: das 5 respostas com "fonte errada", 3 estavam corretas no conteúdo (q030, q037, q040).

## Limitações

- 24 perguntas com resposta: cada uma vale 4,2 pontos percentuais; só 6 sem resposta (16,7 pontos cada). Diferenças pequenas estão no ruído.
- O conjunto de teste foi usado uma só vez; não foi medida a variação entre execuções.
- A conferência manual foi feita pelo autor, que leu cada resposta e decidiu a marcação por conta própria. Antes de marcar, ele tinha lido uma segunda opinião da IA (registrado em `PROMPTS.md`, entrada 15); a marcação coincidiu com a dela nas duas respostas erradas.
- O conjunto de perguntas aceita uma só fonte por pergunta, mas a documentação repete assuntos em vários arquivos (q040).
- Modelos de 3 bilhões de parâmetros (tradução e respostas) são pequenos; a q004 mostra um erro de interpretação do modelo.

## Casos de falha para a análise

Análise completa, com trechos recuperados e causas, em `evidencias/analise-de-falhas.md`.

- **q004:** busca trouxe a seção vizinha; o modelo inverteu o exemplo (resposta errada).
- **q012:** o arquivo certo veio, mas a frase com os exemplos estava em outro trecho (resposta vaga, errada).
- **q037:** frase-fonte no trecho seguinte ao recuperado (resposta aceitável).
- **q040:** a documentação responde em mais de um arquivo (resposta aceitável).
- **q030:** trecho certo recuperado, mas não citado (resposta correta, citação errada).
