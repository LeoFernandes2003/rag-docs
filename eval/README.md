# Avaliação

Aqui ficam o conjunto de perguntas, os dados e os resultados da avaliação. Os scripts
ficam em `src/app/evaluation/` e são executados, a partir da pasta `src`, com
`python -m app.evaluation.<nome>`.

## Como as 50 perguntas são construídas

As perguntas são escritas **antes** de ajustar o sistema, e as de teste final nunca são
usadas para ajustá-lo.

1. **Sorteio das passagens.** `python -m app.evaluation.sample_candidates` sorteia, com
   semente fixa (42), um parágrafo de cada um de 60 arquivos do corpus e grava o
   resultado em `candidates.md` e `candidates.json`. Sortear evita escolher só os
   assuntos fáceis.
2. **Escrita das perguntas com resposta (40).** Para cada passagem escolhida, escreve-se
   uma pergunta em português cuja resposta está nela, a resposta esperada e o trecho-fonte
   copiado da passagem. Passagens que não permitem uma pergunta clara são descartadas.
3. **Escrita das perguntas sem resposta (10).** Perguntas plausíveis sobre assuntos que a
   documentação não cobre, cada uma com termos (`forbidden_terms`) que não podem aparecer
   em nenhum lugar do corpus.
4. **Conferência automática.** `python -m app.evaluation.check_questions --final`
   confirma que cada trecho-fonte existe no corpus, que os termos proibidos não existem
   e que os totais estão certos (40 com resposta, 10 sem; 20 de desenvolvimento, 30 de teste).

## Formato de `questions.jsonl`

Uma pergunta por linha:

```json
{"id": "q001", "split": "dev", "question": "...", "answerable": true, "expected_answer": "...", "source_file": "tutorial/first-steps.md", "source_span": "trecho exato da fonte"}
{"id": "q041", "split": "dev", "question": "...", "answerable": false, "forbidden_terms": ["termo1", "termo2"]}
```

- `split`: `dev` (usado para ajustar o sistema) ou `test` (usado só na avaliação final).
- `answerable: false` marca perguntas cuja resposta não está na documentação.
- `source_file` é o caminho relativo dentro do corpus, como aparece em `candidates.md`.

Os resultados dos experimentos serão adicionados a partir do Marco 2.
