# Starter: build your own API

This folder already runs. It has the database, fake login and `/api/me` set up. You add your project's tables and endpoints.

## 1. Run it

```bash
cd starter
python -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```

Open **http://localhost:8000/docs**, click **Authorize**, enter `1`, then try `GET /api/me`. If you see Alex, you're set up.

## 2. Design first

Fill in [`API_CONTRACT.md`](API_CONTRACT.md) and get a TA sign-off. **No code before this.**

## 3. Build one slice at a time

For each resource in your contract, do these five steps, then test it in `/docs` before moving on.

| Step | File | Copy the pattern from |
| --- | --- | --- |
| 1. Add the table | `app/models.py` | `../example/app/models.py` |
| 2. Add request/response shapes | `app/schemas.py` | `../example/app/schemas.py` |
| 3. Add the endpoints | copy `app/routers/_TEMPLATE.py` to `app/routers/<resource>.py` | `../example/app/routers/` |
| 4. Plug the router in | bottom of `app/main.py` | `../example/app/main.py` |
| 5. Add fake rows, then reset | `app/seed.py`, then `python -m app.seed` | `../example/app/seed.py` |

Added a table or changed its columns? Run `python -m app.seed` to rebuild the database.

## 4. Check your error cases

For every endpoint, try each error in your contract in `/docs`:

- Logged out (click Authorize → Logout) → **401**
- Logged in as someone who doesn't own it → **403**
- An id that doesn't exist → **404**
- The same thing twice, if that's not allowed → **409**
- Bad input (empty text, number out of range) → **422**

Then write them as tests in `tests/test_api.py` and run `pytest`.

## Done when

- [ ] Every endpoint in `API_CONTRACT.md` works in `/docs`
- [ ] Every error code in the contract actually happens
- [ ] `pytest` passes

## Commands

| Command | What it does |
| --- | --- |
| `uvicorn app.main:app --reload` | Start the API |
| `python -m app.seed` | Wipe and reload fake data |
| `pytest` | Run tests |

## Stuck?

- **Search the example for `PATTERN:`** to find how each idea is done.
- **`no such table` or `no such column`:** run `python -m app.seed`.
- **422 you didn't expect:** read the response body; it says which field is wrong.
