import os.path

from fastapi import Response, APIRouter, Depends, status
from pydantic import BaseModel
from dotenv import unset_key

import app.routes.dependencies as dependencies
import app.main as main

router = APIRouter(
    prefix="/api/v1/{project_id}/environment",
    dependencies=[Depends(dependencies.get_key)],
)

class DeleteProjectEnvironmentVariableModel(BaseModel):
    key: str

@router.delete("/")
async def delete_project_env_variable(
        project_id: str,
        body: DeleteProjectEnvironmentVariableModel,
        response: Response,
):
    if (project := main.projects.get(project_id)) is None:
        response.status_code = status.HTTP_404_NOT_FOUND
        return f"Could not find project {project_id}"

    if project.env_vars.get(body.key) is not None:
        unset_key(os.path.join(project.project_path, ".env"), body.key)
        project.env_vars.pop(body.key)
    return {
        "key": body.key,
        "value": body.value,
    }