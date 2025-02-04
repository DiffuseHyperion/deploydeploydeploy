from fastapi import Response, APIRouter, Depends, status

from app.lib import dependencies
from app import main

router = APIRouter(
    prefix="/api/v1/{project_id}/container",
    dependencies=[Depends(dependencies.get_key)],
)

@router.post("/")
async def create_container(
        project_id: str,
        response: Response,
):
    if (project := main.projects.get(project_id)) is None:
        response.status_code = status.HTTP_404_NOT_FOUND
        return f"Could not find project {project_id}"
    return project.invoke_method(project.start_container, response)

@router.delete("/")
async def stop_container(
        project_id: str,
        response: Response,
):
    if (project := main.projects.get(project_id)) is None:
        response.status_code = status.HTTP_404_NOT_FOUND
        return f"Could not find project {project_id}"
    return project.invoke_method(project.stop_container, response)