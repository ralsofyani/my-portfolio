"""The one and only page."""

from __future__ import annotations

from datetime import date
from pathlib import Path

from fastapi import APIRouter, Query, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

from app.content import loader

TEMPLATES_DIR = Path(__file__).resolve().parent.parent / "templates"
STATIC_DIR = Path(__file__).resolve().parent.parent / "static"


def asset_version() -> str:
    """Changes whenever CSS/JS change, so browsers never show a stale cached copy."""
    files = [STATIC_DIR / "css" / "style.css", STATIC_DIR / "js" / "main.js"]
    return str(int(max(f.stat().st_mtime for f in files)))
templates = Jinja2Templates(directory=TEMPLATES_DIR)

router = APIRouter()

# Page order (top to bottom) and which sections appear in the top navigation.
# Story order: who I am → what I build → how I solve problems → what drives me → contact.
SECTIONS = ["hero", "experience", "projects", "troubleshooting", "learning", "credentials",
            "ideas", "creative", "teaching", "contact"]
NAV = ["experience", "projects", "troubleshooting", "learning", "credentials", "contact"]
STATUSES = ["professional", "analysis", "in_progress", "experiment", "finished"]


@router.get("/", response_class=HTMLResponse)
async def index(request: Request, lang: str | None = Query(default=None)):
    lang = loader.normalize_lang(lang)
    return templates.TemplateResponse(
        request,
        "index.html",
        {
            "lang": lang,
            "dir": "rtl" if lang in loader.RTL_LANGUAGES else "ltr",
            "c": loader.copy(lang),
            "i18n": loader.all_copy(),
            "site": loader.site(),
            "projects": loader.projects(),
            "first_idea": loader.learning_ideas()[0],
            "experience": loader.experience(),
            "credentials": loader.credentials(),
            "sections": SECTIONS,
            "nav": NAV,
            "statuses": STATUSES,
            "year": date.today().year,
            "v": asset_version(),
        },
    )
