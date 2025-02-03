# deploydeploydeploy

A lightweight continuous deployment app made to be adaptable to existing server environments.

Built with [FastAPI](https://fastapi.tiangolo.com/) and [Nixpacks](https://nixpacks.com/docs).

## Installation:

Example Docker Compose stacks can be found within the repository. 

`docker-compose_http.yml` will only support HTTP, while `docker-compose_https.yml` supports HTTP and HTTPS.

You will need to generate a secret key to interact with the API. Generate a random string with `openssl rand -hex 16`

## Documentation:

You will need to enable docs by setting the environment variable `ENABLE_DOCS` to `true`.
Afterward, you can find the docs at `/docs` and `/redoc`.