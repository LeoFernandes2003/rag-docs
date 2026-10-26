# Passagens sorteadas para as perguntas de avaliação

Sorteio com semente 42: um parágrafo de cada arquivo sorteado do corpus.

## C01 · `tutorial/first-steps.md`

````text
If you are curious about what the raw OpenAPI schema looks like, FastAPI automatically generates a JSON (schema) with the descriptions of all your API.
````

## C02 · `advanced/opentelemetry.md`

````text
Exception logs include the exception's type, message, and stack trace. Messages and stack traces can contain sensitive information. Use your provider's log processors to filter or redact them, or set `logs` to `False` to disable these logs.
````

## C03 · `advanced/advanced-python-types.md`

````text
If your code for some reason can't use `|`, for example if it's not in a type annotation but in something like `response_model=`, instead of using the vertical bar (`|`) you can use `Union` from `typing`.
````

## C04 · `tutorial/query-params.md`

````text
Also notice that **FastAPI** is smart enough to notice that the path parameter `item_id` is a path parameter and `q` is not, so, it's a query parameter.
````

## C05 · `deployment/concepts.md`

````text
I'll tell you a bit more about these **concepts** here, and that would hopefully give you the **intuition** you would need to decide how to deploy your API in very different environments, possibly even in **future** ones that don't exist yet.
````

## C06 · `advanced/websockets.md`

````text
If you need something easy to integrate with FastAPI but that is more robust, supported by Redis, PostgreSQL or others, check [encode/broadcaster](https://github.com/encode/broadcaster).
````

## C07 · `advanced/testing-dependencies.md`

````text
To override a dependency for testing, you put as a key the original dependency (a function), and as the value, your dependency override (another function).
````

## C08 · `advanced/response-cookies.md`

````text
**FastAPI** provides the same `starlette.responses` as `fastapi.responses` just as a convenience for you, the developer. But most of the available responses come directly from Starlette.
````

## C09 · `tutorial/static-files.md`

````text
**FastAPI** provides the same `starlette.staticfiles` as `fastapi.staticfiles` just as a convenience for you, the developer. But it actually comes directly from Starlette.
````

## C10 · `advanced/openapi-webhooks.md`

````text
With **FastAPI**, using OpenAPI, you can define the names of these webhooks, the types of HTTP operations that your app can send (e.g. `POST`, `PUT`, etc.) and the request **bodies** that your app would send.
````

## C11 · `tutorial/index.md`

````text
Using it in your editor is what really shows you the benefits of FastAPI, seeing how little code you have to write, all the type checks, autocompletion, etc.
````

## C12 · `tutorial/security/index.md`

````text
There was an OAuth 1, which is very different from OAuth2, and more complex, as it included direct specifications on how to encrypt the communication.
````

## C13 · `tutorial/cookie-param-models.md`

````text
Poor cookie banners with all their effort to get your consent for the API to reject it (This is another joke. Don't pay attention to me. Have some coffee for your cookie. ☕). 🍪
````

## C14 · `advanced/middleware.md`

````text
**FastAPI** provides several middlewares in `fastapi.middleware` just as a convenience for you, the developer. But most of the available middlewares come directly from Starlette.
````

## C15 · `tutorial/dependencies/dependencies-with-yield.md`

````text
This is because any dependency needs to be able to run its exit code before the sub-dependencies, as it might need to still use them during its exit code.
````

## C16 · `how-to/general.md`

````text
To deprecate a *path operation*, and show it in the docs UI, read the docs for [Tutorial - Path Operation Configurations - Deprecation](../tutorial/path-operation-configuration.md#deprecate-a-path-operation).
````

## C17 · `advanced/async-tests.md`

````text
Being able to use asynchronous functions in your tests could be useful, for example, when you're querying your database asynchronously. Imagine you want to test sending requests to your FastAPI application and then verify that your backend successfully wrote the correct data in the database, while using an async database library.
````

## C18 · `tutorial/stream-json-lines.md`

````text
You could use this to stream data from an **AI LLM** service, from **logs** or **telemetry**, or from other types of data that can be structured in **JSON** items.
````

## C19 · `tutorial/response-model.md`

````text
We want FastAPI to keep **filtering** the data using the response model. So that even though the function returns more data, the response will only include the fields declared in the response model.
````

## C20 · `advanced/templates.md`

````text
**FastAPI** provides the same `starlette.templating` as `fastapi.templating` just as a convenience for you, the developer. But most of the available responses come directly from Starlette. The same with `Request` and `StaticFiles`.
````

## C21 · `advanced/testing-events.md`

````text
You can read more details about the ["Running lifespan in tests in the official Starlette documentation site."](https://starlette.dev/lifespan/#running-lifespan-in-tests)
````

## C22 · `tutorial/body-fields.md`

````text
Notice how each model's attribute with a type, default value and `Field` has the same structure as a *path operation function's* parameter, with `Field` instead of `Path`, `Query` and `Body`.
````

## C23 · `tutorial/dependencies/index.md`

````text
In the end, a hierarchical tree of dependencies is built, and the **Dependency Injection** system takes care of solving all these dependencies for you (and their sub-dependencies) and providing (injecting) the results at each step.
````

## C24 · `tutorial/request-files.md`

````text
**FastAPI** provides the same `starlette.responses` as `fastapi.responses` just as a convenience for you, the developer. But most of the available responses come directly from Starlette.
````

## C25 · `tutorial/cors.md`

````text
So, let's say you have a frontend running in your browser at `http://localhost:8080`, and its JavaScript is trying to communicate with a backend running at `http://localhost` (because we don't specify a port, the browser will assume the default port `80`).
````

## C26 · `advanced/strict-content-type.md`

````text
As it's running **locally**, and not in the open internet, you decide to **not have any authentication** set up, just trusting the access to the local network.
````

## C27 · `tutorial/handling-errors.md`

````text
The only difference is that **FastAPI**'s `HTTPException` accepts any JSON-able data for the `detail` field, while Starlette's `HTTPException` only accepts strings for it.
````

## C28 · `tutorial/response-status-code.md`

````text
`status_code` can alternatively also receive an `IntEnum`, such as Python's [`http.HTTPStatus`](https://docs.python.org/3/library/http.html#http.HTTPStatus).
````

## C29 · `how-to/extending-openapi.md`

````text
`app.routes` is a lower-level route tree. It can include route candidates that FastAPI uses internally for included routers, not only final `APIRoute` objects.
````

## C30 · `tutorial/security/simple-oauth2.md`

````text
So, the thief won't be able to try to use those same passwords in another system (as many users use the same password everywhere, this would be dangerous).
````

## C31 · `how-to/migrate-from-pydantic-v1-to-pydantic-v2.md`

````text
If you need to use some of the FastAPI-specific tools for parameters like `Body`, `Query`, `Form`, etc. with Pydantic v1 models, you can import them from `fastapi.temp_pydantic_v1_params` while you finish the migration to Pydantic v2:
````

## C32 · `tutorial/request-forms.md`

````text
To declare form bodies, you need to use `Form` explicitly, because without it the parameters would be interpreted as query parameters or body (JSON) parameters.
````

## C33 · `tutorial/sql-databases.md`

````text
We don't really need to inherit from `HeroBase` because we are re-declaring all the fields. I'll leave it inheriting just for consistency, but this is not necessary. It's more a matter of personal taste. 🤷
````

## C34 · `advanced/additional-responses.md`

````text
You might want to have some predefined responses that apply to many *path operations*, but you want to combine them with custom responses needed by each *path operation*.
````

## C35 · `advanced/security/http-basic-auth.md`

````text
Python will have to compare the whole `stanleyjobso` in both `stanleyjobsox` and `stanleyjobson` before realizing that both strings are not the same. So it will take some extra microseconds to reply back "Incorrect username or password".
````

## C36 · `tutorial/request-forms-and-files.md`

````text
You can declare multiple `File` and `Form` parameters in a *path operation*, but you can't also declare `Body` fields that you expect to receive as JSON, as the request will have the body encoded using `multipart/form-data` instead of `application/json`.
````

## C37 · `editor-support.md`

````text
The official [FastAPI Extension](https://marketplace.visualstudio.com/items?itemName=FastAPILabs.fastapi-vscode) enhances your FastAPI development workflow with *path operation* discovery, navigation, as well as FastAPI Cloud deployment, and live log streaming.
````

## C38 · `tutorial/extra-models.md`

````text
The supporting additional functions `fake_password_hasher` and `fake_save_user` are just to demo a possible flow of the data, but they of course are not providing any real security.
````

## C39 · `advanced/response-headers.md`

````text
**FastAPI** will use that *temporary* response to extract the headers (also cookies and status code), and will put them in the final response that contains the value you returned, filtered by any `response_model`.
````

## C40 · `tutorial/query-params-str-validations.md`

````text
If you feel lost with all these **"regular expression"** ideas, don't worry. They are a hard topic for many people. You can still do a lot of stuff without needing regular expressions yet.
````

## C41 · `tutorial/dependencies/global-dependencies.md`

````text
And all the ideas in the section about [adding `dependencies` to the *path operation decorators*](dependencies-in-path-operation-decorators.md) still apply, but in this case, to all of the *path operations* in the app.
````

## C42 · `tutorial/security/get-current-user.md`

````text
You actually don't have users that log in to your application but robots, bots, or other systems, that have just an access token? Again, it all works the same.
````

## C43 · `tutorial/schema-extra-example.md`

````text
You can set `"json_schema_extra"` with a `dict` containing any additional data you would like to show up in the generated JSON Schema, including `examples`.
````

## C44 · `how-to/authentication-error-status-code.md`

````text
Before FastAPI version `0.122.0`, when the integrated security utilities returned an error to the client after a failed authentication, they used the HTTP status code `403 Forbidden`.
````

## C45 · `advanced/openapi-callbacks.md`

````text
At this point you have the *callback path operation(s)* needed (the one(s) that the *external developer*  should implement in the *external API*) in the callback router you created above.
````

## C46 · `fastapi-cli.md`

````text
In most cases you would (and should) have a "termination proxy" handling HTTPS for you on top, this will depend on how you deploy your application, your provider might do this for you, or you might need to set it up yourself.
````

## C47 · `environment-variables.md`

````text
Read the [Environment Variables guide](https://tiangolo.com/guides/environment-variables/) for a detailed, cross-platform explanation, including how to create and read environment variables and how the `PATH` environment variable works.
````

## C48 · `async.md`

````text
But then, even though you still don't have your burgers, your work with the cashier is "on pause" ⏸, because you have to wait 🕙 for your burgers to be ready.
````

## C49 · `advanced/behind-a-proxy.md`

````text
If you need to mount a sub-application (as described in [Sub Applications - Mounts](sub-applications.md)) while also using a proxy with `root_path`, you can do it normally, as you would expect.
````

## C50 · `how-to/separate-openapi-schemas.md`

````text
Probably the main use case for this is if you already have some autogenerated client code/SDKs and you don't want to update all the autogenerated client code/SDKs yet, you probably will want to do it at some point, but maybe not right now.
````

## C51 · `benchmarks.md`

````text
The simpler the problem solved by the tool, the better performance it will get. And most of the benchmarks don't test the additional features provided by the tool.
````

## C52 · `advanced/dataclasses.md`

````text
So, even with the code above that doesn't use Pydantic explicitly, FastAPI is using Pydantic to convert those standard dataclasses to Pydantic's own flavor of dataclasses.
````

## C53 · `index.md`

````text
If you prefer to use `pip`, install `fastapi[standard]` inside a virtual environment. See the [installation guide](tutorial/#install-fastapi) for the alternative steps.
````

## C54 · `advanced/stream-data.md`

````text
This also means that with `StreamingResponse` you have the **freedom** and **responsibility** to produce and encode the data bytes exactly as you need them to be sent, independent of the type annotations. 🤓
````

## C55 · `tutorial/path-params.md`

````text
And because the generated schema is from the [OpenAPI](https://github.com/OAI/OpenAPI-Specification/blob/main/versions/3.1.0.md) standard, there are many compatible tools.
````

## C56 · `virtual-environments.md`

````text
Read the [Virtual Environments guide](https://tiangolo.com/guides/virtual-environments/) to learn how virtual environments work underneath, including activation and the alternative `python -m venv` and `pip` workflow.
````

## C57 · `advanced/response-directly.md`

````text
When you declare a [Response Model - Return Type](../tutorial/response-model.md) in a path operation, **FastAPI** will use it to serialize the data to JSON, using Pydantic.
````

## C58 · `tutorial/header-param-models.md`

````text
The same rules for defaults, extra fields, and OpenAPI apply as for [optional query parameter models](query-param-models.md#optional-query-parameter-models).
````

## C59 · `deployment/manually.md`

````text
The word "**server**" is commonly used to refer to both the remote/cloud computer (the physical or virtual machine) and also the program that is running on that machine (e.g. Uvicorn).
````

## C60 · `deployment/index.md`

````text
This is in contrast to the **development** stages, where you are constantly changing the code, breaking it and fixing it, stopping and restarting the development server, etc.
````
