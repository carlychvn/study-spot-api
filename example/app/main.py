"""
Study Spot Finder API.

Run it:      uvicorn app.main:app --reload
Try it:      http://localhost:8000/docs
"""
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .db import create_tables
from .routers import me, reviews, spots, tags
from .seed import seed_if_empty


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Runs once when the server starts
    create_tables()
    seed_if_empty()
    yield


app = FastAPI(
    title="Study Spot Finder API",
    description=(
        "Find study spots, read and write reviews, and save favorites.\n\n"
        "**To act as a user:** click **Authorize** and enter `1`, `2` or `3`."
    ),
    lifespan=lifespan,
)

# Lets a frontend running on another port (e.g. React/Vite on 5173) call this API.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(spots.router)
app.include_router(tags.router)
app.include_router(reviews.router)
app.include_router(me.router)


@app.get("/api/health", tags=["health"])
def health():
    return {"status": "ok"}
