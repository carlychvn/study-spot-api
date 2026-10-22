"""
Run with:  pytest

Goal: one test for every row in your API contract, plus one test for every
error code you listed. ../example/tests/test_api.py has 23 you can copy from.
"""
from .conftest import ALEX, BEA  # noqa: F401


def test_health(client):
    assert client.get("/api/health").json() == {"status": "ok"}


def test_me_logged_in(client):
    assert client.get("/api/me", headers=ALEX).json()["name"] == "Alex"


def test_me_logged_out_is_401(client):
    assert client.get("/api/me").status_code == 401


# TODO: your tests. Some to start with:
#
# def test_create_recipe(client):
#     r = client.post("/api/recipes", json={"title": "Toast", "minutes": 3}, headers=ALEX)
#     assert r.status_code == 201
#
# def test_create_recipe_logged_out_is_401(client):
#     assert client.post("/api/recipes", json={"title": "Toast", "minutes": 3}).status_code == 401
#
# def test_create_recipe_bad_input_is_422(client):
#     assert client.post("/api/recipes", json={"title": "", "minutes": -1}, headers=ALEX).status_code == 422
#
# def test_edit_someone_elses_recipe_is_403(client):
#     assert client.patch("/api/recipes/1", json={"minutes": 5}, headers=BEA).status_code == 403
