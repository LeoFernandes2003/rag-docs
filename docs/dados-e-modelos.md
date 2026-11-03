# 5. Dados e modelos

## Corpus

| Item | Valor |
| --- | --- |
| Origem | Documentação do FastAPI 0.162.0 (`docs/en/docs` e `docs_src`), https://github.com/fastapi/fastapi/releases/tag/0.162.0 |
| Licença | MIT |
| Idioma | Inglês |
| Tamanho | 121 arquivos Markdown após a limpeza; 452 exemplos de código inseridos |
| Tratamento | Limpeza do HTML e dos marcadores do site, código real no lugar das referências (detalhes em [corpus.md](corpus.md)) |
| Divisão | 1626 trechos de até 1000 caracteres, cortados por estrutura |
| Versão fixa | Nunca atualizado durante o projeto, para os resultados serem reproduzíveis |
| Dados pessoais | Nenhum: é documentação pública de software |

O corpus é baixado automaticamente pelo serviço `setup` (`src/app/ingest/fetch.py`) e fica na pasta `data/raw/corpus`, que não vai para o Git.

## Perguntas de avaliação

`eval/questions.jsonl`: 50 perguntas em português (40 com resposta na documentação e 10 sem), escritas antes de ajustar o sistema. 20 são de desenvolvimento (16 + 4) e 30 de teste (24 + 6). São sintéticas, escritas pelo autor com apoio da IA, e não contêm dados pessoais. Detalhes em `eval/README.md`.

## Modelos

| Modelo | Papel | Licença | Origem |
| --- | --- | --- | --- |
| `bge-m3` (BAAI) | Embeddings multilíngues | MIT | https://ollama.com/library/bge-m3 |
| `qwen2.5:3b` (Alibaba Cloud) | Tradução da pergunta e geração da resposta | Qwen Research License (pesquisa, não comercial) | https://ollama.com/library/qwen2.5:3b |

Os dois rodam localmente pelo Ollama, sem enviar dados para fora do computador.

### Ficha do modelo de geração (`qwen2.5:3b`)

- **Uso pretendido neste projeto:** responder em português usando só trechos da documentação do FastAPI, com citação.
- **Configuração:** temperatura 0, contexto de 4096 tokens, até 400 tokens de resposta.
- **Limitações conhecidas:** modelo pequeno; pode traduzir mal, copiar instruções do prompt, responder só com `[1]` ou recusar perguntas respondíveis. O prompt v5 e a nova tentativa mitigam, mas não eliminam (ver [seguranca-e-limitacoes.md](seguranca-e-limitacoes.md)).
- **Restrição de licença:** não pode ser usado comercialmente sem acordo com o fornecedor.

### Ficha do conjunto de perguntas

- **Composição:** 40 perguntas com resposta (trecho-fonte esperado) e 10 sem resposta (com termos proibidos conferidos contra o corpus).
- **Viés conhecido:** as perguntas foram escritas a partir de parágrafos sorteados do corpus e reaproveitam palavras da documentação, o que favorece a busca por palavras mais do que perguntas de usuários reais.
