# Avaliação

Aqui ficam o conjunto de perguntas, os scripts de avaliação e os resultados.

## Conjunto de perguntas (`questions.jsonl`)

50 perguntas escritas **antes** de ajustar o sistema, uma por linha:

```json
{"id": "q001", "split": "dev", "question": "...", "answerable": true, "expected_answer": "...", "source_file": "docs/...md", "source_span": "trecho exato esperado"}
{"id": "q041", "split": "test", "question": "...", "answerable": false}
```

- `split`: `dev` (usado para ajustar o sistema) ou `test` (usado só na avaliação final).
- `answerable: false` marca perguntas cuja resposta não está na documentação.

Os arquivos de dados e resultados serão adicionados a partir do Marco 2.
