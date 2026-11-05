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
- O sistema não guarda perguntas nem respostas em disco além dos arquivos de avaliação gerados pelos scripts.
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
| Perguntas escritas a partir do corpus | Favorecem a busca por palavras | `eval/results/README.md` |
| Métrica rígida | Achar o arquivo certo mas não o trecho exato conta como erro | `eval/results/README.md` |
| Arquivos duplicados no corpus | Podem ocupar posições da busca | [corpus.md](corpus.md) |
| Licença do Qwen | Uso comercial não permitido sem acordo | [dados-e-modelos.md](dados-e-modelos.md) |
| Tempo de resposta | De cerca de 15 a 60 s em CPU | `README.md` |
| Recusa não baseada em nota | A nota de similaridade não separa perguntas com e sem resposta, então a recusa depende do modelo | [decisoes.md](decisoes.md) |
