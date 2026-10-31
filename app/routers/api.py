"""Small JSON API: content, projects, and the learning-ideas generator."""

from __future__ import annotations

from typing import Any

from fastapi import APIRouter, HTTPException, Query

from app import __version__
from app.content import loader

router = APIRouter(prefix="/api", tags=["api"])


@router.get("/health")
async def health() -> dict[str, str]:
    return {"status": "ok", "mood": "curious", "version": __version__}


@router.get("/content/{lang}")
async def content(lang: str) -> dict[str, Any]:
    if lang not in loader.LANGUAGES:
        raise HTTPException(status_code=404, detail=f"Language must be one of {loader.LANGUAGES}")
    return loader.copy(lang)


@router.get("/projects")
async def projects(
    lang: str | None = Query(default=None),
    status: str | None = Query(default=None),
) -> list[dict[str, Any]]:
    text = loader.copy(lang)["projects"]["items"]
    items = loader.projects()
    if status:
        items = [p for p in items if p["status"] == status]
    return [{**p, **text.get(p["id"], {})} for p in items]


# ---------------------------------------------------------------------------
# "What should I explore today?" — 30 curated ideas, stored in
# app/content/learning_ideas.json. The browser fetches them once and shuffles
# locally, so clicking the button never needs another request.
# ---------------------------------------------------------------------------

@router.get("/learning-ideas")
async def learning_ideas(lang: str | None = Query(default=None)) -> dict[str, Any]:
    ideas = loader.learning_ideas()
    if lang is None:
        return {"count": len(ideas), "ideas": ideas}
    if lang not in loader.LANGUAGES:
        raise HTTPException(status_code=404, detail=f"Language must be one of {loader.LANGUAGES}")
    flat = [{"id": i["id"], "topic": i["topic"][lang], **i[lang]} for i in ideas]
    return {"count": len(flat), "lang": lang, "ideas": flat}
