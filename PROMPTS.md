# Registro de uso de IA na programação

Mínimo exigido: 10 interações relevantes. Cada uma com o prompt, um resumo da resposta e o que foi aceito, corrigido ou descartado, com o motivo.

Ferramenta usada: Claude (Anthropic), via chat, plano pago do autor (Leonardo Costa Fernandes, RA 2410279).

Nota de transparência: as entradas abaixo foram redigidas com ajuda do Claude a partir das conversas reais do projeto (23/10 a 31/10/2026). Os prompts estão resumidos, não copiados palavra por palavra. O autor revisou cada entrada e é responsável pelo conteúdo.

## Modelo de entrada

```text
### N. Título curto (data)
**Prompt:** o que foi pedido.
**Resposta (resumo):** o que a IA devolveu.
**Aceito:** ...
**Corrigido:** ... (motivo)
**Descartado:** ... (motivo)
```

## Entradas

### 1. Esqueleto do repositório e proposta do Marco 1 (23/10/2026)
**Prompt:** pedido para montar o repositório do Tema 4 (estrutura exigida no enunciado, CI com um teste, Docker) e rascunhar a proposta técnica.
**Resposta (resumo):** estrutura de pastas, API FastAPI com `/health`, teste com pytest, Dockerfile, docker-compose com API, Qdrant e Ollama, workflow de CI e rascunho da proposta.
**Aceito:** a estrutura de pastas, a API mínima com `/health`, o teste e o workflow de CI (ruff + pytest), porque seguem o que o enunciado pede para o Marco 1.
**Corrigido:** o texto da proposta foi ajustado ao que o autor realmente vai fazer (trabalho individual, modelos locais pequenos) em vez do texto genérico inicial.
**Descartado:** itens além do escopo do Marco 1 sugeridos no rascunho (funcionalidades da API que ainda não existiam), para não prometer o que não estava feito.

### 2. Limpeza do corpus de documentação (24/10/2026)
**Prompt:** pedido para preparar a documentação do FastAPI 0.162.0 (arquivos Markdown) como corpus: limpar o texto e manter a estrutura dos títulos.
**Resposta (resumo):** script de preparação que remove marcações, preserva títulos e blocos de código e grava os arquivos limpos.
**Aceito:** a ideia de preservar a hierarquia de títulos e os blocos de código, que depois permitiu o chunking por estrutura.
**Corrigido:** ao inspecionar a saída apareceram três defeitos: faltava linha em branco depois de blocos de código, sobrava HTML dentro dos blocos e os avisos (admonitions) indentados ficavam misturados ao texto. Foi pedida a correção de cada um e os testes foram ajustados para cobri-los.
**Descartado:** a primeira versão do limpador, que tratava todo o HTML do mesmo jeito, porque apagava conteúdo útil dentro de código.

### 3. Amostra do corpus e perguntas de avaliação (25/10/2026)
**Prompt:** pedido de ajuda para montar 50 perguntas em português (40 com resposta na documentação e 10 sem), divididas em desenvolvimento e teste.
**Resposta (resumo):** formato do arquivo de perguntas, critérios para boas perguntas e uma divisão: 20 para desenvolvimento (16 + 4) e 30 para teste (24 + 6).
**Aceito:** o formato, a proporção de perguntas sem resposta e a regra de usar o conjunto de teste uma única vez, no fim (`--final`).
**Corrigido:** algumas perguntas sugeridas tinham resposta em mais de um arquivo ou dependiam de contexto; o autor e a IA reescreveram essas para ficarem objetivas.
**Descartado:** perguntas muito parecidas entre si, porque inflariam o resultado sem testar nada novo.

### 4. Instalação do Docker (25 a 31/10/2026)
**Prompt:** como instalar o Docker no Windows 10 e rodar o projeto.
**Resposta (resumo):** passos de instalação e uma instrução de instalação por usuário para a pasta do projeto.
**Aceito:** o uso do Docker Desktop e do `docker compose up` como forma única de subir tudo.
**Corrigido:** a orientação de instalação "por usuário" estava errada para este caso; o autor percebeu que o Docker já estava instalado e a IA refez os passos só com o necessário (ligar o Docker e rodar o compose).
**Descartado:** a instalação separada sugerida, porque duplicava algo que já existia.

### 5. Testes da recuperação e erros do ruff (26/10/2026)
**Prompt:** escrever testes para o índice, o BM25 e a busca híbrida, e corrigir as falhas do CI.
**Resposta (resumo):** testes com dados pequenos e correções de estilo.
**Aceito:** a estrutura dos testes e o uso de dados falsos (sem rede) para o CI rodar rápido.
**Corrigido:** alguns testes tinham valor esperado errado (a IA calculou o resultado de cabeça); ao rodar, falharam e o valor foi recalculado pelo código. O CI também reprovou por linhas longas (E501) e `zip` sem `strict` (B905); foram corrigidos.
**Descartado:** o valor esperado calculado de cabeça, porque o teste deve refletir o comportamento real verificado.

### 6. Tradução da pergunta para a busca por palavras (28/10/2026)
**Prompt:** melhorar a recuperação de perguntas em português sobre uma documentação em inglês.
**Resposta (resumo):** traduzir a pergunta para inglês com o modelo local (`qwen2.5:3b`) e usar a tradução só na busca BM25, mantendo a pergunta original no embedding.
**Aceito:** a ideia. Recall@5 no desenvolvimento subiu de 0,500 para 1,000 no BM25 e de 0,688 para 0,875 no híbrido (estrutura: 0,812 para 0,938).
**Corrigido:** o modelo pequeno traduziu mal casos como "resposta temporária" (virou "response status") e acrescentou palavras; o prompt de tradução foi apertado para devolver só a frase traduzida. Os erros restantes foram registrados como limitação.
**Descartado:** usar a tradução também no embedding, porque o bge-m3 já é multilíngue e o ganho não foi medido.

### 7. Prompt de geração v2: modelo copiou o exemplo (29/10/2026)
**Prompt:** escrever o prompt que gera a resposta só com os trechos, cita as fontes e recusa quando não há resposta.
**Resposta (resumo):** prompt com regras e um exemplo de resposta.
**Aceito:** as regras (usar só os trechos, citar [n], recusar com frase fixa).
**Corrigido:** o modelo repetia o exemplo ("Use o parâmetro X para fazer Y"); o exemplo foi removido. A frase de recusa também aparecia em variações ("NÃO ENCONTROU"), então a detecção passou a usar uma expressão regular tolerante.
**Descartado:** o exemplo dentro do prompt, porque modelos pequenos o copiam.

### 8. Prompt v3: várias mudanças de uma vez (29/10/2026)
**Prompt:** reduzir recusas indevidas mudando o prompt.
**Resposta (resumo):** versão com várias regras novas ao mesmo tempo.
**Aceito:** nada da v3; serviu de lição.
**Corrigido:** o resultado piorou (recusa indevida 6/16, fonte certa 8/16). Decidimos mudar uma coisa por vez e medir.
**Descartado:** a v3 inteira, porque misturar mudanças impediu saber qual causava o problema.

### 9. Prompt v4: respostas só com "[1]" (29/10/2026)
**Prompt:** fazer o modelo responder com frases e citar a fonte.
**Resposta (resumo):** instrução para citar entre colchetes e uma nova tentativa automática quando não houvesse citação.
**Aceito:** a nova tentativa (retry) e a detecção de resposta vazia.
**Corrigido:** 7 de 16 respostas vieram só com "[1]". A v5 passou a exigir frases completas e uma linha separada `Fontes: [n]`; a verificação de resposta vazia ignora essa linha e os `[n]`. Resultado no desenvolvimento: recusa indevida 0/16, recusa correta 4/4, fonte certa 14/16, citação válida 1,000.
**Descartado:** a v4, porque o modelo obedecia à citação mas não escrevia a resposta.

### 10. Parser da conferência manual (29/10/2026)
**Prompt:** gerar um arquivo para o autor conferir cada resposta e um script que lê as marcações.
**Resposta (resumo):** arquivo Markdown com caixas `[ ]` e `score_review`.
**Aceito:** o fluxo: o autor marca `[x]` nas respostas corretas e o script soma.
**Corrigido:** o leitor era rígido demais ("[ x]" contava 1/16 em vez de 15/16) e meu teste tinha um exemplo errado. A expressão regular ficou tolerante e o teste foi corrigido. Resultado: 15/16 e 4/4 conferidos pelo autor.
**Descartado:** a leitura estrita das marcações, porque falhava com espaço dentro dos colchetes.

### 11. Pedido recusado: marcar a conferência manual como se fosse humana (29/10/2026)
**Prompt:** o autor pediu que a IA marcasse os `x` da conferência e que isso ficasse sem registro de ter sido feito por IA.
**Resposta (resumo):** a IA recusou registrar uma conferência feita por ela como humana e explicou que isso falsearia a métrica de avaliação e o registro de uso de IA.
**Aceito:** a recusa. O autor leu as respostas e marcou ele mesmo; a IA só discutiu casos duvidosos (q023 e q033).
**Corrigido:** nada no código; o procedimento passou a exigir que a marcação seja humana.
**Descartado:** a ideia de a IA preencher a conferência, porque a conferência existe justamente para checar o modelo de forma independente.

### 12. Arquivo antigo sobrescreveu o `pipeline.py` e o CI falhou (29/10/2026)
**Prompt:** entregar a interface (API + UI) em um zip para subir via pull request.
**Resposta (resumo):** o zip trazia uma versão antiga de `pipeline.py` junto.
**Aceito:** a API `/ask` e a interface Streamlit.
**Corrigido:** o CI falhou com "cannot import is_empty_answer" porque o arquivo antigo substituiu o bom. A IA reconheceu o erro, gerou um zip só com o arquivo correto, o autor o enviou ao mesmo PR e o CI passou.
**Descartado:** o `pipeline.py` do primeiro zip; passamos a conferir o conteúdo do zip antes de entregar.

### 13. Reranker e diagnóstico errado da IA (31/10/2026)
**Prompt:** testar um reranker (LLM dá nota a cada trecho) para melhorar o Recall@5.
**Resposta (resumo):** módulo `rerank.py` e opção `--rerank` na avaliação.
**Aceito:** o experimento e o registro honesto do resultado negativo: híbrido com tradução e reranker teve 0,875, abaixo dos 0,938 sem ele. Não foi adotado.
**Corrigido:** quando a execução parou, a IA culpou o Ollama e a memória; na verdade foi o autor que interrompeu com Ctrl+C durante uma execução sem mensagens. A IA corrigiu o diagnóstico e acrescentou mensagens de progresso.
**Descartado:** o reranker na versão final, porque piorou a métrica e aumentou o tempo.

### 14. Revisão de pull requests (27/10 a 31/10/2026)
**Prompt:** como cumprir a regra de revisão dos PRs trabalhando sozinho.
**Resposta (resumo):** a IA revisa o conteúdo e o autor registra um comentário no PR começando com "Revisão feita por IA (Claude), não por um colega humano."
**Aceito:** declarar claramente que a revisão foi de IA, em vez de fingir revisão humana.
**Corrigido:** nada até agora; a regra do enunciado ("revisado por outro membro humano") segue pendente de confirmação por escrito do professor.
**Descartado:** a ideia de aprovar sem comentário, porque esconderia quem revisou.
