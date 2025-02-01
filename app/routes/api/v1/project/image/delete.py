from docker.errors import ImageNotFound
from fastapi import Response, APIRouter, Depends, status

import app.routes.dependencies as dependencies
import app.main as main

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