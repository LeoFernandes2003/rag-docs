# 3. Decisões de arquitetura

Cada registro tem contexto, decisão e alternativas descartadas. Os ADRs 1 a 5 são as decisões de arquitetura; os ADRs 6 e 7 são decisões de processo (protocolo de avaliação e registro de execução), separados mais abaixo. Os números vêm de `eval/results/README.md`: as comparações de escolha foram feitas no conjunto de desenvolvimento (16 perguntas com resposta) e o resultado oficial é o do conjunto de teste (24 com resposta e 6 sem, medido em 10/11/2026), com o baseline medido também no teste em 16/11/2026.

## ADR 1. Dividir o texto por estrutura (títulos), não por tamanho fixo

- **Contexto:** a documentação é organizada em seções com títulos. Cortar a cada 1000 caracteres separa explicações dos exemplos de código.
- **Decisão:** estratégia `structure`, que corta nos títulos (limite de 1000 caracteres por trecho). Gera 1626 trechos.
- **Alternativas:** `fixed` (tamanho fixo, sem sobreposição), que é o baseline. No desenvolvimento, na busca densa os dois empataram (0,812). Na combinação final a estrutura teve 0,938 e o tamanho fixo 0,875. Porém, tamanho fixo com BM25 e tradução teve 1,000, o melhor número individual. Com 16 perguntas, uma pergunta vale 6,25 pontos percentuais, então essas diferenças estão no ruído (ver `eval/results/README.md`).
- **Limite honesto da decisão:** a escolha da estrutura se apoia mais no motivo de manter blocos de código e seções inteiros do que em ganho comprovado. O número oficial veio do conjunto de teste (0,833, ver o resultado abaixo). A variante com sobreposição não foi medida.
- **Resultado no teste:** o sistema final (estrutura) teve Recall@5 de 0,833 (20/24) e o baseline (tamanho fixo, só busca densa) 0,875 (21/24). As perguntas q012 e q037, que o sistema final errou, o baseline acertou; isso é compatível com a hipótese de que a divisão por estrutura separou as frases esperadas, mas não a prova, porque os dois sistemas diferem também na busca por palavras e na tradução. A decisão não foi revista, porque o sistema foi congelado antes do teste (ver ADR 6).

## ADR 2. Busca híbrida (densa + BM25) com fusão RRF

- **Contexto:** a busca por significado (embeddings) acha paráfrases, mas erra nomes exatos como `Depends` ou `dependency_overrides`. A busca por palavras faz o contrário.
- **Decisão:** unir as duas com Reciprocal Rank Fusion (k=60, 20 candidatos de cada lado).
- **Alternativas:** só densa (0,812 em ambas as divisões) e só BM25 sem tradução (0,500 e 0,312). A híbrida sem tradução piora quando uma das listas é ruidosa (0,688 com tamanho fixo). Com tradução, a híbrida chegou a 0,938 com estrutura. BM25 com tradução sozinho teve 0,938 (estrutura) e 1,000 (tamanho fixo), o que mostra que no desenvolvimento a busca por palavras traduzida já resolve quase tudo. A híbrida foi mantida por combinar as duas fontes de sinal, mas o ganho sobre BM25 com tradução não foi demonstrado com 16 perguntas.
- **Resultado no teste:** a busca híbrida com tradução (parte do sistema final) teve 0,833 e a busca só por significado do baseline teve 0,875. Com 24 perguntas a diferença de uma pergunta está no ruído, então o teste não confirma que a híbrida seja melhor que a simples neste corpus.

## ADR 3. Traduzir a pergunta para inglês só na busca por palavras

- **Contexto:** a pergunta é em português e o corpus em inglês, então o BM25 quase não encontra palavras em comum (0,312).
- **Decisão:** o modelo local traduz a pergunta e o resultado alimenta só o BM25. O embedding (bge-m3, multilíngue) usa a pergunta original.
- **Alternativas:** traduzir o corpus (caro e fora do escopo); usar a tradução também no embedding (não medido). Limitação: o modelo pequeno às vezes traduz mal (ex.: "resposta temporária" virou "response status").

## ADR 4. Gerar com modelo pequeno local e prompt com citação obrigatória e recusa fixa

- **Contexto:** custo zero e computador sem GPU suportada. O modelo `qwen2.5:3b` roda em CPU.
- **Decisão:** prompt v5 (temperatura 0): responder só com os trechos, em frases completas, depois uma linha `Fontes: [n]`; se não houver resposta, escrever exatamente `NÃO ENCONTREI NA DOCUMENTAÇÃO.`. Uma nova tentativa se a resposta vier vazia ou sem citação. Cada versão do prompt foi medida antes de seguir (v2 a v5).
- **Resultado no teste (prompt v5):** recusa indevida 0/24, recusa correta 6/6, nenhuma pergunta sem resposta respondida, citação válida 1,000, fonte correta 0,792 (19/24) e conferência manual de 22/24 com resposta e 6/6 sem resposta. Tempo em CPU: média de 25 s por resposta, máximo de 38 s.
- **Alternativas:** prompt com exemplo (o modelo copiava o exemplo); várias mudanças de uma vez (v3, piorou); recusa por nota mínima de similaridade (descartada: a nota não separa perguntas com e sem resposta, 0,619 contra 0,630).

## ADR 5. Não usar reranker

- **Contexto:** o enunciado pede comparar reranking. Foi testado um reranker por nota atribuída pelo próprio modelo de texto a cada candidato.
- **Decisão:** não adotar. Híbrida com tradução e reranker teve Recall@5 de 0,875, abaixo dos 0,938 sem ele, e deixa a resposta mais lenta (cerca de 45 segundos a mais por pergunta).
- **Alternativas:** um modelo de reranking dedicado (cross-encoder) não foi testado. Fica como trabalho futuro.

# Decisões de processo

Os dois registros seguintes não mudam a arquitetura: dizem como o trabalho foi conduzido depois do teste final.

## ADR 6. Não trocar o sistema depois de ver o resultado do teste

- **Contexto:** depois do teste final, o baseline (busca só por significado, trechos de tamanho fixo) foi medido no mesmo conjunto e acertou uma pergunta a mais (0,875 contra 0,833).
- **Decisão:** manter o sistema como estava. Trocar para o baseline seria ajustar o sistema ao conjunto de teste, o que quebra o protocolo, e a diferença de uma pergunta em 24 está no ruído.
- **Alternativas:** adotar o baseline (descartada pelo motivo acima); repetir a comparação com mais perguntas, que fica como trabalho futuro. O resultado, incluindo o fato de a vantagem do desenvolvimento não se repetir no teste, está descrito no artigo (seções 4.4 e 4.8).

## ADR 7. Registrar em log cada pergunta, depois do teste final

- **Contexto:** o enunciado pede logs com data e hora de uma execução completa, mostrando entradas, decisões do sistema e saídas. A API não registrava nada; só os arquivos de avaliação guardavam as respostas, sem horário.
- **Decisão:** a API passa a escrever uma linha de log para a pergunta recebida, a decisão (respondeu, evidência fraca ou modelo recusou, com nota de similaridade, trechos devolvidos e trechos citados), a resposta e as falhas tratadas. A mudança só registra: não altera a busca, o prompt nem a resposta, e por isso os resultados do teste final continuam valendo. Dois testes automáticos conferem o registro.
- **Alternativas:** usar só o log de acesso do servidor (mostra apenas `POST /ask 200`, sem a pergunta nem a decisão); gerar o log a partir dos arquivos de avaliação (não tem horário e não vem da aplicação rodando).
