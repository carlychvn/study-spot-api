"""
TEMPLATE: one resource, all five standard endpoints.

How to use this file:
  1. Copy it to a new file named after your resource, e.g. routers/recipes.py
  2. Replace Thing / things / ThingIn / ThingOut with your names
  3. Fill in every TODO using YOUR API contract (who can call it, which errors)
  4. Delete endpoints your contract doesn't have
  5. Plug the router in at the bottom of app/main.py

This file is not loaded by the app, so it won't break anything as-is.
The finished version of each pattern is in ../example/app/routers/.

    GET    /api/things               list        TODO: who?
    GET    /api/things/{id}          one         TODO: who?           404
    POST   /api/things               create      TODO: who?           401 422 (409?)
    PATCH  /api/things/{id}          change      TODO: owner only?    401 403 404 422
    DELETE /api/things/{id}          remove      TODO: owner only?    401 403 404
"""
from fastapi import APIRouter, Depends, HTTPException, Query, Response, status
from sqlalchemy import func
from sqlmodel import Session, select

from ..auth import get_current_user
from ..db import get_session
from ..models import Thing, User  # TODO: your model
from ..schemas import ThingIn, ThingOut, ThingPage, ThingUpdate, UserOut  # TODO: your schemas

router = APIRouter(prefix="/api/things", tags=["things"])  # TODO: plural noun


# ---------- LIST ----------
@router.get("", response_model=ThingPage)
def list_things(
    # TODO: add filters your screens need, e.g. tag: str | None = None
    limit: int = Query(default=20, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
    session: Session = Depends(get_session),
):
    query = select(Thing)
    # TODO: if tag: query = query.where(...)
    total = session.exec(select(func.count()).select_from(query.subquery())).one()
    rows = session.exec(query.order_by(Thing.id).offset(offset).limit(limit)).all()
    return ThingPage(items=[to_out(session, t) for t in rows], total=total, limit=limit, offset=offset)


# ---------- GET ONE ----------
@router.get("/{thing_id}", response_model=ThingOut)
def get_thing(thing_id: int, session: Session = Depends(get_session)):
    thing = session.get(Thing, thing_id)
    if thing is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Thing not found")  # TODO: message
    return to_out(session, thing)


# ---------- CREATE ----------
@router.post("", response_model=ThingOut, status_code=status.HTTP_201_CREATED)
def create_thing(
    body: ThingIn,                            # 422 if the input doesn't match ThingIn
    user: User = Depends(get_current_user),   # 401 if not logged in
    session: Session = Depends(get_session),
):
    # user_id comes from the login, NEVER from the request body
    thing = Thing(user_id=user.id, **body.model_dump())
    session.add(thing)
    session.commit()
    # TODO: if your table has a UNIQUE rule, catch IntegrityError -> 409
    #       (see create_review in ../example/app/routers/reviews.py)
    session.refresh(thing)
    return to_out(session, thing)


# ---------- UPDATE ----------
@router.patch("/{thing_id}", response_model=ThingOut)
def update_thing(
    thing_id: int,
    body: ThingUpdate,
    user: User = Depends(get_current_user),
    session: Session = Depends(get_session),
):
    thing = get_own_thing(session, thing_id, user)
    for field, value in body.model_dump(exclude_unset=True).items():
        setattr(thing, field, value)
    session.add(thing)
    session.commit()
    session.refresh(thing)
    return to_out(session, thing)


# ---------- DELETE ----------
@router.delete("/{thing_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_thing(
    thing_id: int,
    user: User = Depends(get_current_user),
    session: Session = Depends(get_session),
):
    thing = get_own_thing(session, thing_id, user)
    session.delete(thing)
    session.commit()
    return Response(status_code=status.HTTP_204_NO_CONTENT)


# ---------- helpers ----------
def get_own_thing(session: Session, thing_id: int, user: User) -> Thing:
    thing = session.get(Thing, thing_id)
    if thing is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Thing not found")
    # Authorization: logged in is not the same as allowed
    # TODO: is this the right rule for YOUR app? (owner only? admins too?)
    if thing.user_id != user.id:
        raise HTTPException(status.HTTP_403_FORBIDDEN, "You can only change your own things")
    return thing


def to_out(session: Session, thing: Thing) -> ThingOut:
    """Shape the database row into the response. Add joined data, leave out private fields."""
    author = session.get(User, thing.user_id)
    return ThingOut(
        id=thing.id,
        # TODO: your fields
        author=UserOut(id=author.id, name=author.name),
    )
