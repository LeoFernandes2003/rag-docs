# Corpus

Documentação usada como base de conhecimento do assistente.

- **Origem:** repositório do FastAPI, versão `0.162.0` (https://github.com/fastapi/fastapi/releases/tag/0.162.0).
- **Licença:** MIT (conferir o arquivo `LICENSE` dentro do pacote baixado).
- **Idioma:** textos em inglês (`docs/en/docs`). As perguntas de avaliação são em português.
- **Versão fixa:** o corpus nunca é atualizado durante o projeto, para que os resultados sejam reproduzíveis.

## O que entra

Tudo em `docs/en/docs`, exceto o que está listado abaixo.

## O que fica de fora

| Item | Motivo |
| --- | --- |
| `css/`, `js/`, `img/` | Estilo, scripts e imagens do site, não são texto |
| `reference/` | Gerado a partir do código; cada arquivo tem só uma linha de indicação e uma lista de nomes |
| `resources/` | Lista de links |
| `release-notes.md` | Histórico de versões: grande, repetitivo e faria a busca trazer notas de versão |
| `_llm-test.md`, `translation-banner.md` | Arquivos técnicos do site |
| `newsletter.md`, `management.md`, `fastapi-people.md`, `external-links.md`, `help-fastapi.md`, `translations.md`, `contributing.md` | Sobre a comunidade e o projeto, não ajudam a responder dúvidas técnicas |

As listas estão em `src/app/ingest/prepare.py` e podem ser ajustadas.

## Limpeza

Os arquivos originais são escritos para virar um site. O script `src/app/ingest/clean.py`:

1. troca cada indicação `{* ../../docs_src/arquivo.py *}` pelo código real, em um bloco de código;
2. remove enfeites de cor dos blocos de terminal (`<font>`, `<span>` e semelhantes);
3. converte HTML do texto em Markdown simples: `<strong>`, `<kbd>`, `<code>`, `<a>`; `<abbr>` e `<dfn>` viram `X (explicação)`; imagens viram `[Image: descrição]` ou somem;
4. remove os marcadores de âncora dos títulos (`{ #first-steps }`);
5. troca os blocos `/// tip` (com ou sem espaços na frente) por um rótulo simples (**Tip**).

Os exemplos de código dos tutoriais (blocos com três crases) **não são alterados**, exceto os blocos `console`. Muitos deles são HTML de verdade, como `<form>` e `<button>`.

## Limitações conhecidas

- Dos 453 exemplos de código indicados no texto, 452 foram inseridos. O que ficou de fora está em `how-to/configure-swagger-ui.md` e aponta para o código-fonte da própria biblioteca (`fastapi/openapi/docs.py`), não para a pasta `docs_src`. O script remove essa indicação, e o texto explicativo ao redor permanece.
- As opções de destaque de linhas (`hl[...]`) são ignoradas: o código entra completo.
- Algumas páginas repetem o mesmo exemplo várias vezes, cada uma com um destaque diferente (por exemplo, `tutorial/sql-databases.md`). Isso gera trechos duplicados, que serão tratados na etapa de divisão do texto.

## Como gerar

A partir da pasta `src`, com `CAMINHO` sendo a pasta onde o FastAPI foi extraído:

```bash
python -m app.ingest.prepare --docs CAMINHO/docs/en/docs --docs-src CAMINHO/docs_src
```

O resultado vai para `data/raw/corpus`, na raiz do repositório, com um `manifest.json` que lista os arquivos incluídos. Essa pasta não vai para o Git.
