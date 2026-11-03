# 2. Instalação e execução

## Pré-requisitos

- Docker com Docker Compose (Docker Desktop no Windows ou Mac).
- Alguns GB livres em disco (os modelos ocupam a maior parte) e 16 GB de memória RAM recomendados (os modelos rodam em CPU).
- Internet na primeira execução (baixa modelos e a documentação). Depois funciona sem internet.
- Nenhuma conta, chave ou pagamento.

## Subir o projeto

```bash
git clone https://github.com/LeoFernandes2003/rag-docs.git
cd rag-docs
docker compose up --build
```

Na primeira vez, o serviço `setup` baixa os modelos `bge-m3` e `qwen2.5:3b`, baixa a documentação do FastAPI 0.162.0 e cria o índice (1626 trechos). Isso leva vários minutos. Nas próximas vezes ele pula o que já existe.

Quando as mensagens pararem e a API e a interface estiverem de pé:

- Interface: http://localhost:8501
- API: http://localhost:8000 (documentação interativa em `/docs`)
- Saúde: http://localhost:8000/health

Para parar: `Ctrl+C` no terminal e, se quiser limpar, `docker compose down`. Para apagar também os dados baixados: `docker compose down -v`.

## Variáveis de ambiente

Valores padrão em `.env.example`. Não há chaves.

| Variável | Padrão no Docker | Função |
| --- | --- | --- |
| `OLLAMA_URL` | `http://ollama:11434` | Onde estão os modelos |
| `QDRANT_URL` | `http://qdrant:6333` | Onde está o banco vetorial |
| `GEN_MODEL` | `qwen2.5:3b` | Modelo que escreve as respostas |
| `EMBED_MODEL` | `bge-m3` | Modelo de embeddings |
| `CORPUS_DIR` | `data/raw/corpus` | Pasta do corpus limpo (opcional) |
| `CHUNK_STRATEGY` | `structure` | Como dividir os textos (opcional) |
| `API_URL` | `http://api:8000` | Endereço da API usado pela interface |

Para mudar algo, copie `.env.example` para `.env` (o `.env` não vai para o Git).

## Sem Docker (desenvolvimento)

Requer Python 3.12 ou superior, Ollama e Qdrant rodando no computador.

```bash
python -m venv .venv
source .venv/bin/activate        # no Windows: .venv\Scripts\activate
pip install -r requirements-dev.txt -r requirements-ui.txt
pytest
cd src
python -m app.setup              # modelos, corpus e índice
uvicorn app.main:app --reload
streamlit run app/ui.py
```

## Problemas comuns

| Sintoma | Causa provável | O que fazer |
| --- | --- | --- |
| Erro 503 ao perguntar | Ollama ou Qdrant ainda não terminaram de subir, ou o índice não foi criado | Espere o `setup` terminar e olhe os logs: `docker compose logs setup` |
| Primeira resposta muito lenta | O modelo está carregando na memória | Espere; as próximas são mais rápidas (cerca de 15 a 60 s em CPU) |
| Porta já em uso | Outro programa usa 8000, 8501 ou 6333 | Feche o programa ou mude a porta em `docker-compose.yml` |
