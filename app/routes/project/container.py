from fastapi import Response, APIRouter, Depends, status

from app.lib import dependencies
from app.lib.environment import TRAEFIK_NETWORK
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

    cursor = main.connection.cursor()
    domain = cursor.execute("SELECT domain FROM projects WHERE id = ?", [project_id]).fetchone()[0]
    port = cursor.execute("SELECT port FROM projects WHERE id = ?", [project_id]).fetchone()[0]
    cursor.close()
    main.client.containers.run(
        image=project_id,
        name=project_id,
        auto_remove=True,
        detach=True,
        network=TRAEFIK_NETWORK,
        labels={
            "traefik.enable": "true",
            f"traefik.http.routers.http-{project_id}.entrypoints": "http",
            f"traefik.http.routers.http-{project_id}.rule": f"Host(`{domain}`)",
            f"traefik.http.services.http-{project_id}.loadbalancer.server.port": str(port),
        }
    )
    project.running = True
    return {
        "project_id": project_id,
    }

@router.delete("/")
async def stop_container(
        project_id: str,
        response: Response,
):
    if (project := main.projects.get(project_id)) is None:
        response.status_code = status.HTTP_404_NOT_FOUND
        return f"Could not find project {project_id}"
    if not project.running:
        response.status_code = status.HTTP_403_FORBIDDEN
        return f"Project {project_id} is not running"

    container = main.client.containers.get(project_id)
    container.stop()

    project.running = False
    return {
        "project_id": project_id,
    }