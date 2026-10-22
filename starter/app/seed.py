"""
Seed data: fake rows so your API has something to show right away.

Run `python -m app.seed` to wipe the database and start fresh.
(The app also seeds itself the first time it starts.)
See ../example/app/seed.py for a bigger example.
"""
from sqlmodel import Session, SQLModel, select

from .db import engine
from .models import User

USERS = [
    ("Alex", "alex@example.com"),
    ("Bea", "bea@example.com"),
    ("Chris", "chris@example.com"),
]


def seed(session: Session) -> None:
    users = [User(name=n, email=e) for n, e in USERS]
    session.add_all(users)
    session.commit()

    # TODO: add 3-10 rows for each of your tables, e.g.
    #
    # recipes = [
    #     Recipe(user_id=users[0].id, title="Garlic noodles", minutes=20),
    #     Recipe(user_id=users[1].id, title="Overnight oats", minutes=5),
    # ]
    # session.add_all(recipes)
    # session.commit()
    #
    # Tip: make sure users[0] and users[1] own different things, so you can
    # test the 403 "not yours" case.


def seed_if_empty() -> None:
    with Session(engine) as session:
        if session.exec(select(User)).first() is None:
            seed(session)


def reset() -> None:
    SQLModel.metadata.drop_all(engine)
    SQLModel.metadata.create_all(engine)
    with Session(engine) as session:
        seed(session)


if __name__ == "__main__":
    reset()
    print("Database reset and seeded.")
