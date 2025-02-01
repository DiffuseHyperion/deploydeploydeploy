import os

def assert_env(name):
    if (env := os.getenv(name)) is None:
        raise RuntimeError(f"Environment variable {name} is not set")
    return env

PROJECT_DIR = os.getenv("PROJECT_DIR") or os.path.join("/", "projects")
DATA_FILE = os.getenv("DATA_FILE") or os.path.join("/", "data.sqlite")
SECRET_KEY = assert_env("SECRET_KEY")
TRAEFIK_NAME = assert_env("TRAEFIK_NAME")
TRAEFIK_NETWORK = assert_env("TRAEFIK_NETWORK")
TRAEFIK_VOLUME = assert_env("TRAEFIK_VOLUME")