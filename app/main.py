import docker
from fastapi import FastAPI
import sqlite3

from app.lib.environment import DATA_FILE
app = FastAPI()
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
init.initialize_traefik()

from app import routes
app.include_router(routes.projects.router)
app.include_router(routes.project.project.router)
app.include_router(routes.project.container.router)
app.include_router(routes.project.environment.router)
app.include_router(routes.project.image.router)
app.include_router(routes.project.settings.router)