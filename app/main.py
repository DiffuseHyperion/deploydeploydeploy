import docker
from fastapi import FastAPI
import sqlite3

from app.lib.environment import DATA_FILE, ENABLE_DOCS
app = FastAPI(
    title="deploydeploydeploy",
    summary="A lightweight continuous deployment app made to be adaptable to existing server environments.",
    docs_url=("/docs" if ENABLE_DOCS else None),
    redoc_url=("/redoc" if ENABLE_DOCS else None),
)
connection = sqlite3.connect(DATA_FILE)
client: docker.DockerClient
try:
    client = docker.from_env()
except:
    raise RuntimeError("Unable to connect to Docker socket")

from app.projects.Project import Project
import app.init as init

if len(result := init.check_programs()) > 0:
    raise RuntimeError(f"The following programs are not installed: {", ".join(result)}")
init.initialize_database()
init.synchronize_projects()
projects: dict[str, Project] = init.create_projects()

from app import routes
app.include_router(routes.projects.router)
app.include_router(routes.project.project.router)
app.include_router(routes.project.container.router)
app.include_router(routes.project.environment.router)
app.include_router(routes.project.image.router)
app.include_router(routes.project.settings.router)