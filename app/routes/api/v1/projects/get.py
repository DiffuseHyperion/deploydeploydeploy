from fastapi import Response, APIRouter, Depends

import app.routes.dependencies as dependencies
import app.main as main

router = APIRouter(
    prefix="/api/v1/projects",
    dependencies=[Depends(dependencies.get_key)],
)

@router.get("/")
async def get_projects(
        response: Response,
):
    return main.projects