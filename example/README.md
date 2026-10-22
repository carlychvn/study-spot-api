# Study Spot Finder (worked example)

A complete API that follows every pattern from the lecture. **Read it, run it, and copy its patterns into your own project in `../starter`.**

Start with [`API_CONTRACT.md`](API_CONTRACT.md): it's the design we made before writing any code.

## Run it

```bash
cd example
python -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```

Open **http://localhost:8000/docs**. Every endpoint is listed there and you can call it with **Try it out**.

**To act as a user:** click **Authorize** (top right), type `1`, `2` or `3`, and click Authorize. You're now Alex, Bea or Chris.

| Command | What it does |
| --- | --- |
| `uvicorn app.main:app --reload` | Starts the API (reloads when you save a file) |
| `python -m app.seed` | Wipes the database and reloads the fake data |
| `pytest` | Runs the tests |

## Things to try in /docs

1. `GET /api/spots` with `tag=quiet` and `sort=-rating` (filter and sort)
2. `GET /api/spots/1` logged out, then logged in as `1` (watch `is_favorited` change)
3. `POST /api/spots/2/reviews` logged out → **401**
4. Same, logged in as `2`, with `"rating": 7` → **422**
5. Fix the rating and send it → **201**. Send it again → **409**
6. Log in as `3` and `PATCH /api/reviews/1` → **403** (it's Alex's review)
7. `PUT /api/me/favorites/4` twice → same result both times (idempotent)

## Where each concept lives

Search the code for `PATTERN:` to find every one.

| Concept | File |
| --- | --- |
| Tables, primary and foreign keys, unique rules | `app/models.py` |
| Join tables (many-to-many) | `app/models.py`: `SpotTag`, `Favorite` |
| Request vs. response shapes, validation (422) | `app/schemas.py` |
| Login (401) | `app/auth.py` |
| Filter, sort, paginate, computed averages | `app/routers/spots.py` |
| 201, 404, 409, ownership check (403), 204 | `app/routers/reviews.py` |
| `/me` paths, idempotent PUT | `app/routers/me.py` |
| Fake data | `app/seed.py` |
| One test per contract row and error code | `tests/test_api.py` |

## Folder layout

```
example/
├── API_CONTRACT.md      the design (read this first)
├── requirements.txt
├── app/
│   ├── main.py          creates the app and plugs in the routers
│   ├── db.py            database connection (SQLite file)
│   ├── models.py        tables
│   ├── schemas.py       request and response shapes
│   ├── auth.py          fake login
│   ├── seed.py          fake data
│   └── routers/         one file per resource
│       ├── spots.py
│       ├── tags.py
│       ├── reviews.py
│       └── me.py
└── tests/
    └── test_api.py
```

## Stretch ideas

- `GET /api/spots?open_now=true` using the `hours` table
- `POST /api/spots` so users can add new spots
- A React frontend that calls this API (CORS is already set up for `localhost:5173`)
