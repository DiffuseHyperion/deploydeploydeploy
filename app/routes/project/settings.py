from typing import Literal

from fastapi import Response, APIRouter, Depends, status
from pydantic import BaseModel

from app.lib import dependencies
from app import main

router = APIRouter(
    prefix="/api/v1/{project_id}/settings",
    dependencies=[Depends(dependencies.get_key)],
)

class SetProjectPortModel(BaseModel):
    port: int

@router.put("/port")
async def set_project_port(
        project_id: str,
        body: SetProjectPortModel,
        response: Response,
):
    if (main.projects.get(project_id)) is None:
        response.status_code = status.HTTP_404_NOT_FOUND
        return f"Could not find project {project_id}"
    cursor = main.connection.cursor()
    cursor.execute("UPDATE projects SET port = ? WHERE id = ?", (body.port, project_id))
    main.connection.commit()
    cursor.close()
    return {
        "project_id": project_id,
        "port": body.port,
    }

class SetProjectDomainModel(BaseModel):
    domain: str

@router.put("/domain")
async def set_project_port(
        project_id: str,
        body: SetProjectDomainModel,
        response: Response,
):
    if (main.projects.get(project_id)) is None:
        response.status_code = status.HTTP_404_NOT_FOUND
        return f"Could not find project {project_id}"
    cursor = main.connection.cursor()
    cursor.execute("UPDATE projects SET domain = ? WHERE id = ?", (body.domain, project_id))
    main.connection.commit()
    cursor.close()
    return {
        "project_id": project_id,
        "domain": body.domain,
    }

class SetProjectBranchModel(BaseModel):
    branch: str

@router.put("/branch")
async def set_project_branch(
        project_id: str,
        body: SetProjectBranchModel,
        response: Response,
):
    if (main.projects.get(project_id)) is None:
        response.status_code = status.HTTP_404_NOT_FOUND
        return f"Could not find project {project_id}"
    cursor = main.connection.cursor()
    cursor.execute("UPDATE projects SET branch = ? WHERE id = ?", (body.branch, project_id))
    main.connection.commit()
    cursor.close()
    return {
        "project_id": project_id,
        "branch": body.branch,
    }