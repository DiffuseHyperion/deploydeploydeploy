from fastapi import Response, APIRouter, Depends, status

import app.routes.dependencies as dependencies
import app.main as main

router = APIRouter(
    prefix="/api/v1/{project_id}",
    dependencies=[Depends(dependencies.get_key)],
)

@router.get("/")
async def get_project_info(
        project_id: str,
        response: Response,
):
    if (project := main.projects.get(project_id)) is None:
        response.status_code = status.HTTP_404_NOT_FOUND
        return f"Could not find project {project_id}"
    return project