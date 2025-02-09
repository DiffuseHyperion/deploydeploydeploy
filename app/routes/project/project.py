import os, shutil, stat, sys

from fastapi import Response, APIRouter, Depends, status

from app.lib import dependencies, git
from app import main

router = APIRouter(
    prefix="/api/v1/{project_id}",
    dependencies=[Depends(dependencies.get_key)],
)

@router.get("/")
async def get_project(
        project_id: str,
        response: Response,
):
    if (project := main.projects.get(project_id)) is None:
        response.status_code = status.HTTP_404_NOT_FOUND
        return f"Could not find project {project_id}"
    return {
        "project_id": project.project_id,
        "project_path": project.project_path,
        "running": project.running,
        "built": project.built,
        "build_process": False if project.build_process is None else True
    }

@router.put("/")
async def update_project(
        project_id: str,
        response: Response,
):
    if (project := main.projects.get(project_id)) is None:
        response.status_code = status.HTTP_404_NOT_FOUND
        return f"Could not find project {project_id}"
    return project.invoke_method(project.update_project, response)

# taken mostly from https://github.com/gitpython-developers/GitPython/blob/main/git/util.py#L212
def handler(function, path, _excinfo):
    os.chmod(path, stat.S_IWUSR)
    function(path)

@router.delete("/")
async def delete_project(
        project_id: str,
        response: Response,
):
    if (project := main.projects.get(project_id)) is None:
        response.status_code = status.HTTP_404_NOT_FOUND
        return f"Could not find project {project_id}"

    if sys.platform != "win32":
        shutil.rmtree(project.project_path)
    elif sys.version_info >= (3, 12):
        shutil.rmtree(project.project_path, onexc=handler)
    else:
        shutil.rmtree(project.project_path, onerror=handler)

    main.projects.pop(project_id)
    return {
        "project_id": project_id,
    }