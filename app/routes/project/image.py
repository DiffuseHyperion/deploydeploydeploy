from fastapi import Response, APIRouter, Depends, status, WebSocket, WebSocketDisconnect

from app.lib import dependencies, nixpacks
from app import main

router = APIRouter(
    prefix="/api/v1/{project_id}/image",
    dependencies=[Depends(dependencies.get_key)],
)

@router.websocket("/ws/")
async def get_image_build_logs(
        project_id: str,
        websocket: WebSocket,
):
    await websocket.accept()
    if (project := main.projects.get(project_id)) is None:
        await websocket.send_text(f"Could not find project {project_id}")
        await websocket.close()
    if project.build_process is None:
        await websocket.send_text(f"Project {project_id} has no ongoing build process")
        await websocket.close()
    while True:
        if project.build_process is None:
            break
        line = bytes(project.build_process.stdout.readline()).decode("utf-8")
        if line is None or line == "":
            break
        await websocket.send_text(line)
    await websocket.close()

@router.put("/")
async def create_image(
        project_id: str,
        response: Response,
):
    if (project := main.projects.get(project_id)) is None:
        response.status_code = status.HTTP_404_NOT_FOUND
        return f"Could not find project {project_id}"
    return project.invoke_method(project.build_image, response)

@router.put("/async/")
async def start_image_build(
        project_id: str,
        response: Response,
):
    if (project := main.projects.get(project_id)) is None:
        response.status_code = status.HTTP_404_NOT_FOUND
        return f"Could not find project {project_id}"
    return project.invoke_method(project.start_image_build, response)

@router.delete("/")
async def delete_image(
        project_id: str,
        response: Response,
):
    if (project := main.projects.get(project_id)) is None:
        response.status_code = status.HTTP_404_NOT_FOUND
        return f"Could not find project {project_id}"
    return project.invoke_method(project.delete_image, response)