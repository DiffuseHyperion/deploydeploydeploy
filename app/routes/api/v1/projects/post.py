import uuid
import os

from fastapi import Response, APIRouter, Depends, status
from pydantic import BaseModel

from app.lib.environment import PROJECT_DIR
import app.routes.dependencies as dependencies
import app.lib.git as git
import app.main as main
from app.projects.Project import Project

router = APIRouter(
    prefix="/api/v1/projects",
    dependencies=[Depends(dependencies.get_key)],
)

class CreateProjectModel(BaseModel):
    git_url: str

@router.post("/")
async def create_project(
        body: CreateProjectModel,
        response: Response,
):
    project_uuid: str = str(uuid.uuid4())

    exit_code, output = git.clone_repo(body.git_url, os.path.join(PROJECT_DIR, project_uuid))
    if exit_code != 0:
        response.status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
        return {
            "exit_code": exit_code,
            "output": output,
        }
    else:
        main.projects.update({project_uuid: Project(project_uuid)})
        return {
            "project_uuid": project_uuid,
        }