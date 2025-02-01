import os.path

from fastapi import Response, APIRouter, Depends, status
from pydantic import BaseModel
from dotenv import set_key

import app.routes.dependencies as dependencies
import app.main as main

router = APIRouter(
    prefix="/api/v1/{project_id}/environment",
    dependencies=[Depends(dependencies.get_key)],
)

class SetProjectEnvironmentVariableModel(BaseModel):
    key: str
    value: str

@router.post("/")
async def set_project_env_variable(
        project_id: str,
        body: SetProjectEnvironmentVariableModel,
        response: Response,
):
    if (project := main.projects.get(project_id)) is None:
        response.status_code = status.HTTP_404_NOT_FOUND
        return f"Could not find project {project_id}"

    set_key(os.path.join(project.project_path, ".env"), body.key, body.value)
    project.env_vars.update({body.key: body.value})
    return {
        "key": body.key,
        "value": body.value,
    }