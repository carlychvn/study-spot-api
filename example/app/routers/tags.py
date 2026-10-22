"""
Tags: the list of filter chips.

    GET /api/tags     all tags     anyone

This endpoint exists because sketching the spot list screen showed a gap:
the filter chips need the full list of tags, and no other endpoint gave it.
"""
from fastapi import APIRouter, Depends
from sqlmodel import Session, select

from ..db import get_session
from ..models import Tag
from ..schemas import TagOut

router = APIRouter(prefix="/api/tags", tags=["tags"])


@router.get("", response_model=list[TagOut])
def list_tags(session: Session = Depends(get_session)):
    tags = session.exec(select(Tag).order_by(Tag.name)).all()
    return [TagOut(id=t.id, name=t.name) for t in tags]
