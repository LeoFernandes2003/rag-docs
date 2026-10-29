# Conferência manual das respostas

Marque `[x]` se a resposta está correta.

## q001: O que o FastAPI gera automaticamente com as descrições de toda a sua API?
- Esperado: Um schema JSON (OpenAPI) com as descrições de toda a API.
- Sistema (respondeu): O FastAPI gera automaticamente um JSON (esquema) com as descrições de toda a sua API, chamado `openapi.json`, que pode ser acessado diretamente em [http://127.0.0.1:8000/openapi.json](http://127.0.0.1:8000/openapi.json). Fontes: [2]
- [x] correta

## q003: O que usar no lugar da barra vertical (|) quando ela não pode ser usada, por exemplo em `response_model=`?
- Esperado: Usar `Union` do módulo `typing`.
- Sistema (respondeu): O lugar da barra vertical (|) quando ela não pode ser usada, por exemplo em `response_model=`, é a utilização da `Union` do pacote `typing`. Fontes: [1]
- [ x] correta

## q006: Por que existe `fastapi.staticfiles` se o código vem do Starlette?
- Esperado: É uma conveniência para o desenvolvedor; o código vem diretamente do Starlette.
- Sistema (respondeu): Por que existe `fastapi.staticfiles` se o código vem do Starlette? O `fastapi.staticfiles` é fornecido como uma conveniência para o desenvolvedor, mesmo que o código venha diretamente do Starlette. Essa conveniência permite que o FastAPI utilize facilmente as funcionalidades de `starlette.staticfiles` sem a necessidade de importar diretamente do Starlette. Fontes: [1] [2]
- [x ] correta

## q008: O que diferencia o OAuth 1 do OAuth2?
- Esperado: O OAuth 1 era bem diferente e mais complexo, pois incluía especificações diretas de como criptografar a comunicação.
- Sistema (respondeu): OAuth 1 é muito diferente do OAuth2. OAuth 1 é muito mais complexo e especifica diretamente como criptografar as comunicações. Já OAuth2 não especifica como criptografar as comunicações, ele espera que você tenha seu aplicativo servido com HTTPS. Fontes: [1]
- [ x] correta

## q011: Quando é útil usar funções assíncronas nos testes?
- Esperado: Por exemplo, ao consultar o banco de dados de forma assíncrona para verificar se o backend gravou os dados corretos.
- Sistema (respondeu): Quando é útil usar funções assíncronas nos testes é quando você precisa realizar operações assíncronas, como consultar um banco de dados, em seus testes. Isso pode ser útil, por exemplo, quando você deseja testar a solicitação de um aplicativo FastAPI e, em seguida, verificar se o backend escreveu corretamente os dados no banco de dados, usando uma biblioteca de banco de dados assíncrona. Fontes: [1]
- [ x] correta

## q013: Mesmo que a função retorne mais dados, o que o response model garante na resposta?
- Esperado: Que a resposta inclua só os campos declarados no response model, pois o FastAPI continua filtrando os dados.
- Sistema (respondeu): Mesmo que a função retorne mais dados, o response model garante que a resposta incluirá apenas os campos declarados nele. Fontes: [1]
- [ x] correta

## q016: No exemplo de CORS, por que o navegador assume a porta 80 para o backend?
- Esperado: Porque a porta não foi especificada em `http://localhost`, então o navegador assume a porta padrão 80.
- Sistema (respondeu): No exemplo de CORS, o navegador assume a porta 80 para o backend porque o usuário não especificou uma porta para o backend. Quando não é especificado, o navegador assume a porta padrão, que é 80. Fontes: [1]
- [ x] correta

## q018: Que outro tipo o `status_code` pode receber, além de um número?
- Esperado: Um `IntEnum`, como o `http.HTTPStatus` do Python.
- Sistema (respondeu): O `status_code` pode receber também um objeto `IntEnum`, como o Python's `http.HTTPStatus`. Fontes: [2]
- [ x] correta

## q021: Por que é preciso usar `Form` explicitamente para declarar corpos de formulário?
- Esperado: Sem ele, os parâmetros seriam interpretados como parâmetros de consulta ou do corpo (JSON).
- Sistema (respondeu): Por que é preciso usar `Form` explicitamente para declarar corpos de formulário? É necessário usar `Form` explicitamente porque sem ele, os parâmetros seriam interpretados como parâmetros de consulta ou parâmetros de corpo (JSON). Fontes: [1]
- [ x] correta

## q023: Por que a resposta "Incorrect username or password" leva alguns microssegundos extras no exemplo de HTTP Basic?
- Esperado: Porque o Python precisa comparar a string inteira antes de perceber que as duas são diferentes.
- Sistema (respondeu): Por que a resposta "Incorrect username or password" leva alguns microssegundos extras no exemplo de HTTP Basic, é porque o servidor precisa comparar completamente o `stanleyjobso` em ambos `stanleyjobsox` e `stanleyjobson` antes de reconhecer que ambos os strings não são iguais. Isso leva um tempo adicional para responder "Incorrect username or password". Fontes: [1]
- [ x] correta

## q026: Que informações o FastAPI extrai da resposta temporária?
- Esperado: Os headers (também cookies e status code), que vão para a resposta final.
- Sistema (respondeu): FastAPI extraí todas as informações da resposta temporária, incluindo o status code, cookies e cabeçalhos, e as coloca na resposta final que contém o valor retornado, filtrado pelo `response_model` que você declarou. Fontes: [1]
- [ x] correta

## q028: Como adicionar dados extras ao JSON Schema gerado de um modelo, incluindo exemplos?
- Esperado: Definindo `json_schema_extra` com um `dict` com os dados adicionais, incluindo `examples`.
- Sistema (respondeu): Para adicionar dados extras ao JSON Schema gerado de um modelo, incluindo exemplos, você pode usar a propriedade `model_config` que aceita um dicionário. Você pode adicionar `json_schema_extra` com um dicionário contendo qualquer dado adicional que deseja mostrar no JSON Schema gerado, incluindo `examples`. Exemplos de como fazer isso: 1. Você pode adicionar `examples` diretamente ao Pydantic modelo, usando `schema_extra` ou `Field(examples=["something"])`. Esses exemplos são adicionados ao JSON Schema para esse Pydantic modelo. 2. Você também pode adicionar `examples` ao `model_config` do Pydantic modelo, usando `json_schema_extra`. Esses exemplos são adicionados ao JSON Schema do Pydantic modelo, que é incluído no OpenAPI da sua API e usado nos documentos UI. Fontes: [1] [3]
- [ x] correta

## q031: O que o FastAPI usa por baixo para converter dataclasses padrão?
- Esperado: Usa o Pydantic para converter as dataclasses padrão para a versão de dataclasses do próprio Pydantic.
- Sistema (respondeu): O FastAPI usa Pydantic por baixo para converter dataclasses padrão. Fontes: [1]
- [ x] correta

## q033: O que mostra, no editor, os benefícios do FastAPI?
- Esperado: Ver quão pouco código é preciso escrever, as verificações de tipo, o autocompletar etc.
- Sistema (respondeu): O editor mostra os benefícios do FastAPI, como a flexibilidade fornecida por modelos Pydantic, suporte de editor (completude em todo lugar), conversão de dados (conversão / serialização), validação de dados, documentação de esquema e gerenciamento de docs automatizados. Fontes: [1]
- [ ] correta

## q036: Como a fase de desenvolvimento se contrapõe à de implantação?
- Esperado: No desenvolvimento se muda o código o tempo todo, quebrando e consertando, parando e reiniciando o servidor de desenvolvimento.
- Sistema (respondeu): Na fase de desenvolvimento, você está constantemente alterando o código, quebrando-o e corrigindo erros, interrompendo e reiniciando o servidor de desenvolvimento. Contrariamente, a fase de implantação envolve fazer os passos necessários para tornar o aplicativo **disponível para os usuários**. Para um API web, isso geralmente envolve colocá-lo em um **servidor remoto** com um programa de servidor que oferece desempenho, estabilidade e outras características, de modo que os usuários possam acessar o aplicativo de forma eficiente e sem interrupções ou problemas. Fontes: [1]
- [ x] correta

## q038: O que é `app.routes`?
- Esperado: Uma árvore de rotas de nível mais baixo, que pode incluir candidatas a rota usadas internamente para routers incluídos, e não só objetos `APIRoute` finais.
- Sistema (respondeu): `app.routes` é uma árvore de rotas mais baixa que pode conter definições de rota e roteadores incluídos, e não deve ser dependente de uma lista plana de operações de rota final. Fontes: [1]
- [ x] correta

## q041: Como integrar o FastAPI com a API de pagamentos da Stripe?
- Esperado: recusar (a documentação não tem a resposta)
- Sistema (modelo_recusou): NÃO ENCONTREI NA DOCUMENTAÇÃO.
- [ x] correta

## q043: Como gerar relatórios em PDF com ReportLab em uma rota?
- Esperado: recusar (a documentação não tem a resposta)
- Sistema (modelo_recusou): NÃO ENCONTREI NA DOCUMENTAÇÃO.
- [ x] correta

## q045: Como consumir e publicar mensagens em tópicos do Kafka?
- Esperado: recusar (a documentação não tem a resposta)
- Sistema (modelo_recusou): NÃO ENCONTREI NA DOCUMENTAÇÃO.
- [ x] correta

## q047: Como ler um CSV com pandas e devolver o resultado na API?
- Esperado: recusar (a documentação não tem a resposta)
- Sistema (modelo_recusou): NÃO ENCONTREI NA DOCUMENTAÇÃO.
- [ x] correta
