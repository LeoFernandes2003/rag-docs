# Análise de falhas do teste final (10/11/2026)

Conjunto de teste: 30 perguntas (24 com resposta e 6 sem), medido uma única vez, no sistema do Docker (Ollama fixado por digest). Arquivos de origem: `eval/results/retrieval-docs-structure-1000-hybrid-traducao-test-top5.json`, `eval/results/generation-docs-structure-1000-test-v5.json` e `eval/results/generation-docs-structure-1000-test-v5-conferencia.md` (marcado pelo autor).

## Resumo

| Medida | Resultado |
| --- | --- |
| Recall@5 da busca (24 com resposta) | 0,833 (20 de 24) |
| Fonte correta na resposta (24 com resposta) | 0,792 (19 de 24) |
| Citação válida (entre as respondidas) | 1,000 |
| Recusa indevida | 0 de 24 |
| Recusa correta | 6 de 6 |
| Conferência manual do autor (conteúdo) | 22 de 24 com resposta; 6 de 6 sem resposta |

A métrica "fonte correta" é mais rígida que a conferência de conteúdo: ela só aceita a resposta se um dos trechos citados cobre a frase exata marcada como fonte (arquivo e posição). Por isso há 5 casos de "fonte errada", mas só 2 respostas erradas no conteúdo.

## Os cinco casos

| Caso | Onde falhou | Conteúdo da resposta (conferência do autor) |
| --- | --- | --- |
| q004 | Modelo (com a busca trazendo a seção vizinha) | Errada |
| q012 | Busca (frase esperada em outro trecho do arquivo) | Errada |
| q037 | Busca (frase esperada no trecho seguinte) | Correta |
| q040 | Pergunta com mais de uma fonte válida | Correta |
| q030 | Citação (trecho certo recuperado, mas não citado) | Correta |

Resumo por causa: 3 falhas de busca (q012, q037, q040), 1 de modelo (q004) e 1 de citação (q030).

### q004: "Como o FastAPI distingue parâmetros de caminho de parâmetros de consulta?"

- **Esperado:** ele percebe que `item_id` é parâmetro de caminho e que `q`, que não está no caminho, é parâmetro de consulta. Frase-fonte em `tutorial/query-params.md`.
- **Busca:** o arquivo certo veio em 1º e 2º lugar, mas nenhum dos trechos cobre a frase-fonte. O 1º trecho é a seção "Multiple path and query parameters", vizinha da esperada.
- **Resposta:** diz que, em `/users/{user_id}/items/{item_id}`, `user_id` é de caminho e `item_id` é de consulta. Isso está errado: os dois estão no caminho.
- **Causa:** o modelo `qwen2.5:3b` interpretou mal o exemplo do trecho recuperado (provável, pelo conteúdo da resposta). É a única falha clara de conteúdo causada pelo modelo, e não pela busca.

### q012: "Para que tipos de dados o streaming de JSON Lines pode ser usado?"

- **Esperado:** transmitir dados de um serviço de LLM de IA, logs, telemetria ou outros dados estruturados em itens JSON. Frase-fonte em `tutorial/stream-json-lines.md`.
- **Busca:** o arquivo certo veio em 4º e 5º lugar (trechos 0 a 986 e 988 a 1855), mas a frase com os exemplos não está em nenhum dos dois; ela fica mais adiante no arquivo. Os três primeiros resultados eram de outros assuntos (`custom-response.md`, `server-sent-events.md`, `stream-data.md`).
- **Resposta:** vaga ("dados estruturados como JSON"), sem os exemplos.
- **Causa:** a informação específica está em um trecho que não entrou nos 5. O modelo respondeu só com o que recebeu.

### q037: "O que vale ao adicionar dependências globais a toda a aplicação?"

- **Esperado:** as mesmas ideias de `dependencies` nos decoradores, aplicadas a todas as operações de rota. Frase-fonte em `tutorial/dependencies/global-dependencies.md`.
- **Busca:** o arquivo certo veio em 1º lugar, com o trecho 0 a 377, que é só o parágrafo de abertura. A frase-fonte não está nesse trecho; provavelmente está no seguinte, que não entrou nos 5.
- **Resposta:** diz que as dependências valem para todas as operações de rota; é aceitável no conteúdo, mas não repete a ligação com os decoradores.
- **Causa:** a divisão por estrutura gera trechos pequenos nesse arquivo curto, e a frase exata ficou separada. A métrica rígida conta como erro uma resposta aceitável.

### q040: "Quem deve cuidar do HTTPS na frente da aplicação na maioria dos casos?"

- **Esperado:** um "proxy de terminação"; o provedor pode fazer isso ou é preciso configurá-lo. Frase-fonte em `fastapi-cli.md`.
- **Busca:** vieram `advanced/behind-a-proxy.md` e quatro trechos de `deployment/https.md`, que tratam do mesmo assunto. O trecho esperado em `fastapi-cli.md` é uma menção breve e não entrou.
- **Resposta:** "o proxy". Está certa no essencial, mas não fala em proxy de terminação nem no papel do provedor.
- **Causa:** a documentação responde a essa pergunta em mais de um arquivo, e o conjunto de perguntas aceita só uma fonte. É uma limitação do conjunto, e não necessariamente do sistema.

### q030: "No exemplo do restaurante de hambúrguer, por que o trabalho com o caixa fica 'em pausa'?"

- **Esperado:** porque é preciso esperar os hambúrgueres ficarem prontos. Frase-fonte em `async.md`.
- **Busca:** a busca acertou (esta pergunta não está entre os erros da recuperação): entre os 5 trechos de `async.md` estava o da frase-fonte.
- **Resposta:** conteúdo correto, mas as citações apontam para outros dois trechos (um sobre "esperar o caixa", outro sobre limpar a casa em paralelo, que não tem relação com a pergunta).
- **Causa:** erro de **citação**: o modelo parece ter usado o trecho certo no texto, mas citou os números de outros trechos (provável; os trechos não citados não são gravados no JSON).

## Limitações desta análise

- A conferência de conteúdo foi feita pelo autor, que leu cada resposta e decidiu a marcação por conta própria. Antes de marcar, ele tinha lido uma segunda opinião da IA (registrado em `PROMPTS.md`, entrada 15); a marcação coincidiu com a dela nas duas respostas erradas.
- São 24 perguntas com resposta: cada uma vale 4,2 pontos percentuais. Diferenças de uma pergunta estão no ruído.
- A contagem alternativa "arquivo certo entre os 5" (23 de 24 na busca) é só uma informação complementar. O resultado oficial continua sendo o da métrica definida antes do teste: 0,833 na busca e 0,792 na fonte.
- As causas de q004 e q030 são prováveis, não provadas: o JSON guarda o texto só dos trechos citados.

## O que se poderia tentar numa próxima versão (não feito: o sistema está congelado)

Hipóteses, nenhuma testada:

- Juntar trechos vizinhos do mesmo arquivo, ou usar trechos maiores, para frases como as de q012 e q037 não ficarem separadas.
- Um reranker específico (como `bge-reranker-v2-m3`), já que o reranker feito com o próprio modelo de respostas não ajudou no desenvolvimento.
- Um modelo de respostas maior, para casos como o de q004.
- Aceitar mais de uma fonte válida por pergunta no conjunto de avaliação (q040).
