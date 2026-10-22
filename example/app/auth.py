"""
Fake login.

Real login (passwords, sessions) is a stretch goal. For this project we
"log in" by sending a header with a user's id:

    X-User-Id: 1

In the /docs page, click the green "Authorize" button and type 1, 2 or 3
to act as one of the seeded users.

The important part is NOT how login works. It's the two questions every
protected route asks:
    1. Authentication: who are you?        -> fails with 401
    2. Authorization:  are you allowed?    -> fails with 403  (checked in the routes)
"""
from fastapi import Depends, HTTPException, status
from fastapi.security import APIKeyHeader
from sqlmodel import Session

from .db import get_session
from .models import User

# This makes the "Authorize" button appear in /docs.
user_id_header = APIKeyHeader(
    name="X-User-Id",
    auto_error=False,
    description="Fake login: the id of a seeded user (1, 2 or 3).",
)


def get_optional_user(
    raw_id: str | None = Depends(user_id_header),
    session: Session = Depends(get_session),
) -> User | None:
    """For routes anyone can call, but that show extra info when you're logged in."""
    if raw_id is None:
        return None
    if not raw_id.isdigit():
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "X-User-Id must be a number")
    user = session.get(User, int(raw_id))
    if user is None:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "No user with that id")
    return user


def get_current_user(user: User | None = Depends(get_optional_user)) -> User:
    """
    PATTERN: authentication.
    Add `user: User = Depends(get_current_user)` to any route that requires login.
    """
    if user is None:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "You need to log in")
    return user
