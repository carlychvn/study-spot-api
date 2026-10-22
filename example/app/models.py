"""
The data model: one class per table.

Each class with `table=True` becomes a table in the database.
Read this file next to your ERD. It should match it exactly.

    users ──< reviews >── spots ──< spot_tags >── tags
      └──────< favorites >──┘ └──< hours
"""
from datetime import datetime, time, timezone

from sqlmodel import Field, SQLModel, UniqueConstraint


def utc_now() -> datetime:
    return datetime.now(timezone.utc)


class User(SQLModel, table=True):
    __tablename__ = "users"

    id: int | None = Field(default=None, primary_key=True)  # PATTERN: primary key
    name: str
    email: str = Field(unique=True)  # PATTERN: rule the database enforces


class Spot(SQLModel, table=True):
    __tablename__ = "spots"

    id: int | None = Field(default=None, primary_key=True)
    name: str
    address: str
    # Notice what is NOT here:
    #   - no `tags` text column      -> tags live in their own table (many-to-many)
    #   - no `hours` text column     -> hours live in their own table (one-to-many)
    #   - no `avg_rating` column     -> computed from reviews, never stored


class Tag(SQLModel, table=True):
    __tablename__ = "tags"

    id: int | None = Field(default=None, primary_key=True)
    name: str = Field(unique=True)  # "quiet", "outlets", "open late"


class SpotTag(SQLModel, table=True):
    """
    PATTERN: join table (many-to-many).
    One spot has many tags, and one tag is on many spots.
    Each row means "this spot has this tag".
    """
    __tablename__ = "spot_tags"

    spot_id: int = Field(foreign_key="spots.id", primary_key=True)
    tag_id: int = Field(foreign_key="tags.id", primary_key=True)


class Hours(SQLModel, table=True):
    """
    PATTERN: one-to-many. One spot has many rows of hours (one per day).
    The foreign key (spot_id) goes on the "many" side.
    """
    __tablename__ = "hours"

    id: int | None = Field(default=None, primary_key=True)
    spot_id: int = Field(foreign_key="spots.id", index=True)
    day_of_week: int = Field(ge=0, le=6)  # 0 = Monday ... 6 = Sunday
    opens: time
    closes: time


class Review(SQLModel, table=True):
    __tablename__ = "reviews"
    # PATTERN: one review per person per spot, enforced by the database itself
    __table_args__ = (UniqueConstraint("user_id", "spot_id"),)

    id: int | None = Field(default=None, primary_key=True)
    spot_id: int = Field(foreign_key="spots.id", index=True)  # PATTERN: foreign key
    user_id: int = Field(foreign_key="users.id", index=True)  # who owns this row
    rating: int  # 1-5, validated by ReviewIn in schemas.py
    noise: str   # "quiet" | "moderate" | "loud"
    comment: str
    created_at: datetime = Field(default_factory=utc_now)


class Favorite(SQLModel, table=True):
    """
    PATTERN: join table that also stores its own data (saved_at).
    Many users <-> many spots. The composite primary key makes it
    impossible to favorite the same spot twice.
    """
    __tablename__ = "favorites"

    user_id: int = Field(foreign_key="users.id", primary_key=True)
    spot_id: int = Field(foreign_key="spots.id", primary_key=True)
    saved_at: datetime = Field(default_factory=utc_now)
