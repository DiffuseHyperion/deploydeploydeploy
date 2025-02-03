import dotenv, os

from fastapi import Response, APIRouter, Depends, status
from pydantic import BaseModel

from app.lib import dependencies
from app import main

router = APIRouter(
    prefix="/api/v1/{project_id}/environment",
    dependencies=[Depends(dependencies.get_key)],
)

class SetProjectEnvironmentVariableModel(BaseModel):
    key: str
    value: str

@router.put("/")
async def set_project_environment_variable(
        project_id: str,
        body: SetProjectEnvironmentVariableModel,
        response: Response,
):
    if (project := main.projects.get(project_id)) is None:
        response.status_code = status.HTTP_404_NOT_FOUND
        return f"Could not find project {project_id}"
    cursor = main.connection.cursor()
    dotenv.set_key(os.path.join(project.project_path, ".env"), body.key, body.value)
    cursor.execute("INSERT into environments VALUES (?, ?, ?) ON CONFLICT (id, key) DO UPDATE SET value = ?", (project_id, body.key, body.value, body.value))
    main.connection.commit()
    cursor.close()
    return {
        "key": body.key,
        "value": body.value,
    }

class DeleteProjectEnvironmentVariableModel(BaseModel):
    key: str

@router.delete("/")
async def delete_project_environment_variable(
        project_id: str,
        body: DeleteProjectEnvironmentVariableModel,
        response: Response,
):
    if (project := main.projects.get(project_id)) is None:
        response.status_code = status.HTTP_404_NOT_FOUND
        return f"Could not find project {project_id}"

    cursor = main.connection.cursor()
    if len(cursor.execute("SELECT id FROM environments WHERE id = ? AND key = ?", [project_id, body.key]).fetchall()) > 0:
        dotenv.unset_key(os.path.join(project.project_path, ".env"), body.key)
        cursor.execute("DELETE FROM environments WHERE id = ? AND key = ?", [project_id, body.key])
        main.connection.commit()
    cursor.close()
    return {
        "key": body.key,
    }