import os

def assert_env(name):
    if (env := os.getenv(name)) is None:
        raise RuntimeError(f"Environment variable {name} is not set")
    return env

ENABLE_DOCS = os.getenv("ENABLE_DOCS", "false").lower() == "true"
PROJECT_DIR = os.getenv("PROJECT_DIR", os.path.join("/", "projects"))
DATA_FILE = os.getenv("DATA_FILE", os.path.join("/", "data.sqlite"))
SECRET_KEY = assert_env("SECRET_KEY")
TRAEFIK_NETWORK = assert_env("TRAEFIK_NETWORK")
TRAEFIK_HTTP_ENTRYPOINT = assert_env("TRAEFIK_HTTP_ENTRYPOINT")
TRAEFIK_HTTPS_ENTRYPOINT = os.getenv("TRAEFIK_HTTPS_ENTRYPOINT")
TRAEFIK_CERTRESOLVER = (assert_env("TRAEFIK_CERTRESOLVER") if TRAEFIK_HTTPS_ENTRYPOINT is not None else None)