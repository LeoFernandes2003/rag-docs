# 3. Decisões de arquitetura

Cada registro tem contexto, decisão e alternativas descartadas. Os números vêm de `eval/results/README.md` (conjunto de desenvolvimento, 16 perguntas com resposta).

## ADR 1. Dividir o texto por estrutura (títulos), não por tamanho fixo

- **Contexto:** a documentação é organizada em seções com títulos. Cortar a cada 1000 caracteres separa explicações dos exemplos de código.
- **Decisão:** estratégia `structure`, que corta nos títulos (limite de 1000 caracteres por trecho). Gera 1626 trechos.
- **Alternativas:** `fixed` (tamanho fixo, sem sobreposição), que é o baseline. No desenvolvimento, na busca densa os dois empataram (0,812). Na combinação final a estrutura teve 0,938 e o tamanho fixo 0,875. Porém, tamanho fixo com BM25 e tradução teve 1,000, o melhor número individual. Com 16 perguntas, uma pergunta vale 6,25 pontos percentuais, então essas diferenças estão no ruído (ver `eval/results/README.md`).
- **Limite honesto da decisão:** a escolha da estrutura se apoia mais no motivo de manter blocos de código e seções inteiros do que em ganho comprovado. O número oficial virá do conjunto de teste, medido uma só vez. A variante com sobreposição não foi medida.

## ADR 2. Busca híbrida (densa + BM25) com fusão RRF

- **Contexto:** a busca por significado (embeddings) acha paráfrases, mas erra nomes exatos como `Depends` ou `dependency_overrides`. A busca por palavras faz o contrário.
- **Decisão:** unir as duas com Reciprocal Rank Fusion (k=60, 20 candidatos de cada lado).
- **Alternativas:** só densa (0,812 em ambas as divisões) e só BM25 sem tradução (0,500 e 0,312). A híbrida sem tradução piora quando uma das listas é ruidosa (0,688 com tamanho fixo). Com tradução, a híbrida chegou a 0,938 com estrutura. BM25 com tradução sozinho teve 0,938 (estrutura) e 1,000 (tamanho fixo), o que mostra que no desenvolvimento a busca por palavras traduzida já resolve quase tudo. A híbrida foi mantida por combinar as duas fontes de sinal, mas o ganho sobre BM25 com tradução não foi demonstrado com 16 perguntas.

## ADR 3. Traduzir a pergunta para inglês só na busca por palavras

- **Contexto:** a pergunta é em português e o corpus em inglês, então o BM25 quase não encontra palavras em comum (0,312).
- **Decisão:** o modelo local traduz a pergunta e o resultado alimenta só o BM25. O embedding (bge-m3, multilíngue) usa a pergunta original.
- **Alternativas:** traduzir o corpus (caro e fora do escopo); usar a tradução também no embedding (não medido). Limitação: o modelo pequeno às vezes traduz mal (ex.: "resposta temporária" virou "response status").

## ADR 4. Gerar com modelo pequeno local e prompt com citação obrigatória e recusa fixa

- **Contexto:** custo zero e computador sem GPU suportada. O modelo `qwen2.5:3b` roda em CPU.
- **Decisão:** prompt v5 (temperatura 0): responder só com os trechos, em frases completas, depois uma linha `Fontes: [n]`; se não houver resposta, escrever exatamente `NÃO ENCONTREI NA DOCUMENTAÇÃO.`. Uma nova tentativa se a resposta vier vazia ou sem citação. Cada versão do prompt foi medida antes de seguir (v2 a v5).
- **Alternativas:** prompt com exemplo (o modelo copiava o exemplo); várias mudanças de uma vez (v3, piorou); recusa por nota mínima de similaridade (descartada: a nota não separa perguntas com e sem resposta, 0,619 contra 0,630).

## ADR 5. Não usar reranker

- **Contexto:** o enunciado pede comparar reranking. Foi testado um reranker por nota atribuída pelo próprio modelo de texto a cada candidato.
- **Decisão:** não adotar. Híbrida com tradução e reranker teve Recall@5 de 0,875, abaixo dos 0,938 sem ele, e deixa a resposta mais lenta.
- **Alternativas:** um modelo de reranking dedicado (cross-encoder) não foi testado. Fica como trabalho futuro.
