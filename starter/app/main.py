"""
Your API.

Run it:      uvicorn app.main:app --reload
Try it:      http://localhost:8000/docs
"""
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .db import create_tables
from .routers import me
from .seed import seed_if_empty

# TODO: import your routers, e.g.
# from .routers import recipes


@asynccontextmanager
async def lifespan(app: FastAPI):
    create_tables()
    seed_if_empty()
    yield


app = FastAPI(
    title="My Project API",  # TODO: your project's name
    description="**To act as a user:** click **Authorize** and enter `1`, `2` or `3`.",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(me.router)
# TODO: plug in your routers, e.g.
# app.include_router(recipes.router)


@app.get("/api/health", tags=["health"])
def health():
    return {"status": "ok"}
