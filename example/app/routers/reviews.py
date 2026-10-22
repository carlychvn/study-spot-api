"""
Reviews: write, edit and delete.

    POST   /api/spots/{spot_id}/reviews   write a review        logged in     401 404 409 422
    PATCH  /api/reviews/{review_id}       edit my review        author only   401 403 404 422
    DELETE /api/reviews/{review_id}       delete my review      author only   401 403 404

Every write route follows the same order:
    1. Who are you?          401   (Depends(get_current_user))
    2. Is the input valid?   422   (Pydantic, automatically)
    3. Does it exist?        404
    4. Are you allowed?      403
    5. Do the work, respond
"""
from fastapi import APIRouter, Depends, HTTPException, Response, status
from sqlalchemy.exc import IntegrityError
from sqlmodel import Session

from ..auth import get_current_user
from ..db import get_session
from ..models import Review, Spot, User
from ..schemas import ReviewIn, ReviewOut, ReviewUpdate
from .spots import review_out

router = APIRouter(tags=["reviews"])


@router.post(
    "/api/spots/{spot_id}/reviews",
    response_model=ReviewOut,
    status_code=status.HTTP_201_CREATED,  # PATTERN: 201 = created something new
    responses={
        401: {"description": "Not logged in"},
        404: {"description": "Spot not found"},
        409: {"description": "You already reviewed this spot"},
    },
)
def create_review(
    spot_id: int,
    body: ReviewIn,                                # PATTERN: validation (422)
    user: User = Depends(get_current_user),        # PATTERN: authentication (401)
    session: Session = Depends(get_session),
):
    if session.get(Spot, spot_id) is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Spot not found")

    # PATTERN: never trust the client about WHO they are.
    # user_id comes from the login, not from the request body.
    review = Review(spot_id=spot_id, user_id=user.id, **body.model_dump())
    session.add(review)
    try:
        session.commit()
    except IntegrityError:
        # PATTERN: 409 conflict. The database's UNIQUE(user_id, spot_id)
        # rule caught a second review from the same person.
        session.rollback()
        raise HTTPException(status.HTTP_409_CONFLICT, "You already reviewed this spot")
    session.refresh(review)
    return review_out(review, user)


@router.patch(
    "/api/reviews/{review_id}",
    response_model=ReviewOut,
    responses={
        401: {"description": "Not logged in"},
        403: {"description": "Not your review"},
        404: {"description": "Review not found"},
    },
)
def update_review(
    review_id: int,
    body: ReviewUpdate,
    user: User = Depends(get_current_user),
    session: Session = Depends(get_session),
):
    review = get_own_review(session, review_id, user)

    # Only change the fields the client actually sent
    for field, value in body.model_dump(exclude_unset=True).items():
        setattr(review, field, value)
    session.add(review)
    session.commit()
    session.refresh(review)
    return review_out(review, user)


@router.delete(
    "/api/reviews/{review_id}",
    status_code=status.HTTP_204_NO_CONTENT,  # PATTERN: 204 = done, nothing to return
    responses={
        401: {"description": "Not logged in"},
        403: {"description": "Not your review"},
        404: {"description": "Review not found"},
    },
)
def delete_review(
    review_id: int,
    user: User = Depends(get_current_user),
    session: Session = Depends(get_session),
):
    review = get_own_review(session, review_id, user)
    session.delete(review)
    session.commit()
    return Response(status_code=status.HTTP_204_NO_CONTENT)


def get_own_review(session: Session, review_id: int, user: User) -> Review:
    review = session.get(Review, review_id)
    if review is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Review not found")
    # PATTERN: authorization. Logged in is not the same as allowed.
    # Hiding the Edit button in the UI is not enough; the server must check.
    if review.user_id != user.id:
        raise HTTPException(status.HTTP_403_FORBIDDEN, "You can only change your own reviews")
    return review
