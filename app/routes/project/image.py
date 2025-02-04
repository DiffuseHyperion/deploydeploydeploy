from fastapi import Response, APIRouter, Depends, status

from app.lib import dependencies
from app import main

router = APIRouter(
    prefix="/api/v1/{project_id}/image",
    dependencies=[Depends(dependencies.get_key)],
)

@router.put("/")
async def create_image(
        project_id: str,
        response: Response,
):
    if (project := main.projects.get(project_id)) is None:
        response.status_code = status.HTTP_404_NOT_FOUND
        return f"Could not find project {project_id}"
    return project.invoke_method(project.build_image, response)

@router.delete("/")
async def delete_image(
        project_id: str,
        response: Response,
):
    if (project := main.projects.get(project_id)) is None:
        response.status_code = status.HTTP_404_NOT_FOUND
        return f"Could not find project {project_id}"
    return project.invoke_method(project.delete_image, response)