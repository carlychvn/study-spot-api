"""
Tests double as a checklist for the API contract: one test per row, plus
one test per error code. Run with:  pytest
"""
from .conftest import ALEX, BEA, CHRIS

GOOD_REVIEW = {"rating": 4, "noise": "quiet", "comment": "Nice spot"}


# ---------- GET /api/spots ----------

def test_list_spots_is_paginated(client):
    r = client.get("/api/spots?limit=2")
    assert r.status_code == 200
    body = r.json()
    assert body["total"] == 8
    assert len(body["items"]) == 2
    assert body["limit"] == 2 and body["offset"] == 0


def test_filter_by_tag(client):
    names = {s["name"] for s in client.get("/api/spots?tag=quiet").json()["items"]}
    assert names == {"Moffitt Library", "Main Stacks", "East Asian Library", "Northside Reading Room"}


def test_sort_by_rating(client):
    items = client.get("/api/spots?sort=-rating").json()["items"]
    assert items[0]["avg_rating"] == 5.0  # Main Stacks


def test_rating_is_computed(client):
    moffitt = next(s for s in client.get("/api/spots").json()["items"] if s["name"] == "Moffitt Library")
    assert moffitt["avg_rating"] == 4.5 and moffitt["review_count"] == 2


def test_is_favorited_depends_on_who_is_logged_in(client):
    anon = client.get("/api/spots/1").json()
    alex = client.get("/api/spots/1", headers=ALEX).json()
    assert anon["is_favorited"] is False
    assert alex["is_favorited"] is True


def test_bad_sort_is_422(client):
    assert client.get("/api/spots?sort=banana").status_code == 422


# ---------- GET /api/spots/{id} ----------

def test_spot_detail_has_hours_reviews_and_author(client):
    body = client.get("/api/spots/1").json()
    assert len(body["hours"]) == 7
    assert body["reviews"][0]["author"]["name"] in {"Alex", "Bea"}
    assert "email" not in body["reviews"][0]["author"]  # private field never leaks


def test_spot_not_found_is_404(client):
    r = client.get("/api/spots/999")
    assert r.status_code == 404
    assert r.json() == {"detail": "Spot not found"}


# ---------- POST /api/spots/{id}/reviews ----------

def test_create_review(client):
    r = client.post("/api/spots/2/reviews", json=GOOD_REVIEW, headers=BEA)
    assert r.status_code == 201
    assert r.json()["author"]["name"] == "Bea"


def test_create_review_logged_out_is_401(client):
    assert client.post("/api/spots/2/reviews", json=GOOD_REVIEW).status_code == 401


def test_create_review_bad_input_is_422(client):
    bad = {"rating": 7, "noise": "silent", "comment": ""}
    assert client.post("/api/spots/2/reviews", json=bad, headers=BEA).status_code == 422


def test_create_review_twice_is_409(client):
    # Alex already reviewed spot 1 in the seed data
    assert client.post("/api/spots/1/reviews", json=GOOD_REVIEW, headers=ALEX).status_code == 409


def test_create_review_missing_spot_is_404(client):
    assert client.post("/api/spots/999/reviews", json=GOOD_REVIEW, headers=BEA).status_code == 404


def test_user_id_in_body_is_ignored(client):
    sneaky = {**GOOD_REVIEW, "user_id": 1}
    r = client.post("/api/spots/2/reviews", json=sneaky, headers=CHRIS)
    assert r.status_code == 201
    assert r.json()["author"]["name"] == "Chris"


# ---------- PATCH / DELETE /api/reviews/{id} ----------

def test_edit_own_review(client):
    r = client.patch("/api/reviews/1", json={"rating": 3}, headers=ALEX)
    assert r.status_code == 200
    assert r.json()["rating"] == 3
    assert r.json()["comment"] == "Third floor is silent and every desk has outlets."  # unchanged


def test_edit_someone_elses_review_is_403(client):
    assert client.patch("/api/reviews/1", json={"rating": 1}, headers=BEA).status_code == 403


def test_delete_own_review(client):
    assert client.delete("/api/reviews/1", headers=ALEX).status_code == 204
    assert client.delete("/api/reviews/1", headers=ALEX).status_code == 404


def test_delete_someone_elses_review_is_403(client):
    assert client.delete("/api/reviews/1", headers=CHRIS).status_code == 403


# ---------- /api/me ----------

def test_me(client):
    assert client.get("/api/me", headers=BEA).json()["name"] == "Bea"
    assert client.get("/api/me").status_code == 401


def test_favorite_is_idempotent(client):
    first = client.put("/api/me/favorites/4", headers=CHRIS)
    second = client.put("/api/me/favorites/4", headers=CHRIS)
    assert first.status_code == second.status_code == 200
    saved = [f["spot_id"] for f in client.get("/api/me/favorites", headers=CHRIS).json()]
    assert saved == [4]  # saved once, not twice


def test_unfavorite_is_idempotent(client):
    assert client.delete("/api/me/favorites/1", headers=ALEX).status_code == 204
    assert client.delete("/api/me/favorites/1", headers=ALEX).status_code == 204


def test_favorite_missing_spot_is_404(client):
    assert client.put("/api/me/favorites/999", headers=ALEX).status_code == 404


def test_tags(client):
    names = [t["name"] for t in client.get("/api/tags").json()]
    assert "quiet" in names and len(names) == 5
