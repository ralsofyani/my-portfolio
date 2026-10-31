"""Load the editable JSON content files.

Files are re-read whenever they change on disk, so you can edit copy while the
server is running and simply refresh the page.
"""

from __future__ import annotations

import json
from functools import lru_cache
from pathlib import Path
from typing import Any

CONTENT_DIR = Path(__file__).resolve().parent
LANGUAGES: tuple[str, ...] = ("ar", "en")
RTL_LANGUAGES = {"ar"}


@lru_cache(maxsize=32)
def _read_json(path: str, mtime: float) -> dict[str, Any]:  # mtime busts the cache
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def load_json(name: str) -> dict[str, Any]:
    path = CONTENT_DIR / name
    return _read_json(str(path), path.stat().st_mtime)


def site() -> dict[str, Any]:
    return load_json("site.json")


def projects() -> list[dict[str, Any]]:
    return load_json("projects.json")["projects"]


def learning_ideas() -> list[dict[str, Any]]:
    return load_json("learning_ideas.json")["ideas"]


def experience() -> dict[str, Any]:
    return load_json("experience.json")


def credentials() -> dict[str, Any]:
    return load_json("credentials.json")


def normalize_lang(lang: str | None) -> str:
    if lang in LANGUAGES:
        return lang  # type: ignore[return-value]
    return site().get("default_language", "ar")


def copy(lang: str) -> dict[str, Any]:
    """Return the text for one language, with the site name merged in."""
    lang = normalize_lang(lang)
    data = dict(load_json(f"{lang}.json"))
    data["name"] = site()["name"][lang]
    return data


def all_copy() -> dict[str, dict[str, Any]]:
    return {lang: copy(lang) for lang in LANGUAGES}
