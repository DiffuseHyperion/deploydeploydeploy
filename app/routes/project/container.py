from fastapi import Response, APIRouter, Depends, status

import app.lib.dependencies as dependencies
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

    if not project.built:
        response.status_code = status.HTTP_403_FORBIDDEN
        return f"Project {project_id} has not been built"
    if project.running:
        response.status_code = status.HTTP_403_FORBIDDEN
        return f"Project {project_id} is already running"

    main.client.containers.run(
        image=project_id,
        name=project_id,
        auto_remove=True,
        detach=True,
        labels={
            "traefik.enable": "true",
            f"traefik.http.routers.http-{project_id}.entrypoints": "http",
            f"traefik.http.routers.http-{project_id}.rule": f"Host(`http://{project_id}.127.0.0.1.sslip.io`)",
        }
    )
    project.running = True
    return {
        "project_id": project_id,
    }