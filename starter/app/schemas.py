"""
Request and response shapes: your API contract, written as Python.

For each resource you usually need:
  - ThingIn      what the frontend SENDS to create one     (no id, no user_id!)
  - ThingUpdate  what it sends to change one (all fields optional, for PATCH)
  - ThingOut     what it GETS BACK                          (no private fields!)

Pydantic rejects anything that doesn't match with a 422, automatically.
See ../example/app/schemas.py for a full set.
"""
from pydantic import BaseModel, Field  # noqa: F401  (you'll need Field)


class UserOut(BaseModel):
    id: int
    name: str


class MeOut(UserOut):
    email: str


# ---------------------------------------------------------------------------
# TODO: add your request and response shapes below.
# ---------------------------------------------------------------------------

# class RecipeIn(BaseModel):
#     title: str = Field(min_length=1, max_length=100)
#     minutes: int = Field(ge=1, le=600)
#
#
# class RecipeUpdate(BaseModel):
#     title: str | None = Field(default=None, min_length=1, max_length=100)
#     minutes: int | None = Field(default=None, ge=1, le=600)
#
#
# class RecipeOut(BaseModel):
#     id: int
#     title: str
#     minutes: int
#     author: UserOut
#
#
# class RecipePage(BaseModel):
#     items: list[RecipeOut]
#     total: int
#     limit: int
#     offset: int
