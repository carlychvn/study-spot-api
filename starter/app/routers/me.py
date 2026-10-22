"""
The logged-in user. Already done, so you can test login right away.

    GET /api/me     who am I?     logged in     401
"""
from fastapi import APIRouter, Depends

from ..auth import get_current_user
from ..models import User
from ..schemas import MeOut

router = APIRouter(prefix="/api/me", tags=["me"])


@router.get("", response_model=MeOut, responses={401: {"description": "Not logged in"}})
def get_me(user: User = Depends(get_current_user)):
    return MeOut(id=user.id, name=user.name, email=user.email)


# TODO (optional): add "my stuff" endpoints here, like GET /api/me/recipes
