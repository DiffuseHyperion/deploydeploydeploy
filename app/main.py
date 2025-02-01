import docker
from docker import DockerClient
from fastapi import FastAPI
import sqlite3
from app.lib.environment import DATA_FILE
app = FastAPI()
connection = sqlite3.connect(DATA_FILE)
client: DockerClient
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

from app.routes.api.v1.projects.post import router as post_projects
from app.routes.api.v1.projects.get import router as get_projects
from app.routes.api.v1.project.get import router as get_project_info
from app.routes.api.v1.project.delete import router as delete_project
from app.routes.api.v1.project.environment.post import router as set_project_env_var
from app.routes.api.v1.project.environment.delete import router as delete_project_env_var
from app.routes.api.v1.project.image.delete import router as delete_project_image
from app.routes.api.v1.project.image.post import router as build_project_image
from app.routes.api.v1.project.container.post import router as create_project_container

app.include_router(post_projects)
app.include_router(get_projects)
app.include_router(get_project_info)
app.include_router(delete_project)
app.include_router(set_project_env_var)
app.include_router(delete_project_env_var)
app.include_router(delete_project_image)
app.include_router(build_project_image)
app.include_router(create_project_container)