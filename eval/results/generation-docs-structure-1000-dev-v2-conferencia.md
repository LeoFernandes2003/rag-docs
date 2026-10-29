# Conferência manual das respostas

Marque `[x]` se a resposta está correta.

## q001: O que o FastAPI gera automaticamente com as descrições de toda a sua API?
- Esperado: Um schema JSON (OpenAPI) com as descrições de toda a API.
- Sistema (respondeu): Use o parâmetro X para fazer Y [2]
- [ ] correta

## q003: O que usar no lugar da barra vertical (|) quando ela não pode ser usada, por exemplo em `response_model=`?
- Esperado: Usar `Union` do módulo `typing`.
- Sistema (respondeu): Use o parâmetro `Union` para fazer isso [1].
- [ ] correta

## q006: Por que existe `fastapi.staticfiles` se o código vem do Starlette?
- Esperado: É uma conveniência para o desenvolvedor; o código vem diretamente do Starlette.
- Sistema (respondeu): Use o parâmetro fastapi.staticfiles para usar os arquivos estáticos [2]. [3]
- [ ] correta

## q008: O que diferencia o OAuth 1 do OAuth2?
- Esperado: O OAuth 1 era bem diferente e mais complexo, pois incluía especificações diretas de como criptografar a comunicação.
- Sistema (respondeu): O OAuth 1 é muito diferente do OAuth2 e é mais complexo, pois especifica diretamente como encriptar a comunicação [1]. O OAuth2, por outro lado, não especifica como encriptar a comunicação, apenas espera que o seu aplicativo seja servido com HTTPS [2].
- [ ] correta

## q011: Quando é útil usar funções assíncronas nos testes?
- Esperado: Por exemplo, ao consultar o banco de dados de forma assíncrona para verificar se o backend gravou os dados corretos.
- Sistema (respondeu): Use o parâmetro X para fazer Y [1]
- [ ] correta

## q013: Mesmo que a função retorne mais dados, o que o response model garante na resposta?
- Esperado: Que a resposta inclua só os campos declarados no response model, pois o FastAPI continua filtrando os dados.
- Sistema (respondeu): [1] O response model garante que a resposta incluirá apenas os campos declarados nele, mesmo que a função retorne mais dados.
- [ ] correta

## q016: No exemplo de CORS, por que o navegador assume a porta 80 para o backend?
- Esperado: Porque a porta não foi especificada em `http://localhost`, então o navegador assume a porta padrão 80.
- Sistema (respondeu): Use o parâmetro `allow_origins` para especificar as origens permitidas [1].
- [ ] correta

## q018: Que outro tipo o `status_code` pode receber, além de um número?
- Esperado: Um `IntEnum`, como o `http.HTTPStatus` do Python.
- Sistema (modelo_recusou): NÃO ENCONTREI NA DOCUMENTAÇÃO.
- [ ] correta

## q021: Por que é preciso usar `Form` explicitamente para declarar corpos de formulário?
- Esperado: Sem ele, os parâmetros seriam interpretados como parâmetros de consulta ou do corpo (JSON).
- Sistema (respondeu): [1] É necessário usar `Form` explicitamente para declarar corpos de formulário porque sem ele, os parâmetros seriam interpretados como parâmetros de consulta ou parâmetros de corpo (JSON).
- [ ] correta

## q023: Por que a resposta "Incorrect username or password" leva alguns microssegundos extras no exemplo de HTTP Basic?
- Esperado: Porque o Python precisa comparar a string inteira antes de perceber que as duas são diferentes.
- Sistema (respondeu): Use o parâmetro [1] para entender por que a resposta "Incorrect username or password" leva alguns microssegundos extras no exemplo de HTTP Basic. [1] explica que o servidor precisa comparar todo o `stanleyjobso` em ambas as `stanleyjobsox` e `stanleyjobson` antes de perceber que ambos os strings não são iguais. Isso leva alguns microssegundos a mais para responder "Incorrect username or password". [2] destaca que, ao notar que o servidor demorou alguns microssegundos a enviar a resposta "Incorrect username or password", os atacantes sabem que eles obtiveram algo certo, algumas letras iniciais estavam certas. Eles podem então tentar novamente, sabendo que é provavelmente algo mais próximo de `stanleyjobsox` do que de `johndoe`.
- [ ] correta

## q026: Que informações o FastAPI extrai da resposta temporária?
- Esperado: Os headers (também cookies e status code), que vão para a resposta final.
- Sistema (respondeu): [1]
- [ ] correta

## q028: Como adicionar dados extras ao JSON Schema gerado de um modelo, incluindo exemplos?
- Esperado: Definindo `json_schema_extra` com um `dict` com os dados adicionais, incluindo `examples`.
- Sistema (respondeu): [1] Você pode usar o atributo `model_config` que toma um `dict` como descrito na [Pydantic's docs: Configuration](https://pydantic.dev/docs/validation/latest/api/pydantic/config/). Você pode definir `"json_schema_extra"` com um `dict` contendo qualquer dado adicional que gostaria de mostrar no JSON Schema gerado, incluindo `examples`. **Dica** Você pode usar o mesmo método para extender o JSON Schema e adicionar seu próprio extra info personalizado. Por exemplo, você pode usá-lo para adicionar metadados para uma interface de usuário do usuário frontend, etc. **Nota** OpenAPI 3.1.0 (usado desde FastAPI 0.99.0) adicionou suporte para `examples`, que faz parte da **JSON Schema** padrão. [2] Você pode declarar informações extra com `json_schema_extra` em `Field`, `Query`, `Body`, etc. E isso será incluído no JSON Schema gerado. Você aprenderá mais sobre como adicionar informações extra mais tarde nos docs, quando aprender a declarar exemplos. **Aviso** Chaves extras passadas em `json_schema_extra` também estarão presentes no resultado OpenAPI para sua aplicação. Ao usar chaves extras, você pode não estar seguro de que elas estarão presentes no OpenAPI, pois não são necessariamente parte do OpenAPI. [3] Você pode declarar exemplos de dados que seu app pode receber. Aqui estão algumas maneiras de fazer isso. **Extra JSON Schema data in Pydantic models** Você pode declarar `examples` para um modelo Pydantic que será adicionado ao JSON Schema gerado. ```python from fastapi import FastAPI from pydantic import BaseModel app = FastAPI() class Item(BaseModel): name: str description: str | None = None price: float tax: float | None = None model_config = { "json_schema_extra": { "examples": [ { "name": "Foo", "description": "A very nice Item", "price": 35.4, "tax": 3.2, } ] } } @app.put("/items/{item_id}") async def update_item(item_id: int, item: Item): results = {"item_id": item_id, "item": item} return results ``` [4] Quando você adiciona `examples` dentro de um modelo Pydantic, usando `schema_extra` ou `Field(examples=["something"])` que exemplo é adicionado ao **JSON Schema** para aquele modelo Pydantic. E aquele **JSON Schema** do modelo Pydantic é incluído no **OpenAPI** de sua API, e então é usado na UI dos docs. Em versões do FastAPI antes de 0.99.0 (0.99.0 e acima usam a versão mais nova do OpenAPI 3.1.0) quando você usou `example` ou `examples` com qualquer dos outros utilitários (`Query()`, `Body()`, etc.) aqueles exemplos não foram adicionados ao JSON Schema que descreve aqueles dados (nem mesmo ao OpenAPI próprio versão de JSON Schema), eles foram adicionados diretamente ao *declaração de operação da rota* no OpenAPI (fora dos partes do OpenAPI que usam JSON Schema). Mas agora que o FastAPI 0.99.0 e acima usa o OpenAPI 3.1.0, que usa JSON Schema 2020-12, e o Swagger UI 5.0.0 e acima, tudo está mais consistente e os exemplos são incluídos no JSON Schema. [5] Quando você faz isso, os exemplos estarão presentes no JSON Schema interno para aquele dado de corpo. No entanto, ao tempo de escrever essa resposta (26 de agosto de 2023), o Swagger UI, o ferramenta em charge de mostrar a UI dos docs, não suporta mostrar múltiplos exemplos para os dados no **JSON Schema**. Mas leia abaixo para uma solução de trabalho.
- [ ] correta

## q031: O que o FastAPI usa por baixo para converter dataclasses padrão?
- Esperado: Usa o Pydantic para converter as dataclasses padrão para a versão de dataclasses do próprio Pydantic.
- Sistema (respondeu): [1]
- [ ] correta

## q033: O que mostra, no editor, os benefícios do FastAPI?
- Esperado: Ver quão pouco código é preciso escrever, as verificações de tipo, o autocompletar etc.
- Sistema (respondeu): Use o parâmetro X para fazer Y [2]
- [ ] correta

## q036: Como a fase de desenvolvimento se contrapõe à de implantação?
- Esperado: No desenvolvimento se muda o código o tempo todo, quebrando e consertando, parando e reiniciando o servidor de desenvolvimento.
- Sistema (respondeu): NÃO ENCONTROI NA DOCUMENTAÇÃO. [1]
- [ ] correta

## q038: O que é `app.routes`?
- Esperado: Uma árvore de rotas de nível mais baixo, que pode incluir candidatas a rota usadas internamente para routers incluídos, e não só objetos `APIRoute` finais.
- Sistema (respondeu): O parâmetro `app.routes` é uma árvore de rotas mais baixa que pode conter definições de rota e roteadores incluídos, e não deve ser dependente de uma lista plana de operações de rota final [1].
- [ ] correta

## q041: Como integrar o FastAPI com a API de pagamentos da Stripe?
- Esperado: recusar (a documentação não tem a resposta)
- Sistema (modelo_recusou): NÃO ENCONTREI NA DOCUMENTAÇÃO.
- [ ] correta

## q043: Como gerar relatórios em PDF com ReportLab em uma rota?
- Esperado: recusar (a documentação não tem a resposta)
- Sistema (modelo_recusou): NÃO ENCONTREI NA DOCUMENTAÇÃO.
- [ ] correta

## q045: Como consumir e publicar mensagens em tópicos do Kafka?
- Esperado: recusar (a documentação não tem a resposta)
- Sistema (respondeu): NÃO ENCONTROU NA DOCUMENTAÇÃO [1]
- [ ] correta

## q047: Como ler um CSV com pandas e devolver o resultado na API?
- Esperado: recusar (a documentação não tem a resposta)
- Sistema (modelo_recusou): NÃO ENCONTREI NA DOCUMENTAÇÃO.
- [ ] correta
