# Study Spot Finder: API contract

This is the design we made **before** writing code. The code in `app/` implements exactly this table.

## User stories (MVP)

| # | As a student, I can... |
| --- | --- |
| S1 | browse spots and filter by tag (quiet, outlets, open late) |
| S2 | see a spot's rating, tags, hours and reviews |
| S3 | write one review per spot, and edit or delete my own |
| S4 | save spots to my favorites |

## Data model

| Table | Fields | Notes |
| --- | --- | --- |
| users | id, name, email (unique) | |
| spots | id, name, address | no tags, hours or average stored here |
| tags | id, name (unique) | "quiet", "outlets", ... |
| spot_tags | spot_id, tag_id | **join table**: spots ↔ tags (many-to-many) |
| hours | id, spot_id, day_of_week, opens, closes | one-to-many: one row per day |
| reviews | id, spot_id, user_id, rating, noise, comment, created_at | one review per user per spot |
| favorites | user_id, spot_id, saved_at | **join table**: users ↔ spots |

Average rating and review count are **computed**, never stored.

## Endpoints

| Method | Path | Who | Request body | Success | Errors | Story |
| --- | --- | --- | --- | --- | --- | --- |
| GET | `/api/spots?tag=&sort=&limit=&offset=` | anyone | none | 200 page of spots | 422 bad sort | S1 |
| GET | `/api/tags` | anyone | none | 200 list of tags | none | S1 |
| GET | `/api/spots/{id}` | anyone | none | 200 spot + hours + reviews | 404 | S2 |
| POST | `/api/spots/{id}/reviews` | logged in | `{rating, noise, comment}` | 201 review | 401, 404, 409, 422 | S3 |
| PATCH | `/api/reviews/{id}` | author only | any of `{rating, noise, comment}` | 200 review | 401, 403, 404, 422 | S3 |
| DELETE | `/api/reviews/{id}` | author only | none | 204 | 401, 403, 404 | S3 |
| GET | `/api/me` | logged in | none | 200 me | 401 | (Edit buttons) |
| GET | `/api/me/favorites` | logged in | none | 200 list | 401 | S4 |
| PUT | `/api/me/favorites/{spot_id}` | logged in | none | 200 (same if repeated) | 401, 404 | S4 |
| DELETE | `/api/me/favorites/{spot_id}` | logged in | none | 204 (same if repeated) | 401 | S4 |

## Example request and response

```
POST /api/spots/2/reviews
X-User-Id: 2

{ "rating": 4, "noise": "quiet", "comment": "Nice spot" }
```

```
201 Created

{
  "id": 7,
  "spot_id": 2,
  "rating": 4,
  "noise": "quiet",
  "comment": "Nice spot",
  "created_at": "2026-10-21T17:00:00Z",
  "author": { "id": 2, "name": "Bea" }
}
```

- The request has **no `user_id`**. The server gets it from the login.
- The response includes `author.name` (joined from users) but **not** the author's email.

## Errors

Every error you raise yourself looks like this:

```json
{ "detail": "You already reviewed this spot" }
```

Validation errors (422) come from FastAPI automatically and list each bad field under `detail`.

| Code | Meaning | Example |
| --- | --- | --- |
| 401 | Not logged in | Writing a review with no `X-User-Id` |
| 403 | Logged in, but not allowed | Editing someone else's review |
| 404 | Doesn't exist | `/api/spots/999` |
| 409 | Conflict | Reviewing the same spot twice |
| 422 | Invalid input | `"rating": 7` |
