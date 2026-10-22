"""
Spots: browse the list and view one spot.

    GET /api/spots          list (filter, sort, paginate)      anyone
    GET /api/spots/{id}     one spot with hours + reviews      anyone   404
"""
from typing import Literal

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import func
from sqlmodel import Session, select

from ..auth import get_optional_user
from ..db import get_session
from ..models import Favorite, Hours, Review, Spot, SpotTag, Tag, User
from ..schemas import HoursOut, ReviewOut, SpotDetail, SpotPage, SpotSummary, UserOut

router = APIRouter(prefix="/api/spots", tags=["spots"])


@router.get("", response_model=SpotPage)
def list_spots(
    # PATTERN: query parameters shape a list (filter, sort, paginate).
    tag: str | None = Query(default=None, description="Only spots with this tag, e.g. quiet"),
    sort: Literal["name", "rating", "-rating"] = Query(
        default="name", description="'-rating' means highest rated first"
    ),
    limit: int = Query(default=20, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
    session: Session = Depends(get_session),
    user: User | None = Depends(get_optional_user),
):
    # PATTERN: derived data. Average rating and review count are computed
    # from the reviews table every time, so they can never go stale.
    stats = (
        select(
            Review.spot_id,
            func.avg(Review.rating).label("avg_rating"),
            func.count(Review.id).label("review_count"),
        )
        .group_by(Review.spot_id)
        .subquery()
    )

    query = select(Spot, stats.c.avg_rating, stats.c.review_count).outerjoin(
        stats, stats.c.spot_id == Spot.id
    )
    if tag:
        # Filtering through the join table: spots -> spot_tags -> tags
        query = (
            query.join(SpotTag, SpotTag.spot_id == Spot.id)
            .join(Tag, Tag.id == SpotTag.tag_id)
            .where(Tag.name == tag)
        )

    total = session.exec(select(func.count()).select_from(query.subquery())).one()

    if sort == "name":
        query = query.order_by(Spot.name)
    elif sort == "rating":
        query = query.order_by(func.coalesce(stats.c.avg_rating, 0), Spot.name)
    else:  # "-rating"
        query = query.order_by(func.coalesce(stats.c.avg_rating, 0).desc(), Spot.name)

    rows = session.exec(query.offset(offset).limit(limit)).all()
    items = build_summaries(session, rows, user)
    return SpotPage(items=items, total=total, limit=limit, offset=offset)


@router.get(
    "/{spot_id}",
    response_model=SpotDetail,
    responses={404: {"description": "Spot not found"}},
)
def get_spot(
    spot_id: int,  # PATTERN: path parameter picks ONE thing
    session: Session = Depends(get_session),
    user: User | None = Depends(get_optional_user),
):
    spot = session.get(Spot, spot_id)
    if spot is None:
        # PATTERN: 404 when the thing doesn't exist
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Spot not found")

    stats = session.exec(
        select(func.avg(Review.rating), func.count(Review.id)).where(Review.spot_id == spot_id)
    ).one()
    summary = build_summaries(session, [(spot, stats[0], stats[1])], user)[0]

    hours = session.exec(
        select(Hours).where(Hours.spot_id == spot_id).order_by(Hours.day_of_week)
    ).all()

    # Join reviews with users so each review can show its author's name
    review_rows = session.exec(
        select(Review, User)
        .join(User, User.id == Review.user_id)
        .where(Review.spot_id == spot_id)
        .order_by(Review.created_at.desc())
    ).all()

    return SpotDetail(
        **summary.model_dump(),
        hours=[HoursOut(day_of_week=h.day_of_week, opens=h.opens, closes=h.closes) for h in hours],
        reviews=[review_out(r, u) for r, u in review_rows],
    )


# ---------- helpers ----------

def build_summaries(session: Session, rows, user: User | None) -> list[SpotSummary]:
    """Turn (spot, avg_rating, review_count) rows into the cards the list screen needs."""
    spot_ids = [spot.id for spot, _, _ in rows]
    if not spot_ids:
        return []

    # Tags for all spots on this page, in one query
    tag_rows = session.exec(
        select(SpotTag.spot_id, Tag.name)
        .join(Tag, Tag.id == SpotTag.tag_id)
        .where(SpotTag.spot_id.in_(spot_ids))
        .order_by(Tag.name)
    ).all()
    tags_by_spot: dict[int, list[str]] = {}
    for spot_id, name in tag_rows:
        tags_by_spot.setdefault(spot_id, []).append(name)

    # Which of these spots has the logged-in user favorited?
    favorited: set[int] = set()
    if user is not None:
        favorited = set(
            session.exec(
                select(Favorite.spot_id).where(
                    Favorite.user_id == user.id, Favorite.spot_id.in_(spot_ids)
                )
            ).all()
        )

    return [
        SpotSummary(
            id=spot.id,
            name=spot.name,
            address=spot.address,
            avg_rating=round(float(avg), 1) if avg is not None else None,
            review_count=count or 0,
            tags=tags_by_spot.get(spot.id, []),
            is_favorited=spot.id in favorited,
        )
        for spot, avg, count in rows
    ]


def review_out(review: Review, author: User) -> ReviewOut:
    return ReviewOut(
        id=review.id,
        spot_id=review.spot_id,
        rating=review.rating,
        noise=review.noise,
        comment=review.comment,
        created_at=review.created_at,
        author=UserOut(id=author.id, name=author.name),  # no email: it's private
    )
