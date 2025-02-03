import os

def assert_env(name):
    if (env := os.getenv(name)) is None:
        raise RuntimeError(f"Environment variable {name} is not set")
    return env

PROJECT_DIR = os.getenv("PROJECT_DIR", os.path.join("/", "projects"))
DATA_FILE = os.getenv("DATA_FILE", os.path.join("/", "data.sqlite"))
SECRET_KEY = assert_env("SECRET_KEY")
TRAEFIK_NAME = assert_env("TRAEFIK_NAME")
TRAEFIK_NETWORK = assert_env("TRAEFIK_NETWORK")
TRAEFIK_VOLUME = assert_env("TRAEFIK_VOLUME")

TRAEFIK_HTTPS = os.getenv("TRAEFIK_HTTPS", "false").lower() == "true"
TRAEFIK_EMAIL = (assert_env("TRAEFIK_EMAIL") if TRAEFIK_HTTPS else None)
TRAEFIK_CERTS = (assert_env("TRAEFIK_CERTS") if TRAEFIK_HTTPS else None)
TRAEFIK_STAGING = (os.getenv("TRAEFIK_STAGING", "false").lower() == "true" if TRAEFIK_HTTPS else None)