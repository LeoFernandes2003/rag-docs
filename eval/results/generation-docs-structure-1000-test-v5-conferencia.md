# Conferência manual das respostas

Marque `[x]` se a resposta está correta.

## q002: Como desativar os logs de exceção do OpenTelemetry no FastAPI?
- Esperado: Definindo `logs` como `False`.
- Sistema (respondeu): Para desativar os logs de exceção do OpenTelemetry no FastAPI, você pode definir a propriedade `logs` para `False` em seu código. Fontes: [1]
- [x] correta

## q004: Como o FastAPI distingue parâmetros de caminho de parâmetros de consulta?
- Esperado: Ele percebe que `item_id` é parâmetro de caminho e que `q`, que não está no caminho, é parâmetro de consulta.
- Sistema (respondeu): O FastAPI distingue parâmetros de caminho de parâmetros de consulta através do nome dos parâmetros declarados. Você pode declarar tanto parâmetros de caminho quanto parâmetros de consulta simultaneamente, e o FastAPI sabe distinguir entre eles devido ao nome dos parâmetros. Por exemplo, em um endpoint como `/users/{user_id}/items/{item_id}`, `user_id` é um parâmetro de caminho e `item_id` é um parâmetro de consulta. Fontes: [1]
- [ ] correta

## q005: Como sobrescrever uma dependência em testes?
- Esperado: Usa-se como chave a dependência original (uma função) e como valor a função que a substitui.
- Sistema (respondeu): Para sobrescrever uma dependência em testes, você pode usar o atributo `app.dependency_overrides` de seu aplicativo FastAPI. Você define uma nova função como valor para a chave que é a dependência original que deseja substituir. Isso permite que você forneça uma nova dependência que será usada apenas durante os testes. Fontes: [1] [3]
- [x] correta

## q007: O que se pode definir sobre webhooks usando OpenAPI no FastAPI?
- Esperado: Os nomes dos webhooks, os tipos de operações HTTP que o app pode enviar e os corpos das requisições.
- Sistema (respondeu): O FastAPI permite definir o nome dos webhooks, os tipos de operações HTTP que o aplicativo pode enviar (como POST, PUT, etc.) e os corpos de solicitação que o aplicativo enviará usando OpenAPI. Fontes: [1]
- [x] correta

## q009: De onde vêm a maioria dos middlewares disponíveis em `fastapi.middleware`?
- Esperado: Vêm diretamente do Starlette; o FastAPI os oferece por conveniência.
- Sistema (respondeu): Maioria dos middlewares disponíveis em `fastapi.middleware` vêm diretamente da Starlette. Fontes: [1] [2]
- [x] correta

## q010: Por que o código de saída de uma dependência precisa rodar antes das subdependências?
- Esperado: Porque a dependência pode precisar ainda usar as subdependências durante o seu código de saída.
- Sistema (respondeu): O código de saída de uma dependência precisa rodar antes das subdependências para garantir que a dependência ainda possa usar as subdependências durante seu próprio código de saída. Isso é importante porque a dependência pode precisar de acesso a valores ou estado gerenciados pelas subdependências durante a execução de seu próprio código de saída. Fontes: [1]
- [x] correta

## q012: Para que tipos de dados o streaming de JSON Lines pode ser usado?
- Esperado: Para transmitir dados de um serviço de LLM de IA, logs, telemetria ou outros dados estruturados em itens JSON.
- Sistema (respondeu): Streaming de JSON Lines pode ser usado para enviar sequências de dados estruturados como JSON. É especialmente útil quando você precisa enviar dados em uma sequência, como uma série de objetos JSON separados por linhas, sem esperar que todos os dados estejam prontos antes de começar a enviar. Fontes: [3] [4]
- [ ] correta

## q014: A que se parece a estrutura de um atributo de modelo declarado com `Field`?
- Esperado: Ao parâmetro de uma função de operação de rota, com `Field` no lugar de `Path`, `Query` e `Body`.
- Sistema (respondeu): A estrutura de um atributo de modelo declarado com `Field` é semelhante à estrutura de um parâmetro de operação de rota, onde `Field` substitui `Path`, `Query` e `Body`. Fontes: [1]
- [x] correta

## q015: O que o sistema de Injeção de Dependências faz com a árvore hierárquica de dependências?
- Esperado: Resolve todas as dependências (e subdependências) e injeta os resultados em cada etapa.
- Sistema (respondeu): O sistema de Injeção de Dependências cria e organiza uma árvore hierárquica de dependências, onde cada função ou objeto dependente pode ter dependências próprias. O sistema FastAPI cuida de resolver todas essas dependências e fornecer (injetar) os resultados em cada etapa, garantindo que a árvore hierárquica de dependências seja construída de forma eficiente e eficaz. Fontes: [1] [2] [3] [4] [5]
- [x] correta

## q017: Qual a diferença entre a `HTTPException` do FastAPI e a do Starlette?
- Esperado: A do FastAPI aceita qualquer dado serializável em JSON no campo `detail`; a do Starlette só aceita strings.
- Sistema (respondeu): A principal diferença entre a `HTTPException` do FastAPI e a do Starlette é que o FastAPI permite que qualquer dado JSON-able seja usado como detalhe (`detail`) da exceção, enquanto o Starlette só aceita strings para esse campo. Fontes: [1]
- [x] correta

## q019: Qual a vantagem de guardar as senhas com hash caso o banco de dados seja roubado?
- Esperado: O ladrão não conseguirá usar as mesmas senhas em outro sistema, o que seria perigoso porque muitos usuários repetem a senha.
- Sistema (respondeu): Guardar as senhas com hash, mesmo que o banco de dados seja roubado, garante que os ladrões não possam usar essas senhas em outros sistemas. Isso é porque os ladrões só terão os hashes das senhas, e não as senhas em formato de texto plano. Portanto, eles não poderão tentar usar essas mesmas senhas em outros sistemas, o que seria perigoso porque muitas pessoas usam a mesma senha em vários lugares. Fontes: [1] [2] [3]
- [x] correta

## q020: De onde importar `Body`, `Query`, `Form` etc. para usar com modelos Pydantic v1 durante a migração?
- Esperado: De `fastapi.temp_pydantic_v1_params`.
- Sistema (respondeu): Para usar `Body`, `Query`, `Form` etc. com modelos Pydantic v1 durante a migração, você deve importar essas funções do pacote `fastapi.temp_pydantic_v1_params`. Fontes: [1]
- [x] correta

## q022: Por que combinar respostas predefinidas com respostas específicas de cada operação de rota?
- Esperado: Porque algumas respostas valem para muitas operações de rota, mas cada operação pode precisar de respostas customizadas além delas.
- Sistema (respondeu): Por que combinar respostas predefinidas com respostas específicas de cada operação de rota? Combinar respostas predefinidas com respostas específicas de cada operação de rota permite que você reutilize as respostas padrão para cenários comuns, enquanto ainda oferece a flexibilidade de personalizar as respostas para casos mais específicos. Isso é útil para evitar duplicar código e manter a consistência na documentação. Fontes: [1] [3] [4]
- [x] correta

## q024: Por que não dá para declarar campos `Body` em JSON junto com parâmetros `File` e `Form`?
- Esperado: Porque a requisição terá o corpo codificado como `multipart/form-data` em vez de `application/json`.
- Sistema (respondeu): Por que não dá para declarar campos `Body` em JSON junto com parâmetros `File` e `Form`? Isso não é permitido por causa da natureza do protocolo HTTP. O FastAPI segue as regras do protocolo HTTP, que determina que os campos `File` e `Form` são enviados como `multipart/form-data`, enquanto os campos `Body` em JSON são enviados como `application/json`. Fontes: [1] [2]
- [x] correta

## q025: As funções `fake_password_hasher` e `fake_save_user` oferecem segurança real?
- Esperado: Não. Servem só para demonstrar um possível fluxo dos dados.
- Sistema (respondeu): As funções `fake_password_hasher` e `fake_save_user` não oferecem segurança real. Elas são apenas usadas para demonstrar um possível fluxo de dados, mas não fornecem segurança de verdade. Fontes: [1]
- [x] correta

## q027: O que o FastAPI diz a quem se sente perdido com expressões regulares?
- Esperado: Que não se preocupe: é um tema difícil para muita gente e dá para fazer muita coisa sem usar expressões regulares ainda.
- Sistema (respondeu): Se você se sente perdido com as ideias de **"expressões regulares"**, não se preocupe. Elas são um tópico difícil para muitas pessoas. Você ainda pode fazer muita coisa sem precisar de expressões regulares. Fontes: [1]
- [x] correta

## q029: Que status HTTP as utilidades de segurança retornavam, antes do FastAPI 0.122.0, após uma falha de autenticação?
- Esperado: 403 Forbidden.
- Sistema (respondeu): Resposta: Antes do FastAPI 0.122.0, as utilidades de segurança retornavam o status HTTP `403 Forbidden` após uma falha de autenticação. Fontes: [1]
- [x] correta

## q030: No exemplo do restaurante de hambúrguer, por que o trabalho com o caixa fica "em pausa"?
- Esperado: Porque é preciso esperar os hambúrgueres ficarem prontos.
- Sistema (respondeu): No exemplo do restaurante de hambúrguer, o trabalho com o caixa fica "em pausa" porque você ainda não tem seus hambúrgueres. Ainda está esperando 🕙 para que eles estejam prontos. Portanto, você não pode continuar processando a conta ou qualquer outra tarefa até que os hambúrgueres estejam disponíveis. Fontes: [1] [3]
- [x] correta

## q032: O que o desenvolvedor passa a controlar ao usar `StreamingResponse`?
- Esperado: A liberdade e a responsabilidade de produzir e codificar os bytes exatamente como devem ser enviados, independente das anotações de tipo.
- Sistema (respondeu): O desenvolvedor passa a controlar a forma como os dados são produzidos e codificados exatamente como ele precisa ser enviado, independentemente das anotações de tipo. Fontes: [1] [4]
- [x] correta

## q034: Por que os benchmarks costumam não refletir bem as ferramentas?
- Esperado: Porque quanto mais simples o problema, melhor o desempenho, e a maioria dos benchmarks não testa os recursos adicionais da ferramenta.
- Sistema (respondeu): Benchmark costumam não refletir bem as ferramentas porque esses testes geralmente focam em desempenho básico, esquecendo de testar as funcionalidades adicionais que as ferramentas podem oferecer. Fontes: [1] [5]
- [x] correta

## q035: A que a palavra "servidor" costuma se referir?
- Esperado: Tanto ao computador remoto ou na nuvem (máquina física ou virtual) quanto ao programa que roda nele, como o Uvicorn.
- Sistema (respondeu): A palavra "servidor" costuma se referir tanto ao computador remoto (físico ou virtual) quanto ao programa que está rodando nesse computador. Fontes: [1]
- [x] correta

## q037: O que vale ao adicionar dependências globais a toda a aplicação?
- Esperado: As mesmas ideias de adicionar `dependencies` nos decoradores de operação de rota, mas aplicadas a todas as operações de rota do app.
- Sistema (respondeu): Adicionar dependências globais a toda a aplicação permite que você crie dependências que serão aplicadas a todos os operadores de caminho da aplicação. Isso é útil para cenários onde você deseja que uma dependência seja usada em todas as partes da aplicação, não apenas em um determinado operador de caminho. Fontes: [1] [3]
- [x] correta

## q039: É possível montar uma subaplicação usando também um proxy com `root_path`?
- Esperado: Sim, dá para fazer normalmente.
- Sistema (respondeu): Sim, é possível montar uma subaplicação usando um proxy com `root_path`. Você pode configurar o servidor com `fastapi run --root-path` e FastAPI cuidará da comunicação do caminho de montagem da subaplicação usando a mecânica do ASGI, conforme descrito no tópico [Behind a Proxy](behind-a-proxy.md). Fontes: [1]
- [x] correta

## q040: Quem deve cuidar do HTTPS na frente da aplicação na maioria dos casos?
- Esperado: Um "proxy de terminação"; o provedor pode fazer isso ou é preciso configurá-lo por conta própria.
- Sistema (respondeu): Na maioria dos casos, é o proxy quem deve cuidar do HTTPS na frente da aplicação. Fontes: [1] [2]
- [x] correta

## q042: Como enviar notificações push para celulares usando o Firebase?
- Esperado: recusar (a documentação não tem a resposta)
- Sistema (modelo_recusou): NÃO ENCONTREI NA DOCUMENTAÇÃO.
- [x] correta

## q044: Como indexar documentos e fazer buscas com Elasticsearch?
- Esperado: recusar (a documentação não tem a resposta)
- Sistema (modelo_recusou): NÃO ENCONTREI NA DOCUMENTAÇÃO.
- [x] correta

## q046: Como criar o aplicativo móvel em Flutter que consome a API?
- Esperado: recusar (a documentação não tem a resposta)
- Sistema (modelo_recusou): NÃO ENCONTREI NA DOCUMENTAÇÃO.
- [x] correta

## q048: Como carregar um modelo do scikit-learn e servir previsões?
- Esperado: recusar (a documentação não tem a resposta)
- Sistema (modelo_recusou): NÃO ENCONTREI NA DOCUMENTAÇÃO.
- [x] correta

## q049: Como limitar a taxa de requisições com a biblioteca SlowAPI?
- Esperado: recusar (a documentação não tem a resposta)
- Sistema (modelo_recusou): NÃO ENCONTREI NA DOCUMENTAÇÃO.
- [x] correta

## q050: Como enviar e-mails com SMTP usando smtplib ou SendGrid?
- Esperado: recusar (a documentação não tem a resposta)
- Sistema (modelo_recusou): NÃO ENCONTREI NA DOCUMENTAÇÃO.
- [x] correta
