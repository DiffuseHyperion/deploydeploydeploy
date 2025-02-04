import uuid, os

from fastapi import Response, APIRouter, Depends, status
from pydantic import BaseModel

from app.lib.environment import PROJECT_DIR
from app.lib import git, dependencies
from app.projects.Project import Project
from app import main

router = APIRouter(
    prefix="/api/v1/projects",
    dependencies=[Depends(dependencies.get_key)],
)

class CreateProjectModel(BaseModel):
    git_url: str
    branch: str

@router.post("/")
async def create_project(
        body: CreateProjectModel,
        response: Response,
):
    project_uuid: str = str(uuid.uuid4())

    exit_code, output = git.clone_repo_branch(body.git_url, body.branch, os.path.join(PROJECT_DIR, project_uuid))
    if exit_code != 0:
        response.status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
        return {
            "exit_code": exit_code,
            "output": output,
        }
    else:
        main.projects.update({project_uuid: Project(project_uuid)})
        cursor = main.connection.cursor()
        cursor.execute("INSERT INTO projects (id, git_url, branch, port, domain) VALUES (?, ?, ?, ?, ?)",
                       [project_uuid, body.git_url, body.branch, 3000, "localhost"])
        return {
            "project_uuid": project_uuid,
        }

@router.get("/")
async def get_projects():
    return main.projects