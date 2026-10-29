# Conferência manual das respostas

Marque `[x]` se a resposta está correta.

## q001: O que o FastAPI gera automaticamente com as descrições de toda a sua API?
- Esperado: Um schema JSON (OpenAPI) com as descrições de toda a API.
- Sistema (respondeu): [2] O FastAPI gera automaticamente com as descrições de toda a sua API um arquivo JSON chamado `openapi.json`.
- [ ] correta

## q003: O que usar no lugar da barra vertical (|) quando ela não pode ser usada, por exemplo em `response_model=`?
- Esperado: Usar `Union` do módulo `typing`.
- Sistema (resposta_vazia): NÃO ENCONTREI NA DOCUMENTAÇÃO.
- [ ] correta

## q006: Por que existe `fastapi.staticfiles` se o código vem do Starlette?
- Esperado: É uma conveniência para o desenvolvedor; o código vem diretamente do Starlette.
- Sistema (resposta_vazia): NÃO ENCONTREI NA DOCUMENTAÇÃO.
- [ ] correta

## q008: O que diferencia o OAuth 1 do OAuth2?
- Esperado: O OAuth 1 era bem diferente e mais complexo, pois incluía especificações diretas de como criptografar a comunicação.
- Sistema (respondeu): [1] OAuth 1 é muito diferente do OAuth2 e é mais complexo, pois especifica diretamente como criptografar a comunicação. Já o OAuth2 não especifica como criptografar a comunicação, ele espera que você tenha seu aplicativo servido com HTTPS.
- [ ] correta

## q011: Quando é útil usar funções assíncronas nos testes?
- Esperado: Por exemplo, ao consultar o banco de dados de forma assíncrona para verificar se o backend gravou os dados corretos.
- Sistema (respondeu): [1] Quando é útil usar funções assíncronas nos testes é quando você quer testar operações assíncronas, como a escrita de dados no banco de dados, usando uma biblioteca de banco de dados assíncrona.
- [ ] correta

## q013: Mesmo que a função retorne mais dados, o que o response model garante na resposta?
- Esperado: Que a resposta inclua só os campos declarados no response model, pois o FastAPI continua filtrando os dados.
- Sistema (respondeu): [1] Mesmo que a função retorne mais dados, o response model garante que a resposta incluirá apenas os campos declarados nele.
- [ ] correta

## q016: No exemplo de CORS, por que o navegador assume a porta 80 para o backend?
- Esperado: Porque a porta não foi especificada em `http://localhost`, então o navegador assume a porta padrão 80.
- Sistema (modelo_recusou): NÃO ENCONTREI NA DOCUMENTAÇÃO.
- [ ] correta

## q018: Que outro tipo o `status_code` pode receber, além de um número?
- Esperado: Um `IntEnum`, como o `http.HTTPStatus` do Python.
- Sistema (respondeu): [2] O `status_code` também pode receber um `IntEnum`, como o Python's `http.HTTPStatus`.
- [ ] correta

## q021: Por que é preciso usar `Form` explicitamente para declarar corpos de formulário?
- Esperado: Sem ele, os parâmetros seriam interpretados como parâmetros de consulta ou do corpo (JSON).
- Sistema (respondeu): [1] É necessário usar `Form` explicitamente para declarar corpos de formulário porque, sem isso, os parâmetros seriam interpretados como parâmetros de consulta ou parâmetros de corpo (JSON).
- [ ] correta

## q023: Por que a resposta "Incorrect username or password" leva alguns microssegundos extras no exemplo de HTTP Basic?
- Esperado: Porque o Python precisa comparar a string inteira antes de perceber que as duas são diferentes.
- Sistema (respondeu): [2] A resposta "Incorrect username or password" leva alguns microssegundos extras porque o servidor precisa comparar completamente o `stanleyjobso` em ambas as `stanleyjobsox` e `stanleyjobson` antes de reconhecer que ambos os strings são diferentes. Isso leva tempo adicional, fazendo com que a resposta demore alguns microssegundos para ser enviada.
- [ ] correta

## q026: Que informações o FastAPI extrai da resposta temporária?
- Esperado: Os headers (também cookies e status code), que vão para a resposta final.
- Sistema (resposta_vazia): NÃO ENCONTREI NA DOCUMENTAÇÃO.
- [ ] correta

## q028: Como adicionar dados extras ao JSON Schema gerado de um modelo, incluindo exemplos?
- Esperado: Definindo `json_schema_extra` com um `dict` com os dados adicionais, incluindo `examples`.
- Sistema (respondeu): [1] Você pode usar a atributo `model_config` que toma um `dict` como descrito na [Pydantic's docs: Configuration](https://pydantic.dev/docs/validation/latest/api/pydantic/config/). Você pode configurar `"json_schema_extra"` com um `dict` contendo qualquer dado adicional que gostaria de mostrar no JSON Schema gerado, incluindo `examples`. **Dica** Você pode usar a mesma técnica para estender o JSON Schema e adicionar seu próprio extra de dados personalizados. Por exemplo, você pode usá-lo para adicionar metadados para uma interface de usuário do frontend, etc. **Nota** OpenAPI 3.1.0 (usado desde FastAPI 0.99.0) adicionou suporte para `examples`, que faz parte do **JSON Schema** padrão. [2] Você pode declarar informações adicionais com `json_schema_extra` em `Field`, `Query`, `Body`, etc. Eles serão incluídos no JSON Schema gerado. Você aprenderá mais sobre como adicionar informações adicionais mais tarde nos docs, quando aprender a declarar exemplos. **Aviso** Chaves extras passadas em `json_schema_extra` também estarão presentes no OpenAPI gerado para sua aplicação. [3] Você pode declarar exemplos de dados que seu app pode receber. Aqui estão algumas maneiras de fazer isso. **Extra JSON Schema data in Pydantic models** Você pode declarar `examples` para um modelo Pydantic que será adicionado ao JSON Schema gerado. ```python from fastapi import FastAPI from pydantic import BaseModel app = FastAPI() class Item(BaseModel): name: str description: str | None = None price: float tax: float | None = None model_config = { "json_schema
- [ ] correta

## q031: O que o FastAPI usa por baixo para converter dataclasses padrão?
- Esperado: Usa o Pydantic para converter as dataclasses padrão para a versão de dataclasses do próprio Pydantic.
- Sistema (resposta_vazia): NÃO ENCONTREI NA DOCUMENTAÇÃO.
- [ ] correta

## q033: O que mostra, no editor, os benefícios do FastAPI?
- Esperado: Ver quão pouco código é preciso escrever, as verificações de tipo, o autocompletar etc.
- Sistema (resposta_vazia): NÃO ENCONTREI NA DOCUMENTAÇÃO.
- [ ] correta

## q036: Como a fase de desenvolvimento se contrapõe à de implantação?
- Esperado: No desenvolvimento se muda o código o tempo todo, quebrando e consertando, parando e reiniciando o servidor de desenvolvimento.
- Sistema (respondeu): [1] Fase de desenvolvimento se contrapõe à fase de implantação na medida em que, durante o desenvolvimento, ocorrem constantes alterações no código, quebrando-o e corrigindo erros, interrompendo e reiniciando o servidor de desenvolvimento, o que não ocorre na fase de implantação. Na fase de implantação, o aplicativo é feito disponível para os usuários, geralmente em um servidor remoto, com um programa de servidor que garante desempenho, estabilidade e acesso eficiente ao aplicativo pelos usuários.
- [ ] correta

## q038: O que é `app.routes`?
- Esperado: Uma árvore de rotas de nível mais baixo, que pode incluir candidatas a rota usadas internamente para routers incluídos, e não só objetos `APIRoute` finais.
- Sistema (resposta_vazia): NÃO ENCONTREI NA DOCUMENTAÇÃO.
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
- Sistema (modelo_recusou): NÃO ENCONTREI NA DOCUMENTAÇÃO.
- [ ] correta

## q047: Como ler um CSV com pandas e devolver o resultado na API?
- Esperado: recusar (a documentação não tem a resposta)
- Sistema (modelo_recusou): NÃO ENCONTREI NA DOCUMENTAÇÃO.
- [ ] correta
