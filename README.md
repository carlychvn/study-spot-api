# Build Something: API starter repo

Two folders, both built with **FastAPI + SQLModel + SQLite** (no SQL or database install needed).

| Folder | What it is | What you do with it |
| --- | --- | --- |
| [`example/`](example/) | **Study Spot Finder**, a complete API that follows every pattern from the lecture | Read it, run it, copy from it |
| [`starter/`](starter/) | A blank project with the setup done (database, fake login, `/api/me`) | Build your own project here |

## The plan

1. **Run the example** and click through `/docs` ([example/README.md](example/README.md) has a list of things to try).
2. **Design your project**: fill in [starter/API_CONTRACT.md](starter/API_CONTRACT.md) and get a TA sign-off.
3. **Build it in `starter/`**, one resource at a time ([starter/README.md](starter/README.md) has the steps).
4. **Done when** every endpoint in your contract works in `/docs`, including the errors.

## Requirements

Python 3.10 or newer. Check with `python --version` (or `python3 --version`).

## Quick start

```bash
cd example
python -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```

Then open http://localhost:8000/docs.

## What's in each project

```
app/
├── main.py       creates the app and plugs in the routers
├── db.py         database connection
├── models.py     tables
├── schemas.py    request and response shapes
├── auth.py       fake login (X-User-Id header)
├── seed.py       fake data
└── routers/      one file per resource (the endpoints)
tests/
└── test_api.py   one test per contract row
```

## About the fake login

Real login (passwords, sessions) is a stretch goal. Here, you "log in" by sending a header `X-User-Id: 1`. In `/docs`, click **Authorize** and type `1`, `2` or `3`. The point is the two checks every route makes: **who are you?** (401) and **are you allowed?** (403).
