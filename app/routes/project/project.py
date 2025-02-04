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
    return project

@router.put("/")
async def update_project(
        project_id: str,
        response: Response,
):
    if (project := main.projects.get(project_id)) is None:
        response.status_code = status.HTTP_404_NOT_FOUND
        return f"Could not find project {project_id}"
    exit_code, response = git.fetch(project.project_path)
    if exit_code != 0:
        response.status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
        return {
            "error": "Could not fetch latest commit",
            "response": response
        }
    exit_code, response = git.reset_hard(project.project_path)
    if exit_code != 0:
        response.status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
        return {
            "error": "Could not fetch latest commit",
            "response": response
        }
    return {
        "project_id": project_id,
    }

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