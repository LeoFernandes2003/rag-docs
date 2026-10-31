# RAG para documentação técnica

- **Curso:** EAD_PROINT_100.DD-ADS-PI-10-74.2026.74
- **Disciplina:** Projeto Integrador
- **Integrante 1:** Leonardo Costa Fernandes, RA 2410279

Assistente que responde dúvidas sobre uma documentação grande de código aberto, **sempre citando o trecho-fonte**, e que mede com números qual estratégia de recuperação funciona melhor (divisão do texto, busca híbrida e reranking). Quando a resposta não está na documentação, o sistema deve dizer que não sabe.

Projeto da disciplina de IA na Programação, Tema 4.

> **Status (31/10/2026):** em desenvolvimento, a caminho do Marco 2. Já existem: corpus limpo, 50 perguntas de avaliação, busca (densa, por palavras e híbrida), resposta com citação e recusa, API (`POST /ask`) e interface (Streamlit). O `docker compose up` completo ainda está em teste. Resultados parciais em `eval/results/README.md`.

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

Veja `docs/proposta-marco1.md` para o problema, o diagrama, as métricas e o plano.

## Estrutura

```text
src/          código da aplicação
tests/        testes automatizados
eval/         perguntas, scripts e resultados da avaliação
evidencias/   vídeo, logs, prints e índice de evidências
docs/         proposta, documentação técnica e trabalho de pesquisa
```

## Ferramentas de IA usadas na programação

- Claude (Anthropic), em conversa de chat, para gerar o esqueleto do repositório e rascunhar a proposta. Todas as interações relevantes estão em `PROMPTS.md`.

A IA dentro do produto roda apenas com modelos abertos locais, via Ollama.

## Licenças de terceiros

A preencher conforme as dependências entrarem (FastAPI, Qdrant, Ollama e os modelos escolhidos).

## Contribuição

Projeto individual de Leonardo Costa Fernandes (RA 2410279).
