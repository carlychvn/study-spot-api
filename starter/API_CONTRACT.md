# [Your project]: API contract

Fill this in **before** writing code, and get a TA to sign off.
See [`../example/API_CONTRACT.md`](../example/API_CONTRACT.md) for a finished one.

## User stories (MVP: 4 at most)

| # | As a ___, I can ___ | so that ___ |
| --- | --- | --- |
| S1 | | |
| S2 | | |
| S3 | | |
| S4 | | |

## Data model

| Table | Fields | Notes (join table? who owns it? unique rules?) |
| --- | --- | --- |
| users | id, name, email | already in the starter |
| | | |
| | | |
| | | |

Computed, not stored: _______________

## Endpoints

Who: **anyone**, **logged in**, or **owner only**.
Errors: 401 not logged in · 403 not allowed · 404 not found · 409 duplicate · 422 bad input.

| Method | Path | Who | Request body | Success | Errors | Story |
| --- | --- | --- | --- | --- | --- | --- |
| GET | `/api/me` | logged in | none | 200 me | 401 | (already done) |
| | | | | | | |
| | | | | | | |
| | | | | | | |
| | | | | | | |
| | | | | | | |

## One example request and response

```
POST /api/________

{ }
```

```
201 Created

{ }
```

## Ready to code?

- [ ] Every story has at least one endpoint, and every endpoint has a story
- [ ] Paths are plural nouns, no verbs (`/api/recipes`, not `/api/getRecipes`)
- [ ] No request body contains `user_id` (it comes from the login)
- [ ] No response leaks private fields
- [ ] List endpoints take `limit` and `offset`
- [ ] Every many-to-many has a join table

TA sign-off: _______________
