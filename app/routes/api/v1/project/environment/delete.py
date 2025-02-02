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

    cursor = main.connection.cursor()
    if len(cursor.execute("SELECT id FROM environments WHERE id = ? AND key = ?", [project_id, body.key]).fetchall()) > 0:
        unset_key(os.path.join(project.project_path, ".env"), body.key)
        cursor.execute("DELETE FROM environments WHERE id = ? AND key = ?", [project_id, body.key])
        main.connection.commit()
    return {
        "key": body.key,
    }