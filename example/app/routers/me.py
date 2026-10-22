"""
The logged-in user's own stuff.

    GET    /api/me                          who am I?            logged in   401
    GET    /api/me/favorites                my saved spots       logged in   401
    PUT    /api/me/favorites/{spot_id}      save a spot          logged in   401 404
    DELETE /api/me/favorites/{spot_id}      unsave a spot        logged in   401

PATTERN: "/me" paths. The user comes from the login, so there is no way
to ask for someone else's favorites by changing an id in the URL.
"""
from fastapi import APIRouter, Depends, HTTPException, Response, status
from sqlmodel import Session, select

from ..auth import get_current_user
from ..db import get_session
from ..models import Favorite, Spot, User
from ..schemas import FavoriteOut, MeOut

router = APIRouter(prefix="/api/me", tags=["me"])


@router.get("", response_model=MeOut, responses={401: {"description": "Not logged in"}})
def get_me(user: User = Depends(get_current_user)):
    """The frontend calls this to know whose Edit buttons to show."""
    return MeOut(id=user.id, name=user.name, email=user.email)


@router.get("/favorites", response_model=list[FavoriteOut])
def list_favorites(
    user: User = Depends(get_current_user),
    session: Session = Depends(get_session),
):
    favorites = session.exec(
        select(Favorite).where(Favorite.user_id == user.id).order_by(Favorite.saved_at.desc())
    ).all()
    return [FavoriteOut(spot_id=f.spot_id, saved_at=f.saved_at) for f in favorites]


@router.put(
    "/favorites/{spot_id}",
    response_model=FavoriteOut,
    responses={404: {"description": "Spot not found"}},
)
def save_favorite(
    spot_id: int,
    user: User = Depends(get_current_user),
    session: Session = Depends(get_session),
):
    """
    PATTERN: PUT is idempotent. Sending it twice has the same result as
    sending it once: the spot is saved. If the Wi-Fi drops and the app
    retries, nothing gets duplicated. (A POST would create a second one.)
    """
    if session.get(Spot, spot_id) is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Spot not found")

    favorite = session.get(Favorite, (user.id, spot_id))
    if favorite is None:
        favorite = Favorite(user_id=user.id, spot_id=spot_id)
        session.add(favorite)
        session.commit()
        session.refresh(favorite)
    return FavoriteOut(spot_id=favorite.spot_id, saved_at=favorite.saved_at)


@router.delete("/favorites/{spot_id}", status_code=status.HTTP_204_NO_CONTENT)
def remove_favorite(
    spot_id: int,
    user: User = Depends(get_current_user),
    session: Session = Depends(get_session),
):
    """Also idempotent: unsaving something that isn't saved is fine (still 204)."""
    favorite = session.get(Favorite, (user.id, spot_id))
    if favorite is not None:
        session.delete(favorite)
        session.commit()
    return Response(status_code=status.HTTP_204_NO_CONTENT)
