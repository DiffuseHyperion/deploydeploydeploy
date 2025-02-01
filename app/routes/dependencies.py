from typing import Annotated
from fastapi import Header, HTTPException
from app.lib.environment import SECRET_KEY

async def get_key(authorization: Annotated[str | None, Header()] = None):
    if authorization != SECRET_KEY:
        raise HTTPException(status_code=400, detail="Secret Key invalid")