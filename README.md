# RAG para documentação técnica

- **Curso:** EAD_PROINT_100.DD-ADS-PI-10-74.2026.74
- **Disciplina:** Projeto Integrador
- **Integrante 1:** Leonardo Costa Fernandes, RA 2410279

Assistente que responde dúvidas sobre uma documentação grande de código aberto, **sempre citando o trecho-fonte**, e que mede com números qual estratégia de recuperação funciona melhor (divisão do texto, busca híbrida e reranking). Quando a resposta não está na documentação, o sistema deve dizer que não sabe.

Projeto da disciplina de IA na Programação, Tema 4.

> **Status (22/11/2026):** versão final, com as funcionalidades congeladas. Desde o teste final (10/11) mudaram só documentos, o registro em log da API (ADR 7 em `docs/decisoes.md`) e o indicador de carregamento da interface. **Resultado oficial no conjunto de teste** (24 perguntas com resposta e 6 sem, medido uma única vez): Recall@5 0,833; citação válida 1,000; recusa indevida 0 de 24; recusa correta 6 de 6; conferência manual do autor 22 de 24 e 6 de 6. O baseline (busca só por significado, trechos de tamanho fixo) teve Recall@5 0,875: a diferença de uma pergunta está dentro do ruído e o sistema não foi trocado depois do teste. Onde ver: resultados em `eval/results/README.md`, trabalho de pesquisa em `docs/pesquisa-abnt.pdf`, provas de funcionamento em `evidencias/README.md`, documentação técnica em `docs/README.md` e uso de IA em `PROMPTS.md`.

## Como rodar

Pré-requisito: Docker com Docker Compose.

```bash
docker compose up --build
```

Na primeira vez, o serviço `setup` baixa os modelos, a documentação do FastAPI 0.162.0 e cria o índice (vários minutos). Depois:

- Interface: http://localhost:8501
- API: http://localhost:8000 (documentação interativa em `/docs`)
- Saúde do serviço: http://localhost:8000/health

Nenhuma chave de API é necessária. Variáveis de ambiente (valores padrão em `.env.example`):

| Variável | Para que serve |
| --- | --- |
| `OLLAMA_URL` | Endereço do Ollama (modelos locais) |
| `QDRANT_URL` | Endereço do banco vetorial |
| `GEN_MODEL` | Modelo de geração de respostas |
| `EMBED_MODEL` | Modelo de embeddings |

### Rodar sem Docker (desenvolvimento)

```bash
python -m venv .venv && source .venv/bin/activate
pip install -r requirements-dev.txt
pytest
uvicorn app.main:app --reload --app-dir src
```

## Arquitetura

Diagrama e fluxo de dados em `docs/arquitetura.md`. O problema, as métricas e o plano estão em `docs/proposta-marco1.md`.

## Estrutura

```text
src/          código da aplicação
tests/        testes automatizados
eval/         perguntas, scripts e resultados da avaliação
evidencias/   vídeo, logs, prints e índice de evidências
docs/         proposta, documentação técnica e trabalho de pesquisa
```

## Ferramentas de IA usadas na programação

- Claude (Anthropic), plano Pro pago pelo autor, usado em conversa de chat para escrever e revisar código, testes, scripts de avaliação e documentação. O uso de IA paga e o trabalho individual foram confirmados pelo professor em 31/10/2026.
- Todas as interações relevantes, com o que foi aceito, corrigido ou descartado, estão em `PROMPTS.md`.
- As revisões dos pull requests foram feitas por IA e declaradas em comentário em cada PR, porque o projeto é individual.

A IA dentro do produto roda apenas com modelos abertos locais, via Ollama, sem custo e sem chaves de API.

## Licenças de terceiros

| Componente | Uso no projeto | Licença | Fonte |
| --- | --- | --- | --- |
| FastAPI | API (`/ask`, `/health`) e corpus (documentação 0.162.0) | MIT | https://github.com/fastapi/fastapi |
| Streamlit | Interface web | Apache-2.0 | https://github.com/streamlit/streamlit |
| Qdrant (imagem `qdrant/qdrant:v1.20.0`) | Banco vetorial | Apache-2.0 | https://github.com/qdrant/qdrant |
| Ollama (imagem `ollama/ollama`) | Execução local dos modelos | MIT | https://github.com/ollama/ollama |
| bge-m3 (BAAI) | Embeddings | MIT | https://ollama.com/library/bge-m3 |
| qwen2.5:3b (Alibaba Cloud) | Tradução da pergunta e geração da resposta | Qwen Research License (uso de pesquisa e não comercial) | https://ollama.com/library/qwen2.5:3b |

Observação sobre o Qwen: a licença Qwen Research não permite uso comercial. O uso neste trabalho é acadêmico, dentro dessa licença. Para uso comercial seria preciso trocar de modelo.

## Contribuição

Projeto individual de Leonardo Costa Fernandes (RA 2410279).
