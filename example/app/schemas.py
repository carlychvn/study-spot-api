"""
Request and response shapes (the API contract, written as Python).

PATTERN: the API response is NOT the database row.
- Requests contain only what the user provides. Notice ReviewIn has no user_id:
  the server knows who you are from your login and never trusts a user_id
  sent by the client.
- Responses are shaped for the screen: they can combine tables (author name,
  tags, average rating) and leave out private fields (like other users' emails).

Pydantic checks every request against these classes. Anything that doesn't
match is rejected with 422 before your route code runs.
"""
from datetime import datetime, time
from typing import Literal

from pydantic import BaseModel, Field

Noise = Literal["quiet", "moderate", "loud"]


# ---------- Requests (what the frontend sends) ----------

class ReviewIn(BaseModel):
    rating: int = Field(ge=1, le=5, examples=[4])
    noise: Noise = Field(examples=["quiet"])
    comment: str = Field(min_length=1, max_length=1000, examples=["Great outlets, very quiet"])


class ReviewUpdate(BaseModel):
    """PATCH = change part of something, so every field is optional."""
    rating: int | None = Field(default=None, ge=1, le=5)
    noise: Noise | None = None
    comment: str | None = Field(default=None, min_length=1, max_length=1000)


# ---------- Responses (what the frontend gets back) ----------

class UserOut(BaseModel):
    id: int
    name: str


class MeOut(UserOut):
    email: str  # only ever shown to yourself


class TagOut(BaseModel):
    id: int
    name: str


class HoursOut(BaseModel):
    day_of_week: int
    opens: time
    closes: time


class ReviewOut(BaseModel):
    id: int
    spot_id: int
    rating: int
    noise: Noise
    comment: str
    created_at: datetime
    author: UserOut  # from a join with users, so the screen can show a name


class SpotSummary(BaseModel):
    """One card on the spot list screen."""
    id: int
    name: str
    address: str
    avg_rating: float | None  # computed, None if no reviews yet
    review_count: int          # computed
    tags: list[str]
    is_favorited: bool         # so the heart icon knows whether to be filled in


class SpotDetail(SpotSummary):
    """The spot detail screen."""
    hours: list[HoursOut]
    reviews: list[ReviewOut]


class SpotPage(BaseModel):
    """PATTERN: paginated list. Never return 'everything' from a list endpoint."""
    items: list[SpotSummary]
    total: int
    limit: int
    offset: int


class FavoriteOut(BaseModel):
    spot_id: int
    saved_at: datetime
