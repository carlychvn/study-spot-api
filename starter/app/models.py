"""
Your data model: one class per table.

Copy your ERD into this file. Look at ../example/app/models.py for how
Study Spot did each kind of table.

Checklist for every table:
  [ ] an `id` primary key (or a two-column primary key for join tables)
  [ ] foreign keys on the "many" side      -> Field(foreign_key="other_table.id")
  [ ] a join table for every many-to-many  -> two foreign keys, both primary_key=True
  [ ] a `user_id` on every row a user owns
  [ ] no lists stored in a column, no averages or counts stored
"""
from datetime import datetime, timezone

from sqlmodel import Field, SQLModel, UniqueConstraint  # noqa: F401  (you'll need these)


def utc_now() -> datetime:
    return datetime.now(timezone.utc)


class User(SQLModel, table=True):
    """Already done: fake login uses this table. Add fields if your app needs them."""
    __tablename__ = "users"

    id: int | None = Field(default=None, primary_key=True)
    name: str
    email: str = Field(unique=True)


# ---------------------------------------------------------------------------
# TODO: add your tables below. Delete these examples once you have your own.
# ---------------------------------------------------------------------------

# A normal table that a user owns (one-to-many: one user has many of these):
#
# class Recipe(SQLModel, table=True):
#     __tablename__ = "recipes"
#
#     id: int | None = Field(default=None, primary_key=True)
#     user_id: int = Field(foreign_key="users.id", index=True)   # who owns it
#     title: str
#     minutes: int
#     created_at: datetime = Field(default_factory=utc_now)


# A join table (many-to-many). The two-column primary key stops duplicates:
#
# class RecipeIngredient(SQLModel, table=True):
#     __tablename__ = "recipe_ingredients"
#
#     recipe_id: int = Field(foreign_key="recipes.id", primary_key=True)
#     ingredient_id: int = Field(foreign_key="ingredients.id", primary_key=True)
#     quantity: str          # join tables can hold their own data


# A "one per person" rule enforced by the database:
#
#     __table_args__ = (UniqueConstraint("user_id", "event_id"),)
