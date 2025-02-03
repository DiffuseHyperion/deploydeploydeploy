from fastapi import Response, APIRouter, Depends, status
from docker.errors import ImageNotFound

from app.lib import dependencies
from app import main
from app.lib import nixpacks

router = APIRouter(
    prefix="/api/v1/{project_id}/image",
    dependencies=[Depends(dependencies.get_key)],
)

@router.delete("/")
async def delete_image(
        project_id: str,
        response: Response,
):
    if (project := main.projects.get(project_id)) is None:
        response.status_code = status.HTTP_404_NOT_FOUND
        return f"Could not find project {project_id}"

    if not project.built:
        response.status_code = status.HTTP_404_NOT_FOUND
        return f"Could not find image to project"
    try:
        main.client.images.get(project_id).remove()
        project.built = False
        return {
            "project_id": project_id,
        }
    except ImageNotFound:
        response.status_code = status.HTTP_404_NOT_FOUND
        return f"Could not find image to project"

@router.put("/")
async def create_image(
        project_id: str,
        response: Response,
):
    if (project := main.projects.get(project_id)) is None:
        response.status_code = status.HTTP_404_NOT_FOUND
        return f"Could not find project {project_id}"

    exit_code, output = nixpacks.build_image(project_id, project.project_path)
    if exit_code != 0:
        response.status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
        return {
            "exit_code": exit_code,
            "output": output,
        }

    project.built = True
    return {
        "project_id": project_id,
    }