import os
import shutil
import stat
import sys

from fastapi import Response, APIRouter, Depends, status

import app.routes.dependencies as dependencies
import app.main as main
from app.lib.environment import PROJECT_DIR

router = APIRouter(
    prefix="/api/v1/{project_id}",
    dependencies=[Depends(dependencies.get_key)],
)

# taken mostly from https://github.com/gitpython-developers/GitPython/blob/main/git/util.py#L212
def handler(function, path, _excinfo):
    os.chmod(path, stat.S_IWUSR)
    function(path)

@router.delete("/")
async def delete_project_info(
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