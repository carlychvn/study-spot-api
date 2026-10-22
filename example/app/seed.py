"""
Seed data: fake rows so the API has something to show right away.

Run `python -m app.seed` to wipe the database and start fresh.
(The app also seeds itself automatically the first time it starts.)
"""
from datetime import time

from sqlmodel import Session, SQLModel, select

from .db import engine
from .models import Favorite, Hours, Review, Spot, SpotTag, Tag, User

USERS = [
    ("Alex", "alex@example.com"),
    ("Bea", "bea@example.com"),
    ("Chris", "chris@example.com"),
]

TAGS = ["quiet", "outlets", "open late", "food nearby", "group friendly"]

# name, address, tags, (weekday opens, weekday closes), (weekend opens, weekend closes)
SPOTS = [
    ("Moffitt Library", "350 Moffitt Library", ["quiet", "outlets", "open late"], (8, 23), (10, 22)),
    ("Main Stacks", "Doe Library, lower levels", ["quiet"], (8, 22), (10, 18)),
    ("Cafe Strada", "2300 College Ave", ["outlets", "food nearby"], (6, 23), (7, 23)),
    ("MLK Student Union", "2495 Bancroft Way", ["group friendly", "food nearby", "outlets"], (7, 22), (9, 20)),
    ("East Asian Library", "C.V. Starr East Asian Library", ["quiet"], (9, 19), (13, 17)),
    ("Northside Reading Room", "100 College Ave", ["quiet", "outlets"], (8, 21), (10, 18)),
    ("Garden Study Cafe", "42 Garden Lane", ["food nearby", "outlets"], (7, 22), (8, 22)),
    ("Riverside Commons", "8 River Walk", ["group friendly", "open late"], (9, 23), (10, 23)),
]

# spot index, user index, rating, noise, comment
REVIEWS = [
    (0, 0, 5, "quiet", "Third floor is silent and every desk has outlets."),
    (0, 1, 4, "moderate", "Great late, but busy during midterms."),
    (1, 0, 5, "quiet", "You can hear a pin drop."),
    (2, 1, 4, "moderate", "Good coffee, outlets along the wall."),
    (2, 2, 3, "loud", "Fun but hard to focus."),
    (3, 2, 4, "loud", "Best for group projects."),
    (5, 1, 5, "quiet", "Plenty of desks and a calm place to read."),
    (6, 0, 4, "moderate", "Easy to find an outlet and a snack."),
    (7, 2, 4, "moderate", "Good tables for studying with friends."),
]

# user index, spot index
FAVORITES = [(0, 0), (0, 1), (1, 2)]


def seed(session: Session) -> None:
    users = [User(name=n, email=e) for n, e in USERS]
    tags = {name: Tag(name=name) for name in TAGS}
    spots = [Spot(name=n, address=a) for n, a, *_ in SPOTS]
    session.add_all(users + list(tags.values()) + spots)
    session.commit()

    for spot, (_, _, tag_names, weekday, weekend) in zip(spots, SPOTS):
        for tag_name in tag_names:
            session.add(SpotTag(spot_id=spot.id, tag_id=tags[tag_name].id))
        for day in range(7):
            opens, closes = weekday if day < 5 else weekend
            session.add(Hours(spot_id=spot.id, day_of_week=day, opens=time(opens), closes=time(closes)))

    for s, u, rating, noise, comment in REVIEWS:
        session.add(Review(spot_id=spots[s].id, user_id=users[u].id, rating=rating, noise=noise, comment=comment))

    for u, s in FAVORITES:
        session.add(Favorite(user_id=users[u].id, spot_id=spots[s].id))

    session.commit()


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
    print("Database reset and seeded: 3 users, 8 spots, 9 reviews.")
