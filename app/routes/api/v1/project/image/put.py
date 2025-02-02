
from fastapi import Response, APIRouter, Depends, status

import app.routes.dependencies as dependencies
import app.lib.nixpacks as nixpacks
import app.main as main

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