# 8. Segurança, privacidade e limitações

## Segurança

- **Sem segredos:** o sistema não usa chaves de API. O `.env` está no `.gitignore`.
- **Execução local:** modelos, banco e API rodam no computador do usuário. Nenhuma pergunta é enviada a serviços externos.
- **Entrada limitada:** a API aceita perguntas de 3 a 500 caracteres.
- **Dependências:** as imagens são fixadas: `qdrant/qdrant:v1.20.0` e `ollama/ollama` pelo digest da versão testada (veja `docker-compose.yml`). Assim uma atualização futura das imagens não muda o comportamento do sistema.
- **Portas:** as portas 8000, 8501, 6333 e 11435 ficam abertas no computador. A API não tem autenticação e não deve ser exposta na internet.
- **Injeção de instruções no corpus:** o prompt manda usar só os trechos, mas um texto malicioso dentro da documentação poderia tentar influenciar o modelo. O corpus aqui é uma documentação oficial fixada em versão.

## Privacidade e LGPD

- O corpus é documentação pública (licença MIT). As perguntas de avaliação são sintéticas.
- O sistema não grava perguntas nem respostas em arquivos próprios, além dos arquivos de avaliação gerados pelos scripts. A API escreve em log (saída padrão) a pergunta, a decisão e a resposta; o Docker guarda esse log no computador do usuário e ele some ao recriar o contêiner (`docker compose logs -t api`).
- Nenhum dado pessoal real deve ser usado em perguntas, logs, vídeos ou capturas de tela.

## O que o sistema não faz

- Não responde sobre assuntos fora da documentação do FastAPI 0.162.0 (ele recusa).
- Não acompanha novas versões da documentação.
- Não mantém conversa: cada pergunta é independente.
- Não garante que a resposta esteja correta, só que ela foi gerada a partir dos trechos mostrados. O usuário deve conferir as fontes.

## Limitações conhecidas

| Limitação | Efeito | Onde está registrada |
| --- | --- | --- |
| Modelo pequeno (3 bilhões de parâmetros) | Respostas às vezes incompletas, recusa de perguntas respondíveis ou resposta só com `[n]` | `eval/results/README.md` |
| Tradução da pergunta imperfeita | Busca por palavras pode falhar (q026) ou ganhar palavras extras (q011, q023) | `eval/results/README.md` |
| Só 16 perguntas de desenvolvimento | Diferenças de uma pergunta (6,25 pontos) estão no ruído | `eval/results/README.md` |
| Só 24 perguntas de teste com resposta e 6 sem | Uma pergunta vale 4,2 pontos (16,7 nas sem resposta); o baseline (0,875) e o sistema final (0,833) não podem ser separados | `eval/results/README.md` |
| Teste usado uma só vez | A variação entre execuções não foi medida | `eval/results/README.md` |
| Conferência manual por uma só pessoa | O autor leu cada resposta e marcou; antes de marcar leu uma segunda opinião de IA (registrada em `PROMPTS.md`) | `eval/results/README.md` |
| Perguntas sem resposta com termos ausentes do corpus | São mais fáceis de recusar do que perguntas sobre assuntos vizinhos; o caso difícil não foi medido | `eval/results/README.md` |
| Perguntas escritas a partir do corpus | Favorecem a busca por palavras | `eval/results/README.md` |
| Métrica rígida | Achar o arquivo certo mas não o trecho exato conta como erro; no teste, 5 respostas com fonte errada, 3 delas corretas no conteúdo | `eval/results/README.md` |
| Citação válida não é citação correta | O sistema garante que o trecho citado existe, não que seja o usado (q030) | `evidencias/analise-de-falhas.md` |
| Resposta sem citação válida é mostrada | Depois da nova tentativa, uma resposta com texto mas sem nenhum `[n]` válido ainda é devolvida, sem fontes; no teste final todas as respostas tiveram citação válida | `src/app/rag/pipeline.py` |
| Resposta errada com fonte certa | O arquivo certo foi citado, mas o modelo errou a interpretação (q004) | `evidencias/analise-de-falhas.md` |
| Arquivos duplicados no corpus | Podem ocupar posições da busca | [corpus.md](corpus.md) |
| Licença do Qwen | Uso comercial não permitido sem acordo | [dados-e-modelos.md](dados-e-modelos.md) |
| Tempo de resposta | Em CPU, média de 25 s por resposta e máximo de 38 s (30 perguntas do teste); sem GPU | `eval/results/README.md` |
| Recusa não baseada em nota | A nota de similaridade não separa perguntas com e sem resposta, então a recusa depende do modelo | [decisoes.md](decisoes.md) |
