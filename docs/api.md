# 4. Referência da API

A API é feita em FastAPI. A documentação interativa (OpenAPI) fica em http://localhost:8000/docs e o esquema em http://localhost:8000/openapi.json.

## `GET /health`

Indica que o serviço está de pé.

```json
{"status": "ok"}
```

## `GET /config`

Mostra a configuração não secreta (endereços e nomes dos modelos).

```json
{"ollama_url": "http://ollama:11434", "qdrant_url": "http://qdrant:6333", "gen_model": "qwen2.5:3b", "embed_model": "bge-m3"}
```

## `POST /ask`

Corpo da requisição:

```json
{"question": "Como sobrescrever uma dependência em testes?"}
```

`question` tem de 3 a 500 caracteres.

Exemplo:

```bash
curl -X POST http://localhost:8000/ask -H "Content-Type: application/json" \
     -d '{"question": "Como sobrescrever uma dependência em testes?"}'
```

Resposta (campos principais):

| Campo | Tipo | Significado |
| --- | --- | --- |
| `question` | texto | A pergunta recebida |
| `answer` | texto | A resposta, ou a frase de recusa |
| `refused` | booleano | `true` se o sistema recusou |
| `reason` | texto | `respondeu`, `modelo_recusou`, `resposta_vazia` ou `evidencia_fraca` |
| `cited` | lista de números | Trechos citados que existem |
| `sources` | lista | Para cada fonte citada: `n`, `source_file`, `start`, `end`, `text` |
| `retrieved` | lista | Os trechos consultados: `source_file`, `start`, `end` |
| `translated` | texto | A pergunta em inglês usada na busca por palavras |
| `top_score` | número | Nota de similaridade do melhor trecho (informativa) |
| `seconds` | número | Tempo total da resposta |
| `raw` | texto | Saída bruta do modelo |

Códigos de erro:

| Código | Quando |
| --- | --- |
| 422 | Pergunta ausente, curta ou longa demais |
| 503 | Ollama ou Qdrant indisponíveis, ou índice não criado. A mensagem explica o que checar |

## Interface

A interface Streamlit (`src/app/ui.py`, porta 8501) chama `POST /ask`. Veja o [manual do usuário](manual-do-usuario.md).

## Linha de comando

```bash
cd src
python -m app.rag.ask "Como sobrescrever uma dependência em testes?"
```

Mostra a resposta, as fontes citadas, os trechos consultados e o tempo.
