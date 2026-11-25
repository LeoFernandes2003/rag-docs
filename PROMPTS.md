# Registro de uso de IA na programação

Mínimo exigido: 10 interações relevantes. Cada uma com o prompt, um resumo da resposta e o que foi aceito, corrigido ou descartado, com o motivo.

Ferramenta usada: Claude (Anthropic), via chat, plano pago do autor (Leonardo Costa Fernandes, RA 2410279).

Nota de transparência: as entradas abaixo foram redigidas com ajuda do Claude a partir das conversas reais do projeto (23/10 a 25/11/2026). Os prompts estão resumidos, não copiados palavra por palavra. O autor revisou cada entrada e é responsável pelo conteúdo.

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

### 15. Segunda opinião da IA antes da conferência manual do teste (10/11/2026)
**Prompt:** o autor pediu uma lista do que a IA consideraria certo ou errado nas 30 respostas do teste final, deixando claro que ele leria tudo e decidiria.
**Resposta (resumo):** a IA listou cada resposta com um motivo, chamou a lista de segunda opinião e disse que a marcação do arquivo era do autor: 22 ou 23 de 24 certas com resposta (só q004 clara, q012 duvidosa) e 6 de 6 recusas corretas.
**Aceito:** usar a lista só como comparação. O autor leu as respostas e marcou ele mesmo: 22/24 e 6/6. A marcação coincidiu com a opinião da IA nas duas respostas erradas (q004 e q012).
**Corrigido:** a explicação da IA sobre as 6 perguntas sem resposta foi ambígua; o autor as deixou sem `[x]` e o cálculo deu 0/6. A regra foi reexplicada (marca-se `[x]` quando o sistema fez o esperado, inclusive recusar) e o resultado final foi 6/6.
**Descartado:** a IA preencher o arquivo de conferência (mesma regra da entrada 11). O autor leu cada resposta e decidiu a marcação por conta própria; o registro fica aqui para ficar claro que a opinião da IA existiu antes da marcação.

### 16. Análise de falhas do teste final e correção da documentação (10/11/2026)
**Prompt:** analisar os erros do teste final e dizer onde cada um falhou (busca, modelo ou citação).
**Resposta (resumo):** a IA leu os JSON do teste e classificou 5 casos: 3 de busca (q012, q037, q040), 1 de modelo (q004) e 1 de citação (q030), com os trechos recuperados como evidência. Registrou também a limitação do JSON, que só guarda o texto dos trechos citados.
**Aceito:** a classificação e o texto de `evidencias/analise-de-falhas.md`, com as causas de q004 e q030 marcadas como prováveis.
**Corrigido:** a IA percebeu que `docs/avaliacao.md` dizia que "fonte certa" era o arquivo esperado, mas o código exige que o trecho citado cubra a frase-fonte; o texto foi corrigido. A IA também tinha comentado que o arquivo certo apareceu em 23 de 24 buscas; isso ficou só como informação complementar.
**Descartado:** trocar a métrica oficial depois de ver o resultado do teste (continuam 0,833 na busca e 0,792 na fonte).

### 17. Revisão contra o enunciado: a API não registrava logs (10/11 a 20/11/2026)
**Prompt:** conferir o repositório contra a seção "Evidências de funcionamento" do enunciado antes da entrega.
**Resposta (resumo):** a IA comparou cada evidência com o que existia e apontou que a evidência 4 (logs com data e hora, mostrando entradas, decisões e saídas) não podia ser feita: a API não registrava nada, e os arquivos de avaliação não têm horário.
**Aceito:** acrescentar o registro em log na API, depois do teste final, só escrevendo o log e sem alterar a busca, o prompt nem a resposta, para os resultados do teste continuarem valendo (ADR 7). Dois testes automáticos conferem o log.
**Corrigido:** a IA não tinha percebido essa falta durante o desenvolvimento; só apareceu na revisão contra o enunciado. A mudança foi limitada a log de propósito, para não invalidar o teste final.
**Descartado:** montar o "log" a partir dos JSON da avaliação (sem horário e não vem da aplicação rodando) e usar só o log de acesso do servidor (mostra `POST /ask 200`, sem a pergunta nem a decisão).

### 18. Sessão de capturas e log: dados fora do roteiro e pull request com arquivos demais (20/11 a 22/11/2026)
**Prompt:** guiar uma sessão de uso com seis situações (duas respostas, duas recusas, uma falha tratada e uma recuperação), exportar o log e preparar os arquivos para subir por pull request.
**Resposta (resumo):** roteiro das seis situações, comandos para exportar o log com `docker compose logs -t api` e um pacote com o log, as capturas e o índice de evidências atualizado.
**Aceito:** o roteiro e o pacote final (pull requests #19 e #20), com cada captura ligada às linhas do log no índice.
**Corrigido:** (1) o primeiro log exportado trazia perguntas de teste feitas antes da sessão, que não faziam parte do roteiro; como o enunciado proíbe dados pessoais em logs, a API foi recriada para zerar o log e as seis situações foram refeitas. (2) O pull request #18 mostrou 24 arquivos em vez de 4, porque a pasta do computador tinha arquivos temporários (`__pycache__`); conferi "Files changed", fechamos o PR e refizemos como #19, arrastando só a partir da pasta limpa extraída do zip.
**Descartado:** o primeiro log, o pull request #18 e a prática de subir arquivos a partir da pasta de trabalho.

### 19. Indicador de carregamento preso depois de um erro (22/11/2026)
**Prompt:** corrigir a interface, que continuava girando depois de a API devolver o erro 503 (situação 5 da sessão).
**Resposta (resumo):** a IA indicou como causa provável o `st.stop()` dentro do bloco do indicador de carregamento e propôs guardar a mensagem de erro, sair do bloco e só então mostrar o erro e parar.
**Aceito:** a correção em `src/app/ui.py`.
**Corrigido:** o ambiente de trabalho da IA não tinha como instalar o Streamlit, então a causa era provável e a correção só foi verificada por leitura do código. A confirmação veio da execução real em 23/11/2026 (subindo do zero, derrubando o Ollama e perguntando): depois da mensagem de erro o indicador de carregamento sumiu.
**Descartado:** deixar o defeito apenas como "detalhe visual" no índice de evidências; ele foi corrigido e o índice atualizado.

### 20. Revisão final de coerência da documentação (22/11/2026)
**Prompt:** reler a proposta e o enunciado, e conferir tudo o que foi feito para ter certeza de que nada ficou de fora.
**Resposta (resumo):** a IA releu o repositório e listou: README ainda com o status de 03/11; ADRs 6 e 7 misturados com os cinco de arquitetura (o enunciado pede de 3 a 5); `PROMPTS.md` sem as entradas da fase final; contagem de testes desatualizada (97, hoje 99); frase do Marco 2 em `eval/README.md`; e a limitação de que uma resposta sem citação válida ainda é devolvida, sem fontes.
**Aceito:** todas as correções, reunidas em um único pull request, e o registro dessa limitação em `docs/seguranca-e-limitacoes.md`.
**Corrigido:** nada no comportamento do sistema; só documentos e o indicador de carregamento.
**Descartado:** renumerar os ADRs (mantidos os números para não quebrar as referências do artigo e do índice de evidências) e mudar o sistema por causa de qualquer achado (o sistema está congelado desde o teste).

### 21. Falha de rede do Docker no teste do zero (23/11/2026)
**Prompt:** colei no chat os erros que apareceram ao subir o projeto do zero: primeiro `Bind for 0.0.0.0:11435 failed: port is already allocated` e, depois, `qdrant:6333 não respondeu a tempo` (duas vezes).
**Resposta (resumo):** para o primeiro erro, a IA pediu a lista de contêineres (`docker ps`) e viu que os contêineres da pasta antiga tinham voltado sozinhos quando o Docker Desktop reiniciou; a solução foi pará-los com `docker stop`. Para o segundo, a IA indicou uma falha da rede interna do Docker (o nome `qdrant` não era resolvido) e a sequência `docker compose down`, fechar o Docker Desktop, `wsl --shutdown`, abrir de novo e subir com `docker compose up --build`.
**Aceito:** as duas soluções; depois delas o ambiente subiu até a mensagem "Ambiente pronto." e a indexação dos 1626 trechos terminou.
**Corrigido:** nada no projeto; foi problema do ambiente do computador, não do código. A IA não tinha como confirmar a causa exata da falha de rede, só que a sequência funcionou.
**Descartado:** mexer no `docker-compose.yml` ou no `setup` por causa desse erro.

### 22. Edição do vídeo de evidência (23/11/2026)
**Prompt:** enviei o vídeo gravado (7 min 2 s) e pedi que fosse deixado em condições de uso como evidência.
**Resposta (resumo):** a IA analisou o vídeo e listou os problemas: mais de 5 minutos, o endereço público do computador aparecendo no PowerShell (linha `External URL` do Streamlit), um comando digitado errado, a janela do programa de gravação, um comando de logs que não rodou e esperas longas. Cortou e acelerou os trechos, cobriu o endereço com uma tarja preta e acrescentou legendas nos pontos de corte e de aceleração (4 min 39 s).
**Aceito:** o vídeo editado, depois de eu assistir ao arquivo inteiro.
**Corrigido:** a primeira versão editada ainda deixava o endereço visível em poucos quadros, nas bordas das tarjas; a IA achou isso lendo o texto dos quadros (OCR), aumentou as tarjas e conferiu de novo: na versão final nenhum quadro mostra o endereço. A conferência por leitura de texto não é infalível, por isso eu também assisti ao vídeo.
**Descartado:** gravar de novo (custaria mais uma construção de cerca de 25 minutos) e desfocar em vez de cobrir (a tarja preta é mais segura).

